# 🔐 SafeCamLock

An IoT system combining **ESP32-CAM** and an **electromagnetic lock** with **facial recognition** for secure access control.

## 📌 Features
- Live monitoring via **ESP32-CAM**
- **Facial recognition** using a Python (FastAPI + OpenCV/TensorFlow) server
- Remote control of the **electromagnetic lock**
- Real-time access logging and monitoring

## 📂 Project Structure
- `FirmwareCamera/` : Arduino firmware for ESP32-CAM  
- `face-recognition-server/` : Python server for facial recognition  

## 🚀 Setup & Usage

### 1. Flash ESP32-CAM
- Open `FirmwareCamera/FirmwareCamera.ino` in Arduino IDE  
- Select **ESP32-CAM (AI Thinker)** board  
- Upload the firmware  

### 2. Install & Run Face Recognition Server
```bash
cd face-recognition-server
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
