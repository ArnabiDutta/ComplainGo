import os
import numpy as np
from PIL import Image, ImageOps
from dotenv import load_dotenv
# import tensorflow.keras  # <--- 1. DELETE THIS LINE. It's for the old .h5 model.
import tflite_runtime.interpreter as tflite # <--- 2. ADD THIS LINE. This is for .tflite models.
from huggingface_hub import InferenceClient

# --- Load Environment Variables ---
load_dotenv()
HF_TOKEN = os.getenv("HUGGING_FACE_API_KEY")

# --- Paths to Model and Labels ---
# MODEL_PATH = "/home/glow/Documents/ComplainGo/tm-my-image-model/model.h5" # <--- 3. DELETE THIS LINE.
# Let's define the correct .tflite model path
TFLITE_MODEL_PATH = "/home/glow/Documents/ComplainGo/model.tflite" # <--- 4. ADD THIS LINE.
LABELS_PATH = "/home/glow/Documents/ComplainGo/labels.txt"

# --- Initialize Hugging Face Client ---
MODEL_ID = "mistralai/Mistral-7B-Instruct-v0.2"
client = InferenceClient(model=MODEL_ID, token=HF_TOKEN)


def classify_image(image_data):
    """
    Classify the image using TensorFlow Lite model (.tflite).
    Returns: (predicted class, confidence score)
    """
    # import tensorflow as tf # <--- 5. DELETE THIS LINE. It's not needed with tflite-runtime.

    try:
        # Load the TFLite model from the correct path variable
        interpreter = tflite.Interpreter(model_path=TFLITE_MODEL_PATH) # <--- 6. CHANGE THIS LINE to use the correct variable.
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
    except Exception as e:
        print(f"ERROR: Could not load TFLite model. Details: {e}")
        return "Model Error", 0.0

    try:
        with open(LABELS_PATH, 'r') as f:
            class_names = [line.strip().split(' ', 1)[1] for line in f if line.strip()]
    except Exception as e:
        print(f"ERROR: Could not read labels from {LABELS_PATH}. Details: {e}")
        return "Label Error", 0.0

    try:
        image = Image.open(image_data).convert('RGB')
        
        # Get the input size from the model details for accuracy
        height = input_details[0]['shape'][1]
        width = input_details[0]['shape'][2]
        
        image = ImageOps.fit(image, (width, height), Image.Resampling.LANCZOS)
        
        image_array = np.asarray(image)
        # Teachable machine models are often normalized to [-1, 1]
        normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1 # <--- 7. Correct normalization.
        
        input_data = np.expand_dims(normalized_image_array, axis=0)

        interpreter.set_tensor(input_details[0]['index'], input_data)
        interpreter.invoke()
        
        # Get the raw output tensor
        output_data = interpreter.get_tensor(output_details[0]['index'])[0] 
        
        # Apply softmax to get probabilities if the model output isn't already
        # Some models output raw logits, some output probabilities. This makes it robust.
        # exp_scores = np.exp(output_data - np.max(output_data))
        # probabilities = exp_scores / np.sum(exp_scores)
        # For Teachable Machine, direct output is usually fine.
        
        probabilities = output_data

        index = int(np.argmax(probabilities))
        class_name = class_names[index]
        confidence_score = float(probabilities[index])

        return class_name, confidence_score

    except Exception as e:
        print(f"ERROR: Image preprocessing or prediction failed. Details: {e}")
        return "Prediction Error", 0.0


# ... (all the imports and the classify_image function remain exactly the same) ...


def generate_complaint_text(category):
    """
    NEW VERSION using Hugging Face's "chat_completion" for Instruct models.
    """
    if not HF_TOKEN or "YOUR_KEY" in HF_TOKEN:
        print("WARNING: Hugging Face API key not set. Returning template response.")
        return f"This is a formal complaint regarding a '{category}' that requires immediate attention."

    # --- We format the prompt as a series of "messages" for a chat model ---
    messages = [
        {
            "role": "system",
            "content": "You are an AI assistant writing a formal, concise, and clear complaint for a Public Works Department (PWD) in India. The tone must be serious and urgent. Respond only with the complaint text itself, nothing else."
        },
        {
            "role": "user",
            "content": """Here are some examples of how to write:

Example 1:
Category: Water Logging
Complaint: There is significant water accumulation on the road, making it impassable for pedestrians and disrupting traffic flow. Urgent action is needed to clear the water and fix the underlying drainage issue.

Example 2:
Category: Broken Streetlight
Complaint: The streetlight at this location is non-functional, creating a dark and unsafe area at night. Immediate repair is requested to ensure public safety.

Now, based on these examples, write the complaint for the following category.
Category: """ + category
        }
    ]

    try:
        # --- Use the correct method: chat_completion ---
        response = client.chat_completion(
            messages=messages,
            max_tokens=100,
            temperature=0.7,
            top_p=0.95,
            # The other parameters like repetition_penalty are not used in chat_completion
        )
        
        # The response object is different for chat models
        # We need to access the content of the assistant's message
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"ERROR: Hugging Face generation failed. Details: {e}")
        return f"This is a formal complaint regarding a '{category}' issue that requires immediate attention."
