import requests
from dotenv import load_dotenv
import os

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

def classify_bird(image_bytes):
    url = "https://router.huggingface.co/hf-inference/models/chriamue/bird-species-classifier"
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "image/jpeg"}
    response = requests.post(url, headers=headers, data=image_bytes)
    response.raise_for_status()
    return response.json()

def classify_general(image_bytes):
    url = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    response = requests.post(url, headers=headers, data=image_bytes)
    response.raise_for_status()
    return response.json()
