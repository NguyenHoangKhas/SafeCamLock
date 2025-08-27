import cv2
import mediapipe as mp
import numpy as np

class FaceEmbedding:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        # Chỉ dùng static_image_mode=True khi xử lý ảnh tĩnh
        self.face_mesh = self.mp_face_mesh.FaceMesh(static_image_mode=True,
                                                    max_num_faces=1,
                                                    refine_landmarks=True,
                                                    min_detection_confidence=0.5)
    
    def get_embedding(self, image):
        """
        image: ảnh đầu vào (numpy array, BGR như cv2.imread)
        return: embedding vector dạng numpy array hoặc None nếu không phát hiện được mặt
        """
        # Chuyển ảnh sang RGB vì mediapipe dùng RGB
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(img_rgb)

        if not results.multi_face_landmarks:
            return None  # Không phát hiện được mặt

        face_landmarks = results.multi_face_landmarks[0]

        # Lấy tất cả điểm landmark (x,y,z)
        landmarks = []
        for lm in face_landmarks.landmark:
            landmarks.append([lm.x, lm.y, lm.z])

        landmarks = np.array(landmarks).flatten()  # Chuyển thành vector 1 chiều

        # Chuẩn hóa vector embedding (tùy chọn)
        norm = np.linalg.norm(landmarks)
        if norm > 0:
            landmarks = landmarks / norm

        return landmarks

# Test nhanh
if __name__ == "__main__":
    embedding_extractor = FaceEmbedding()
    image = cv2.imread("test_face.jpg")  # Thay bằng ảnh của bạn
    embedding = embedding_extractor.get_embedding(image)
    if embedding is not None:
        print("Embedding vector size:", embedding.shape)
    else:
        print("Không tìm thấy khuôn mặt trong ảnh.")
