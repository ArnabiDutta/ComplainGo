import os
import numpy as np
from PIL import Image, ImageOps
import tflite_runtime.interpreter as tflite
from huggingface_hub import InferenceClient
import streamlit as st  # <--- 1. IMPORT STREAMLIT

# --- Paths to Model and Labels ---
# Using relative paths is best for deployment
MODEL_PATH = "model.tflite"
LABELS_PATH = "labels.txt"

# --- Get the Secret API Key using st.secrets ---
# This is the "Streamlit way" and will work both locally and when deployed.
try:
    HF_TOKEN = st.secrets["HUGGING_FACE_API_KEY"] # <--- 2. GET THE SECRET
except (AttributeError, KeyError):
    # This is a fallback for if you run the script outside of Streamlit
    # or forget to set the secret.
    HF_TOKEN = "" 

# --- Initialize Hugging Face Client ---
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)


def classify_image(image_data):
    # ... (This function is already perfect and needs NO changes) ...
    np.set_printoptions(suppress=True)
    try:
        interpreter = tflite.Interpreter(model_path=MODEL_PATH)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        with open(LABELS_PATH, 'r') as f:
            class_names = [line.strip().split(' ', 1)[1] for line in f if line.strip()]
    except Exception as e:
        print(f"ERROR: Could not load model or labels. Details: {e}")
        return "Model/Label Error", 0.0
    try:
        image = Image.open(image_data).convert('RGB')
        height = input_details[0]['shape'][1]
        width = input_details[0]['shape'][2]
        image = ImageOps.fit(image, (width, height), Image.Resampling.LANCZOS)
        image_array = np.asarray(image)
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1
        input_data = np.expand_dims(normalized_image_array, axis=0)
        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        output_data = interpreter.get_tensor(output_details[0]['index'])[0]
        index = int(np.argmax(output_data))
        class_name = class_names[index]
        confidence_score = float(output_data[index])
        return class_name, confidence_score
    except Exception as e:
        print(f"ERROR: Image prediction failed. Details: {e}")
        return "Prediction Error", 0.0


def generate_complaint_text(category):
    """
    (This function is already perfect and needs NO changes)
    """
    if not HF_TOKEN:
        print("WARNING: Hugging Face API key not found. Returning template response.")
        return f"This is a formal complaint regarding a '{category}' that requires immediate attention."

    messages = [
        {"role": "system", "content": "You are an AI assistant writing a formal, concise, and clear complaint for a Public Works Department (PWD) in India. The tone must be serious and urgent. Respond only with the complaint text itself, nothing else."},
        {"role": "user", "content": f"Based on examples, write a complaint for the category: {category}"}
    ]
    try:
        response = client.chat_completion(messages=messages, max_tokens=100)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"ERROR: Hugging Face generation failed. Details: {e}")
        return f"This is a formal complaint regarding a '{category}' issue."
