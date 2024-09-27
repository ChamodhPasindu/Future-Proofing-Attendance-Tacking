import os
import cv2
import numpy as np
from flask import Flask, request, jsonify
from deepface import DeepFace
import mediapipe as mp

app = Flask(__name__)

# Path to store registered users' images
REGISTERED_USERS_DIR = "backend/images"

# Ensure directory exists
if not os.path.exists(REGISTERED_USERS_DIR):
    os.makedirs(REGISTERED_USERS_DIR)

# Mediapipe face detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection()

# Register a customer by saving their image
@app.route('/register', methods=['POST'])
def register_customer():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    customer_name = request.form.get('name')

    if not customer_name:
        return jsonify({"error": "Customer name is required"}), 400

    # Save the image in the registered_users directory
    save_path = os.path.join(REGISTERED_USERS_DIR, f"{customer_name}.jpg")
    file.save(save_path)
    
    return jsonify({"message": f"Customer {customer_name} registered successfully!", "file_path": save_path}), 200

# Recognize the customer by comparing the captured image with registered images
@app.route('/recognize', methods=['POST'])
def recognize_customer():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400
    
    file = request.files['image']
    
    # Load the image using OpenCV
    image_np = np.fromstring(file.read(), np.uint8)
    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    
    # Use Mediapipe to detect the face
    results = face_detection.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    if not results.detections:
        return jsonify({"error": "No face detected"}), 400

    # Compare the uploaded face with all registered images
    registered_images = os.listdir(REGISTERED_USERS_DIR)
    for reg_image in registered_images:
        reg_img_path = os.path.join(REGISTERED_USERS_DIR, reg_image)
        try:
            # Use DeepFace for facial recognition
            result = DeepFace.verify(img, reg_img_path, model_name='VGG-Face', enforce_detection=False)
            if result['verified']:
                return jsonify({"message": f"Customer recognized: {reg_image.split('.')[0]}"})
        except Exception as e:
            continue

    return jsonify({"error": "No match found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
