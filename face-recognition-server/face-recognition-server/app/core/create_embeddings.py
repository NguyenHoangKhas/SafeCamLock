import os
import cv2
import numpy as np
import pickle
import shutil
from app.services.embedding import FaceEmbedding
from app.services.recognition import FaceRecognition

MODEL_PATH = "models/embeddings.pkl"
INVALID_FOLDER = "invalid"

def load_images_from_folder(folder):
    images = []
    labels = []
    file_paths = []
    for label in os.listdir(folder):
        person_folder = os.path.join(folder, label)
        if not os.path.isdir(person_folder):
            continue
        for filename in os.listdir(person_folder):
            img_path = os.path.join(person_folder, filename)
            img = cv2.imread(img_path)
            if img is None:
                print(f"⚠ Không thể đọc ảnh: {img_path}")
                continue
            images.append(img)
            labels.append(label)  
            file_paths.append(img_path)
    return images, labels, file_paths

def main():
    data_folder = "data"
    images, labels, file_paths = load_images_from_folder(data_folder)

    embedding_extractor = FaceEmbedding()
    face_recognition = FaceRecognition(model_path=MODEL_PATH)

    valid_embeddings = []
    valid_labels = []

    for img, label, path in zip(images, labels, file_paths):
        emb = embedding_extractor.get_embedding(img)
        if emb is not None:
            valid_embeddings.append(emb)
            valid_labels.append(label)
        else:
            print(f"⚠ Không tìm thấy khuôn mặt trong ảnh {path}, di chuyển sang '{INVALID_FOLDER}'")
            os.makedirs(INVALID_FOLDER, exist_ok=True)
            shutil.move(path, os.path.join(INVALID_FOLDER, os.path.basename(path)))

    if not valid_embeddings:
        print("❌ Không có dữ liệu hợp lệ để train.")
        return

    face_recognition.embeddings = valid_embeddings
    face_recognition.labels = valid_labels
    face_recognition.train(n_neighbors=3)

    os.makedirs("models", exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump((face_recognition.knn, face_recognition.labels), f)

    print(f"✅ Đã lưu embeddings vào {MODEL_PATH}")

if __name__ == "__main__":
    main()
