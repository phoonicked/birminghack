import cv2
import os
import torch
import numpy as np
from facenet_pytorch import InceptionResnetV1, MTCNN
from PIL import Image

# Load FaceNet model (pretrained on VGGFace2 dataset)
model = InceptionResnetV1(pretrained="vggface2").eval()

# Initialize MTCNN for face detection
mtcnn = MTCNN(image_size=160, margin=20, keep_all=True)

# Directory to store face images
FACE_DATABASE = "face_database"
os.makedirs(FACE_DATABASE, exist_ok=True)

def extract_face_embedding(image_path):
    """Extracts a 512-dim embedding from an image."""
    img = Image.open(image_path).convert("RGB")
    faces = mtcnn(img)  # Detect face(s)
    
    if faces is None or len(faces) == 0:
        return None
    
    # Take the first detected face
    face = faces[0].unsqueeze(0)  

    # Generate FaceNet embedding
    with torch.no_grad():
        embedding = model(face)
    
    return embedding

def cosine_similarity(emb1, emb2):
    """Computes cosine similarity between two embeddings."""
    emb1 = emb1 / emb1.norm()
    emb2 = emb2 / emb2.norm()
    return torch.dot(emb1.squeeze(), emb2.squeeze()).item()

def is_new_face(face_embedding, threshold=0.6):
    """Compares a face embedding against stored faces to check for duplicates."""
    for existing_face in os.listdir(FACE_DATABASE):
        existing_path = os.path.join(FACE_DATABASE, existing_face)
        existing_embedding = extract_face_embedding(existing_path)
        
        if existing_embedding is not None:
            similarity = cosine_similarity(face_embedding, existing_embedding)
            print(f"Comparing with {existing_face}: Similarity = {similarity:.4f}")

            if similarity > threshold:
                return False  # Face already exists

    return True  # Face is new

def capture_and_store_face(frame):
    """Captures the current frame, detects a face, and stores it if it's new."""
    image_path = "captured_face.jpg"
    cv2.imwrite(image_path, frame)

    # Process the captured image
    face_embedding = extract_face_embedding(image_path)
    if face_embedding is None:
        print("No face detected. Try again.")
        return

    # Check if the face already exists
    if is_new_face(face_embedding):
        face_id = len(os.listdir(FACE_DATABASE)) + 1
        new_face_path = os.path.join(FACE_DATABASE, f"face_{face_id}.jpg")
        os.rename(image_path, new_face_path)
        print(f"✅ New face stored as {new_face_path}")
    else:
        print("❌ Face already exists. Not adding to database.")
        os.remove(image_path)

def run_face_detection():
    """Opens the webcam and continuously detects faces, drawing rectangles around them."""
    cap = cv2.VideoCapture(0)  # Open webcam

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image.")
            break

        # Convert frame to RGB format for MTCNN
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, _ = mtcnn.detect(rgb_frame)

        # Draw rectangles around detected faces
        if boxes is not None:
            for box in boxes:
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Show the live webcam feed
        cv2.imshow("Press SPACE to Capture | ESC to Exit", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACE key to capture
            print("Capturing image...")
            capture_and_store_face(frame)  # Process the face but keep running
        elif key == 27:  # ESC key to exit
            print("Exiting...")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_face_detection()
