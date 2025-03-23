import sys
import os
import cv2
import numpy as np
import requests
import base64
import time
import threading
from urllib.parse import urlparse
import firebase_admin
from firebase_admin import credentials, firestore
from openvino.runtime import Core

from services.llm_client import call_llm_get_name_desc_endpoint

last_detected_doc_id = None

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

try:
    from systemFlow import main_flow
except ImportError as e:
    print("Error importing main_flow:", e)
    main_flow = None

try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(os.path.join(parent_dir, "backend/brumhack.json"))
    firebase_admin.initialize_app(cred)
db = firestore.client()

def upload_to_imagebb(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    url = "https://api.imgbb.com/1/upload"
    payload = {"key": "adf49cd5eb7ee8c50f38ebb785fc49d4", "image": encoded_string}
    response = requests.post(url, payload)
    if response.status_code == 200:
        return response.json().get("data", {}).get("url")
    else:
        print("Failed to upload:", response.text)
        return None

def add_contact_to_firestore(doc_id, name, image_url, description, isContact=False):
    doc_ref = db.collection("Contacts").document(doc_id)
    doc_ref.set({
        "name": name,
        "image": image_url,
        "description": description,
        "isContact": isContact
    })
    print(f"Added to Firestore: {doc_id} -> {name}, {image_url}")

ie = Core()
base_dir = os.path.dirname(__file__)
face_det_model_xml = os.path.join(base_dir, "intel/face-detection-adas-0001/FP32/face-detection-adas-0001.xml")
face_det_net = ie.read_model(face_det_model_xml)
face_det_compiled = ie.compile_model(face_det_net, "CPU")
face_det_output_layer = face_det_compiled.outputs[0]

reid_model_xml = os.path.join(base_dir, "models/intel/face-reidentification-retail-0095/FP32/face-reidentification-retail-0095.xml")
reid_net = ie.read_model(reid_model_xml)
reid_compiled = ie.compile_model(reid_net, "CPU")
reid_output_layer = reid_compiled.outputs[0]

def extract_face_embedding(face_image):
    img_resized = cv2.resize(face_image, (128, 128)).transpose(2, 0, 1)[None, :]
    embedding = reid_compiled([img_resized.astype(np.float32)])[reid_output_layer]
    return embedding

def cosine_similarity(emb1, emb2):
    emb1 = emb1.flatten() / np.linalg.norm(emb1)
    emb2 = emb2.flatten() / np.linalg.norm(emb2)
    return np.dot(emb1, emb2).item()

def load_db_faces():
    contacts_ref = db.collection("Contacts")
    docs = contacts_ref.get()
    db_faces = {}
    for doc in docs:
        data = doc.to_dict()
        image_url = data.get("image")
        if image_url:
            resp = requests.get(image_url)
            image = cv2.imdecode(np.frombuffer(resp.content, np.uint8), cv2.IMREAD_COLOR)
            emb = extract_face_embedding(image)
            db_faces[doc.id] = {"name": data.get("name"), "embedding": emb}
    return db_faces

final_instructions = None
def main_flow_wrapper(known_contact, contact_name, stop_event):
    global final_instructions
    final_instructions = main_flow(known_contact, contact_name, stop_event)

def main():
    global final_instructions

    temp_detected_face_info = None
    doorbell_flow_called = False
    doorbell_thread = None
    last_face_time = time.time()
    doorbell_stop_event = threading.Event()

    db_faces = load_db_faces()
    cap = cv2.VideoCapture(0)
    FACE_DATABASE = "face_database"
    os.makedirs(FACE_DATABASE, exist_ok=True)
    face_counter = len(os.listdir(FACE_DATABASE))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        input_image = np.expand_dims(cv2.resize(frame, (672, 384)).transpose(2, 0, 1), axis=0).astype(np.float32)
        results = face_det_compiled([input_image])[face_det_output_layer]

        face_detected_this_frame = False

        for detection in results[0][0]:
            if detection[2] > 0.8:
                face_detected_this_frame = True
                xmin, ymin, xmax, ymax = (detection[3:] * np.array([w, h, w, h])).astype(int)
                face_cropped = frame[ymin:ymax, xmin:xmax]

# Skip empty or invalid faces
                if face_cropped.size == 0 or face_cropped.shape[0] == 0 or face_cropped.shape[1] == 0:
                    continue

                face_embedding = extract_face_embedding(face_cropped)

                known_contact = False
                best_match_name = None
                for doc_id, info in db_faces.items():
                    if cosine_similarity(face_embedding, info["embedding"]) > 0.15:
                        known_contact = True
                        best_match_name = info["name"]

                if not known_contact and temp_detected_face_info is None:
                    face_counter += 1
                    new_id = f"face_{face_counter}.jpg"
                    filename = os.path.join(FACE_DATABASE, new_id)
                    time.sleep(2)
                    cv2.imwrite(filename, face_cropped)
                    temp_detected_face_info = {"local_image_path": filename, "embedding": face_embedding, "doc_id": new_id.replace(".jpg", "")}

                if main_flow and not doorbell_flow_called:
                    doorbell_thread = threading.Thread(target=main_flow_wrapper, args=(known_contact, best_match_name, doorbell_stop_event))
                    doorbell_thread.start()
                    doorbell_flow_called = True

                last_face_time = time.time()

        if doorbell_flow_called and (time.time() - last_face_time > 5):
            doorbell_stop_event.set()
            doorbell_thread.join()

            if temp_detected_face_info:
                image_url = upload_to_imagebb(temp_detected_face_info["local_image_path"])
                llm_response = call_llm_get_name_desc_endpoint(final_instructions)
                add_contact_to_firestore(temp_detected_face_info["doc_id"], llm_response['name'], image_url, llm_response['description'])
                temp_detected_face_info = None
                db_faces = load_db_faces()

            doorbell_flow_called = False
            doorbell_stop_event.clear()

        cv2.imshow("Feed", frame)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
