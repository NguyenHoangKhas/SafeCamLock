from fastapi import FastAPI
from app.api.face import router as face_router

app = FastAPI()

app.include_router(face_router)
