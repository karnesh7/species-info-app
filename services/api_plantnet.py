import requests
from dotenv import load_dotenv
import os
import streamlit as st

PLANTNET_API_KEY = st.secrets["PLANTNET_API_KEY"]

def identify_plant(image_bytes):
    if not PLANTNET_API_KEY:
        raise ValueError("Pl@ntNet API key not found in environment variables.")

    files = {
        'organs': (None, 'auto'),  # or 'leaf', 'flower', etc.
        'images': ('image.jpg', image_bytes, 'image/jpeg'),
    }

    # Change 'weurope' to your intended project
    project = "all"
    url = f"https://my-api.plantnet.org/v2/identify/all?include-related-images=true&no-reject=false&nb-results=10&lang=en&api-key={PLANTNET_API_KEY}"
    response = requests.post(url, files=files)
    response.raise_for_status()
    return response.json()
