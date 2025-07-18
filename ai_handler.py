import os
import numpy as np
from PIL import Image, ImageOps
import tflite_runtime.interpreter as tflite
import google.generativeai as genai  # <-- CHANGE #1: Import Google's library
import streamlit as st                 # <-- CHANGE #2: Import Streamlit to use st.secrets

# --- Paths to Model and Labels ---
MODEL_PATH = "model.tflite"
LABELS_PATH = "labels.txt"

# --- Configure the Google AI Client using st.secrets ---
# This is the "Streamlit way" that works both locally and deployed.
try:
    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"] # <-- CHANGE #3: Get the Google key
    genai.configure(api_key=GOOGLE_API_KEY)
except (AttributeError, KeyError):
    # This is a fallback in case the secret isn't set.
    print("WARNING: GOOGLE_API_KEY secret not found.")
    GOOGLE_API_KEY = None


def classify_image(image_data):
    """
    (This function is perfect and does not need any changes)
    """
    np.set_printoptions(suppress=True)
    try:
        interpreter = tflite.Interpreter(model_path=MODEL_PATH)
        interpreter.allocate_tensors()
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        with open(LABELS_PATH, 'r') as f:
            class_names = [line.strip().split(' ', 1)[1] for line in f if line.strip()]
    except Exception as e:
        return f"Model/Label Error: {e}", 0.0
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
        return f"Prediction Error: {e}", 0.0


def generate_complaint_text(category): # <-- CHANGE #4: No longer need to pass the token
    """
    Generate complaint text using the reliable Google Gemini API.
    """
    if not GOOGLE_API_KEY:
        print("WARNING: Google API Key not available. Returning template.")
        return f"This is a formal complaint regarding a '{category}' issue that requires immediate attention."

    try:
        # Initialize the specific Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash-latest')
        
        # Simple, direct prompt for Gemini
        prompt = f"""You are an AI assistant writing a formal, concise, and clear complaint for a Public Works Department (PWD) in India. The tone must be serious and urgent. Respond only with the complaint text itself, nothing else.

Based on the examples below, write the complaint for the final category.

Example 1:
Category: Water Logging
Complaint: There is significant water accumulation on the road, making it impassable for pedestrians and disrupting traffic flow. Urgent action is needed to clear the water and fix the underlying drainage issue.

Example 2:
Category: Broken Streetlight
Complaint: The streetlight at this location is non-functional, creating a dark and unsafe area at night. Immediate repair is requested to ensure public safety.

Category: {category}
Complaint:"""
        
        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print(f"ERROR: Google Gemini API failed. Details: {e}")
        return f"This is a formal complaint regarding a '{category}' issue."
