import numpy as np
from sklearn.neighbors import KNeighborsClassifier
import pickle
import os

class FaceRecognition:
    def __init__(self, model_path="models/embeddings.pkl"):
        self.model_path = model_path
        self.knn = None
        self.labels = []
        self.embeddings = []

        if os.path.exists(self.model_path):
            self.load_model()

    def add_embedding(self, embedding: np.ndarray, label: str):
        self.embeddings.append(embedding)
        self.labels.append(label)

    def train(self, n_neighbors=3):
        if not self.embeddings:
            raise ValueError("Không có embedding để train")

        X = np.array(self.embeddings)
        y = np.array(self.labels)
        self.knn = KNeighborsClassifier(n_neighbors=n_neighbors, metric='euclidean')
        self.knn.fit(X, y)

        with open(self.model_path, 'wb') as f:
            pickle.dump((self.knn, self.labels), f)
        print("Training completed and model saved.")

    def load_model(self):
        with open(self.model_path, 'rb') as f:
            self.knn, self.labels = pickle.load(f)
        print(f"Model loaded from {self.model_path}.")

    def predict(self, embedding: np.ndarray, threshold=0.6):
        if self.knn is None:
            raise ValueError("Model chưa được train hoặc load")

        distances, indices = self.knn.kneighbors([embedding], n_neighbors=1)
        distance = distances[0][0]
        label = self.knn.predict([embedding])[0]

        if distance > threshold:
            return "Unknown", distance
        else:
            return label, distance
