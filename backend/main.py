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

# 1. Add the parent directory so we can import systemFlow.py
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# 2. Try importing the doorbell conversation function
try:
    from systemFlow import main_flow
except ImportError as e:
    print("Error importing main_flow from systemFlow:", e)
    main_flow = None

######################################
# FIREBASE INITIALIZATION
######################################
try:
    firebase_admin.get_app()
except ValueError:
    cred = credentials.Certificate(os.path.join(parent_dir, "backend/brumhack.json"))
    firebase_admin.initialize_app(cred)
db = firestore.client()

######################################
# IMAGE UPLOAD / FIRESTORE HELPERS
######################################
def upload_to_imagebb(image_path):
    """Uploads an image to ImageBB and returns the URL."""
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

def add_contact_to_firestore(doc_id, name, image_url, description):
    """Adds a new document to Firestore inside the 'Contacts' collection."""
    doc_ref = db.collection("Contacts").document(doc_id)
    doc_ref.set({
        "name": name,
        "image": image_url,
        "description": description
    })
    print(f"Added to Firestore: {doc_id} -> {name}, {image_url}")

######################################
# OPENVINO MODEL LOADING
######################################
ie = Core()

# Use the current (harryfolder) directory as base for the models.
base_dir = os.path.dirname(__file__)

# 1) Face Detection Model
face_det_model_xml = os.path.join(base_dir, "intel", "face-detection-adas-0001", "FP32", "face-detection-adas-0001.xml")
face_det_model_bin = face_det_model_xml.replace(".xml", ".bin")
face_det_net = ie.read_model(model=face_det_model_xml, weights=face_det_model_bin)
face_det_compiled = ie.compile_model(face_det_net, "CPU")
face_det_output_layer = face_det_compiled.outputs[0]

# 2) Face Re-Identification Model
reid_model_xml = os.path.join(base_dir, "models", "intel", "face-reidentification-retail-0095", "FP32", "face-reidentification-retail-0095.xml")
reid_model_bin = reid_model_xml.replace(".xml", ".bin")
reid_net = ie.read_model(model=reid_model_xml, weights=reid_model_bin)
reid_compiled = ie.compile_model(reid_net, "CPU")
reid_output_layer = reid_compiled.outputs[0]

######################################
# EMBEDDING & SIMILARITY
######################################
def extract_face_embedding(face_image):
    """Extracts a 256-dimension embedding from a face image."""
    try:
        img_resized = cv2.resize(face_image, (128, 128))
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None
    img_transposed = img_resized.transpose(2, 0, 1)[None, :]
    img_input = img_transposed.astype(np.float32)
    embedding = reid_compiled([img_input])[reid_output_layer]
    return embedding

def cosine_similarity(emb1, emb2):
    """Computes cosine similarity between two face embeddings."""
    emb1 = emb1.flatten() / np.linalg.norm(emb1)
    emb2 = emb2.flatten() / np.linalg.norm(emb2)
    return np.dot(emb1, emb2).item()

# global container for the result
final_instructions = None

def main_flow_wrapper(known_contact, contact_name, stop_event):
    global final_instructions
    # Call the main_flow function and store its return value
    final_instructions = main_flow(known_contact, contact_name, stop_event)


######################################
# FIRESTORE FACES
######################################
def is_valid_url(url):
    """Checks if the URL has a valid scheme (http or https)."""
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https")

