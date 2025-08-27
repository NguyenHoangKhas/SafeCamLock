import os
import cv2
import time
import requests
import threading
import numpy as np
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Request
from app.services.embedding import FaceEmbedding
from app.services.recognition import FaceRecognition

router = APIRouter()

# ================= Cấu hình =================
LOGOUT_TIMEOUT = 5  # phút
BACKEND_LOGIN_URL = "http://localhost:3002/api/face-login"   # API login web
BACKEND_LOGOUT_URL = "http://localhost:3002/api/logout"      # API logout web

# ================= Biến toàn cục =================
last_recognition_time = None
LOGIN_USER_ID = None

# ================= Khởi tạo model =================
embedding_extractor = FaceEmbedding()
face_recognition = FaceRecognition(model_path="models/embeddings.pkl")

# ================= Auto logout thread =================
def check_auto_logout():
    global last_recognition_time, LOGIN_USER_ID
    while True:
        if LOGIN_USER_ID and last_recognition_time:
            now = datetime.now()
            if now - last_recognition_time > timedelta(minutes=LOGOUT_TIMEOUT):
                print("⏳ Hết thời gian -> auto logout")
                try:
                    requests.post(BACKEND_LOGOUT_URL, json={"userId": LOGIN_USER_ID}, timeout=5)
                except Exception as e:
                    print("Lỗi logout:", e)
                LOGIN_USER_ID = None
                last_recognition_time = None
        time.sleep(5)  # check mỗi 5s

threading.Thread(target=check_auto_logout, daemon=True).start()

# ================= API nhận diện =================
@router.post("/recognize")
async def recognize_face(request: Request):
    global last_recognition_time, LOGIN_USER_ID

    # 1. Đọc raw bytes từ ESP32
    contents = await request.body()
    np_arr = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail="Invalid image")

    # 2. Lấy embedding
    embedding = embedding_extractor.get_embedding(img)
    if embedding is None:
        raise HTTPException(status_code=404, detail="Face not detected")

    # 3. Nhận diện
    predicted_label, distance = face_recognition.predict(embedding)
    print(f"✅ Predict: {predicted_label}, Distance: {distance:.4f}")

    if predicted_label == "Unknown":
        raise HTTPException(status_code=404, detail="Không nhận diện được người này")

    try:
        LOGIN_USER_ID = predicted_label
    except ValueError:
        raise HTTPException(status_code=500, detail=f"Label không hợp lệ: {predicted_label}")

    last_recognition_time = datetime.now()

    # 5. Gọi backend web login
    try:
        response = requests.post(BACKEND_LOGIN_URL, json={"userId": LOGIN_USER_ID}, timeout=5)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Lỗi kết nối backend: {str(e)}")
