import sys
import cv2
from app.services.embedding import FaceEmbedding
from app.services.recognition import FaceRecognition

MODEL_PATH = "models/embeddings.pkl"

if len(sys.argv) < 2:
    print("Usage: python -m app.services.detect <image_path>")
    exit()

image_path = sys.argv[1]

fr = FaceRecognition(model_path=MODEL_PATH)
fe = FaceEmbedding()

img = cv2.imread(image_path)
if img is None:
    print(f"Không thể đọc ảnh: {image_path}")
    exit()

embedding = fe.get_embedding(img)
if embedding is not None:
    label, distance = fr.predict(embedding)
    print(f"Detected: {label} (distance={distance:.4f})")
else:
    print("No face detected")
