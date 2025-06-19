import requests
from dotenv import load_dotenv
import os

load_dotenv()

PLANTNET_API_KEY = os.getenv("PLANTNET_API_KEY")

def identify_plant(image_bytes):
    if not PLANTNET_API_KEY:
        raise ValueError("Pl@ntNet API key not found in environment variables.")

    files = {
        'organs': (None, 'auto'),
        'images': ('image.jpg', image_bytes, 'image/jpeg'),
    }

    url = f"https://my.plantnet.org/v2/identify/all?api-key={PLANTNET_API_KEY}"
    response = requests.post(url, files=files)
    response.raise_for_status()
    return response.json()
