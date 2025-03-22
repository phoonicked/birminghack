import cv2
import os
import numpy as np
from openvino.runtime import Core

# Initialize OpenVINO Core
ie = Core()

# Load OpenVINO Face Detection Model
face_det_model_xml = "intel/face-detection-adas-0001/FP32/face-detection-adas-0001.xml"
face_det_model_bin = face_det_model_xml.replace(".xml", ".bin")
face_det_net = ie.read_model(model=face_det_model_xml, weights=face_det_model_bin)
face_det_compiled = ie.compile_model(face_det_net, "CPU")

# Load OpenVINO Face Re-Identification Model
reid_model_xml = "models/intel/face-reidentification-retail-0095/FP32/face-reidentification-retail-0095.xml"
reid_model_bin = reid_model_xml.replace(".xml", ".bin")
reid_net = ie.read_model(model=reid_model_xml, weights=reid_model_bin)
reid_compiled = ie.compile_model(reid_net, "CPU")

# Get input and output layers
face_det_output_layer = face_det_compiled.outputs[0]
reid_output_layer = reid_compiled.outputs[0]

# Directory for face database
FACE_DATABASE = "face_database"
os.makedirs(FACE_DATABASE, exist_ok=True)

# Load existing face embeddings (images) from the face database.
stored_faces = {}  # {filename: image}
face_counter = len(os.listdir(FACE_DATABASE))
for file in os.listdir(FACE_DATABASE):
    if file.endswith(".jpg"):
        img = cv2.imread(os.path.join(FACE_DATABASE, file))
        stored_faces[file] = img

# Face tracking system: tracks faces currently in view.
tracked_faces = {}  # {face_id: {"embedding": ..., "last_seen": frame_id, "first_seen": frame_id, "position": (x,y), "filename": ...}}
frame_id = 0
DISAPPEAR_THRESHOLD = 120  # Frames to wait before removing a face from tracking
SIMILARITY_THRESHOLD = 0.15
FACE_MERGE_WINDOW = 120  # Time window for merging duplicate faces

def extract_face_embedding(face_image):
    """Extracts a 256-dimension embedding from a face image."""
    img_resized = cv2.resize(face_image, (128, 128))
    img_transposed = img_resized.transpose(2, 0, 1)[None, :]
    img_input = img_transposed.astype(np.float32)
    embedding = reid_compiled([img_input])[reid_output_layer]
    return embedding

def cosine_similarity(emb1, emb2):
    """Computes cosine similarity between two face embeddings."""
    emb1 = emb1.flatten() / np.linalg.norm(emb1)
    emb2 = emb2.flatten() / np.linalg.norm(emb2)
    return np.dot(emb1, emb2).item()

def find_database_match(face_embedding):
    """Searches for a match in the stored face database.
       Returns the filename if a match is found, else None.
    """
    best_match = None
    best_similarity = -1
    for filename, stored_image in stored_faces.items():
        stored_embedding = extract_face_embedding(stored_image)
        similarity = cosine_similarity(face_embedding, stored_embedding)
        if similarity > SIMILARITY_THRESHOLD and similarity > best_similarity:
            best_similarity = similarity
            best_match = filename
    return best_match

def find_best_match(face_embedding, position):
    """Finds the best match in currently tracked faces."""
    best_match = None
    best_similarity = -1
    for face_id, data in tracked_faces.items():
        similarity = cosine_similarity(face_embedding, data["embedding"])
        distance = np.linalg.norm(np.array(position) - np.array(data["position"]))
        if similarity > SIMILARITY_THRESHOLD and distance < 50:
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = face_id
    return best_match

# Open webcam for real-time detection
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1
    h, w = frame.shape[:2]
    frame_resized = cv2.resize(frame, (672, 384))
    input_image = np.expand_dims(frame_resized.transpose(2, 0, 1), axis=0).astype(np.float32)

    # Run face detection
    results = face_det_compiled([input_image])[face_det_output_layer]

    for detection in results[0][0]:
        confidence = detection[2]
        if confidence > 0.8:
            xmin, ymin, xmax, ymax = (detection[3:] * np.array([w, h, w, h])).astype(int)
            xmin, ymin, xmax, ymax = max(0, xmin), max(0, ymin), min(w, xmax), min(h, ymax)
            face_cropped = frame[ymin:ymax, xmin:xmax]
            if face_cropped.size == 0:
                continue

            # Extract embedding and compute face center.
            face_embedding = extract_face_embedding(face_cropped)
            face_position = ((xmin + xmax) // 2, (ymin + ymax) // 2)

            # FIRST: check if the face is already in the database.
            db_match = find_database_match(face_embedding)
            if db_match is not None:
                display_name = db_match
                # Update tracking info for the database face.
                if db_match in tracked_faces:
                    tracked_faces[db_match]["last_seen"] = frame_id
                    tracked_faces[db_match]["position"] = face_position
                else:
                    tracked_faces[db_match] = {
                        "embedding": face_embedding,
                        "last_seen": frame_id,
                        "first_seen": frame_id,
                        "position": face_position,
                        "filename": os.path.join(FACE_DATABASE, db_match)
                    }
                # Check for any short-lived duplicate entries in tracked_faces that are similar.
                for t_face_id in list(tracked_faces.keys()):
                    if t_face_id != db_match:
                        sim = cosine_similarity(face_embedding, tracked_faces[t_face_id]["embedding"])
                        # If similarity is high and the face was only tracked for a short period.
                        if sim > SIMILARITY_THRESHOLD and (frame_id - tracked_faces[t_face_id]["first_seen"]) < DISAPPEAR_THRESHOLD:
                            try:
                                os.remove(tracked_faces[t_face_id]["filename"])
                            except Exception as e:
                                print(f"Error removing file: {e}")
                            del tracked_faces[t_face_id]
                            if t_face_id in stored_faces:
                                del stored_faces[t_face_id]
            else:
                # If not in the database, check tracked faces.
                match_id = find_best_match(face_embedding, face_position)
                if match_id:
                    tracked_faces[match_id]["last_seen"] = frame_id
                    tracked_faces[match_id]["position"] = face_position
                    display_name = match_id
                else:
                    # No match found anywhere: register as a new face.
                    face_counter += 1
                    new_id = f"face{face_counter}.jpg"
                    filename = os.path.join(FACE_DATABASE, new_id)
                    cv2.imwrite(filename, face_cropped)
                    stored_faces[new_id] = face_cropped
                    tracked_faces[new_id] = {
                        "embedding": face_embedding,
                        "last_seen": frame_id,
                        "first_seen": frame_id,
                        "position": face_position,
                        "filename": filename,
                    }
                    display_name = new_id

            # Draw rectangle and label around the detected face.
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(frame, display_name, (xmin, ymin - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Remove faces that disappeared too quickly.
    disappeared_faces = [face_id for face_id, data in tracked_faces.items()
                         if frame_id - data["last_seen"] > DISAPPEAR_THRESHOLD]
    for face_id in disappeared_faces:
        if frame_id - tracked_faces[face_id]["first_seen"] < DISAPPEAR_THRESHOLD:
            try:
                os.remove(tracked_faces[face_id]["filename"])
            except Exception as e:
                print(f"Error removing file: {e}")
        del tracked_faces[face_id]

    # Display webcam feed.
    cv2.imshow("Face Tracking (ESC to Exit)", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        print("Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
