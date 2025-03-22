import cv2
import os
import numpy as np
from openvino.runtime import Core
from collections import deque

# Initialize OpenVINO Core
ie = Core()

# Load OpenVINO Face Detection Model
face_det_model_xml = "intel/face-detection-adas-0001/FP32/face-detection-adas-0001.xml"
face_det_model_bin = face_det_model_xml.replace(".xml", ".bin")
face_det_net = ie.read_model(model=face_det_model_xml, weights=face_det_model_bin)
face_det_compiled = ie.compile_model(face_det_net, "CPU")  # Change to "GPU" if available

# Load OpenVINO Face Re-Identification Model
reid_model_xml = "models/intel/face-reidentification-retail-0095/FP32/face-reidentification-retail-0095.xml"
reid_model_bin = reid_model_xml.replace(".xml", ".bin")
reid_net = ie.read_model(model=reid_model_xml, weights=reid_model_bin)
reid_compiled = ie.compile_model(reid_net, "CPU")  # Change to "GPU" if available

# Get input and output layers
face_det_input_layer = face_det_compiled.input(0)
face_det_output_layer = face_det_compiled.outputs[0]

reid_input_layer = reid_compiled.input(0)
reid_output_layer = reid_compiled.outputs[0]

# Directory to store face images
FACE_DATABASE = "face_database"
os.makedirs(FACE_DATABASE, exist_ok=True)

# Store face embeddings for comparison
stored_faces = []
face_counter = len(os.listdir(FACE_DATABASE))  # Ensure unique filenames

# Face tracking dictionary
tracked_faces = {}  # {face_id: {"embedding": ..., "last_seen": frame_id, "position": (x, y)}}
frame_id = 0  # Track frame number
DISAPPEAR_THRESHOLD = 10  # Number of frames a face can disappear before being considered "new"


def extract_face_embedding(face_image):
    """Extracts a 256-dimension embedding from a face image using OpenVINO's face-reidentification model."""
    img_resized = cv2.resize(face_image, (128, 128))  # Model expects 128x128 input
    img_transposed = img_resized.transpose(2, 0, 1)[None, :]  # Change to NCHW format
    img_input = img_transposed.astype(np.float32)

    # Run face reidentification model
    embedding = reid_compiled([img_input])[reid_output_layer]
    return embedding


def cosine_similarity(emb1, emb2):
    """Computes cosine similarity between two face embeddings."""
    emb1 = emb1.flatten()
    emb2 = emb2.flatten()

    emb1 = emb1 / np.linalg.norm(emb1)
    emb2 = emb2 / np.linalg.norm(emb2)

    return np.dot(emb1, emb2).item()  # Compute cosine similarity


def match_face(face_embedding, position, threshold=0.3):
    """Finds the best match for a face in the tracked faces dictionary."""
    best_match = None
    best_similarity = -1

    for face_id, data in tracked_faces.items():
        similarity = cosine_similarity(face_embedding, data["embedding"])
        dist = np.linalg.norm(np.array(position) - np.array(data["position"]))

        if similarity > threshold and dist < 50:  # Threshold & position check
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = face_id

    return best_match


# Open webcam for real-time face detection
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1  # Increment frame count
    h, w = frame.shape[:2]
    frame_resized = cv2.resize(frame, (672, 384))  # Resize for faster detection
    input_image = np.expand_dims(frame_resized.transpose(2, 0, 1), axis=0).astype(np.float32)

    # Run face detection
    results = face_det_compiled([input_image])[face_det_output_layer]

    detected_faces = []
    current_embeddings = []

    for detection in results[0][0]:
        confidence = detection[2]
        if confidence > 0.8:  # Confidence threshold
            xmin, ymin, xmax, ymax = (detection[3:] * np.array([w, h, w, h])).astype(int)
            xmin, ymin, xmax, ymax = max(0, xmin), max(0, ymin), min(w, xmax), min(h, ymax)

            detected_faces.append((xmin, ymin, xmax, ymax))
            face_cropped = frame[ymin:ymax, xmin:xmax]

            if face_cropped.size == 0:
                continue

            # Extract embedding
            face_embedding = extract_face_embedding(face_cropped)

            # Match with existing faces
            face_position = ((xmin + xmax) // 2, (ymin + ymax) // 2)
            match_id = match_face(face_embedding, face_position)

            if match_id:
                # Update existing face tracking
                tracked_faces[match_id]["last_seen"] = frame_id
                tracked_faces[match_id]["position"] = face_position
                print(f"✅ Face {match_id} is still in view.")
            else:
                # Assign a new ID
                face_counter += 1
                new_id = face_counter
                tracked_faces[new_id] = {
                    "embedding": face_embedding,
                    "last_seen": frame_id,
                    "position": face_position,
                }
                filename = f"{FACE_DATABASE}/face_{face_counter}.jpg"
                cv2.imwrite(filename, face_cropped)
                print(f"🆕 New face detected and stored as ID {new_id}: {filename}")

            # Draw rectangle around detected faces
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(frame, f"Face {match_id if match_id else new_id}", (xmin, ymin - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Remove faces that haven't been seen in DISAPPEAR_THRESHOLD frames
    disappeared_faces = [face_id for face_id, data in tracked_faces.items() if frame_id - data["last_seen"] > DISAPPEAR_THRESHOLD]
    for face_id in disappeared_faces:
        print(f"❌ Face {face_id} lost tracking.")
        del tracked_faces[face_id]

    # Display webcam feed
    cv2.imshow("Face Detection (ESC to Exit)", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
