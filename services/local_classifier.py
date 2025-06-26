import torch
import numpy as np
from PIL import Image
from io import BytesIO
import torchvision.transforms as transforms

# Load the full PyTorch model
model = torch.load("models/broad_category_classifier_full.pt", map_location="cpu", weights_only=False)
model.eval()

# Category mapping (must match training order)
CATEGORIES = ['Bird', 'Fish', 'Insect', 'Mammal', 'Plant', 'Reptile_Amphibian']

# Define preprocessing like EfficientNet
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),  # Converts to [0, 1] range and (C, H, W)
    transforms.Normalize(mean=[0.485, 0.456, 0.406],  # Imagenet stats
                         std=[0.229, 0.224, 0.225])
])

def predict_category(image_bytes):
    # Load image
    img = Image.open(BytesIO(image_bytes)).convert("RGB")
    img_tensor = preprocess(img).unsqueeze(0)  # Add batch dimension

    with torch.no_grad():
        output = model(img_tensor)
        probs = torch.nn.functional.softmax(output[0], dim=0)

    predicted_index = torch.argmax(probs).item()
    confidence = probs[predicted_index].item()

    return {
        "category": CATEGORIES[predicted_index],
        "confidence": confidence
    }

# Using TFLite model:
'''
import numpy as np
import tensorflow as tf
from PIL import Image
from io import BytesIO

# Load the model only once
interpreter = tf.lite.Interpreter(model_path="models/broad_category_classifier_2.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Category mapping (order must match your training)
CATEGORIES = ['Bird', 'Fish', 'Insect', 'Mammal', 'Plant', 'Reptile_Amphibian']

def predict_category(image_bytes):
    img = Image.open(BytesIO(image_bytes)).resize((224, 224)).convert('RGB')
    img_array = np.array(img).astype(np.float32)
    
    # Preprocess like EfficientNet expects
    img_array = tf.keras.applications.efficientnet.preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)

    interpreter.set_tensor(input_details[0]['index'], img_array)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    predicted_index = np.argmax(output[0])
    confidence = output[0][predicted_index]

    return {
        "category": CATEGORIES[predicted_index],
        "confidence": confidence
    }
'''