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
