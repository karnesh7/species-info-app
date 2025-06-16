import requests
from io import BytesIO
from PIL import Image
import os

API_URL = "https://router.huggingface.co/hf-inference/models/chriamue/bird-species-classifier"
API_TOKEN = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "image/jpeg"  # or "image/png" if your image is png
}

def classify_image(image_bytes):
    response = requests.post(API_URL, headers=headers, data=image_bytes)
    response.raise_for_status()
    return response.json()