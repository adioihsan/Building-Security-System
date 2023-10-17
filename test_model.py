import cv2
import tensorflow as tf
import matplotlib.pyplot as plt
import numpy as np



# Load the TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()

# Get input and output tensors.
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

print(input_details)

# Assuming img is originally loaded as BGR format (common in OpenCV)
img = cv2.imread("real-1.jpg", -1)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
img = cv2.resize(img, (224, 224))

# Expand dimensions to match the expected input shape [batch_size, height, width, num_channels]
input_data = np.expand_dims(img, axis=0)

# Set the input tensor
interpreter.set_tensor(input_details[0]['index'], input_data)

interpreter.invoke()

# Get the output tensor
output_data = interpreter.get_tensor(output_details[0]['index'])
print(output_data)

