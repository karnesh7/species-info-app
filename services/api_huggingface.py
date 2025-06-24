# To use locally cached model:

from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import io
import os

# Cache directory to avoid redownloading on every run
CACHE_DIR = "./models/hf_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

# Global placeholders (will load once when used)
general_processor = None
general_model = None
bird_processor = None
bird_model = None

def load_models():
    global general_processor, general_model, bird_processor, bird_model

    if general_processor is None:
        print("[INFO] Loading general model...")
        general_processor = AutoImageProcessor.from_pretrained("google/vit-base-patch16-224", cache_dir=CACHE_DIR)
        general_model = AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224", cache_dir=CACHE_DIR)

    if bird_processor is None:
        print("[INFO] Loading bird model...")
        bird_processor = AutoImageProcessor.from_pretrained("chriamue/bird-species-classifier", cache_dir=CACHE_DIR)
        bird_model = AutoModelForImageClassification.from_pretrained("chriamue/bird-species-classifier", cache_dir=CACHE_DIR)

def classify_general(image_bytes):
    load_models()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = general_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = general_model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits[0], dim=-1)

    labels = general_model.config.id2label
    results = [
        {"label": labels[i], "score": float(p)}
        for i, p in enumerate(probs)
    ]
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10]

def classify_bird(image_bytes):
    load_models()
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    inputs = bird_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = bird_model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits[0], dim=-1)

    labels = bird_model.config.id2label
    results = [
        {"label": labels[i], "score": float(p)}
        for i, p in enumerate(probs)
    ]
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:10]


# To use API:
'''
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
    headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "image/jpeg"}
    response = requests.post(url, headers=headers, data=image_bytes)
    response.raise_for_status()
    return response.json()
'''