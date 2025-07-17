import tensorflow as tf

# Path to your .h5 model
h5_model_path = "model.h5"
tflite_model_path = "model.tflite"

# Load the model
model = tf.keras.models.load_model(h5_model_path)

# Convert to TFLite
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# Save to file
with open(tflite_model_path, 'wb') as f:
    f.write(tflite_model)

print("Conversion successful:", tflite_model_path)