def load_db_faces():
    """
    Fetches all docs from 'Contacts' in Firestore,
    downloads each face image, extracts embedding,
    and returns a dict: {doc_id: {"name": str, "embedding": np.array}}
    """
    contacts_ref = db.collection("Contacts")
    docs = contacts_ref.get()
    db_faces = {}
    for doc in docs:
        doc_id = doc.id
        data = doc.to_dict()
        name = data.get("name")
        image_url = data.get("image")

        if not image_url or not is_valid_url(image_url):
            continue

        try:
            resp = requests.get(image_url)
            if resp.status_code == 200:
                image_data = np.asarray(bytearray(resp.content), dtype=np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
                if image is not None:
                    emb = extract_face_embedding(image)
                    if emb is not None:
                        db_faces[doc_id] = {"name": name, "embedding": emb}
                else:
                    print(f"Failed to decode image for doc {doc_id}")
            else:
                print(f"Failed to download image for doc {doc_id} from {image_url}")
        except Exception as e:
            print(f"Error fetching image for doc {doc_id}: {e}")
    return db_faces

######################################
# DOORBELL FLOW CONTROL (Using a threading.Event)
######################################
doorbell_flow_called = False
doorbell_thread = None
last_face_time = time.time()
doorbell_stop_event = threading.Event()  # We'll pass this into main_flow

def main():
    global doorbell_flow_called, doorbell_thread, last_face_time, final_instructions

    known_contact = False
    contact_name = None

    db_faces = load_db_faces()
    print(f"Loaded {len(db_faces)} faces from Firestore.")

    FACE_DATABASE = "face_database"
    os.makedirs(FACE_DATABASE, exist_ok=True)
    face_counter = len(os.listdir(FACE_DATABASE))

    cap = cv2.VideoCapture(0)
    SIMILARITY_THRESHOLD = 0.15

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w = frame.shape[:2]
        frame_resized = cv2.resize(frame, (672, 384))
        input_image = np.expand_dims(frame_resized.transpose(2, 0, 1), axis=0).astype(np.float32)
        results = face_det_compiled([input_image])[face_det_output_layer]

        for detection in results[0][0]:
            confidence = detection[2]
            if confidence > 0.8:
                xmin, ymin, xmax, ymax = (detection[3:] * np.array([w, h, w, h])).astype(int)
                xmin, ymin, xmax, ymax = max(0, xmin), max(0, ymin), min(w, xmax), min(h, ymax)
                face_cropped = frame[ymin:ymax, xmin:xmax]
                if face_cropped.size == 0:
                    continue

                face_embedding = extract_face_embedding(face_cropped)
                if face_embedding is None:
                    continue

                best_match_id = None
                best_match_name = None
                best_score = -1.0
                for doc_id, info in db_faces.items():
                    db_emb = info["embedding"]
                    score = cosine_similarity(face_embedding, db_emb)
                    if score > SIMILARITY_THRESHOLD and score > best_score:
                        best_score = score
                        best_match_id = doc_id
                        best_match_name = info["name"]

                doc_id = None
                image_url = None

                if best_match_id:
                    display_name = best_match_name
                    known_contact = True
                    contact_name = best_match_name
                else:
                    known_contact = False
                    contact_name = None
                    face_counter += 1
                    new_id = f"face{face_counter}.jpg"
                    filename = os.path.join(FACE_DATABASE, new_id)
                    cv2.imwrite(filename, face_cropped)
                    display_name = new_id

                    image_url = upload_to_imagebb(filename)
                    if image_url:
                        doc_id = new_id.replace(".jpg", "")
                        add_contact_to_firestore(doc_id, new_id, image_url, "")
                        new_emb = extract_face_embedding(face_cropped)
                        if new_emb is not None:
                            db_faces[doc_id] = {"name": new_id, "embedding": new_emb}

                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                cv2.putText(frame, display_name, (xmin, ymin - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # If doorbell conversation hasn't started, start it:
                if main_flow and not doorbell_flow_called:
                    doorbell_thread = threading.Thread(
                        target=main_flow_wrapper,
                        args=(known_contact, contact_name, doorbell_stop_event)
                    )
                    doorbell_thread.start()
                    doorbell_flow_called = True
                    print("Doorbell conversation started.")

                last_face_time = time.time()

        cv2.imshow("Live Feed (Press ESC to exit)", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

        # If no face detected for 5 seconds, stop conversation.
        if doorbell_flow_called and (time.time() - last_face_time > 5):
                doorbell_stop_event.set()
                print("No face detected for 5 seconds. Stopping doorbell conversation.")
                if doorbell_thread is not None:
                    doorbell_thread.join()
                    image_url = upload_to_imagebb(filename)
                    print("Final conversation context:")
                    print(f'hewo {final_instructions}')
                    llm_response = call_llm_get_name_desc_endpoint(final_instructions)
                    name = llm_response['name']
                    desc = llm_response['description']
                    print(f"Name: {name}, Description: {desc}")
                    # Check that doc_id and image_url exist before updating Firestore.
                    if doc_id and image_url:
                        add_contact_to_firestore(doc_id, name, image_url, desc)
                    else:
                        print("No new face was registered, so no contact info to update.")
                doorbell_flow_called = False
                doorbell_stop_event.clear()

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()