import os
import cv2
import numpy as np
from flask import Flask, request, jsonify
from deepface import DeepFace
import mediapipe as mp
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
from datetime import datetime, time
from flask import jsonify
import logging

app = Flask(__name__)

# Replace with your MongoDB URI
client = MongoClient('mongodb://127.0.0.1:27017')
db = client['store']
employees_collection = db['employees']
attendance_collection = db['attendances']

# Path to store registered users' images
REGISTERED_USERS_DIR = "backend/images"

# Ensure directory exists
if not os.path.exists(REGISTERED_USERS_DIR):
    os.makedirs(REGISTERED_USERS_DIR)

# Mediapipe face detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection()

# Helper function to create a common response structure
def create_response(code, message, data=None):
    return {
        "code": code,
        "message": message,
        "data": data if data is not None else {}
    }

def mark_attendance(employee):
    try:
        current_datetime = datetime.now()  # Use full datetime instead of just date
        current_time = current_datetime.time()

        # Fetch the attendance record for today
        attendance_record = attendance_collection.find_one({
            "employee": employee["_id"],
            "date": {"$gte": datetime.combine(current_datetime.date(), time(0, 0)), 
                     "$lt": datetime.combine(current_datetime.date(), time(23, 59))}
        })

        if not attendance_record:
            # First time marking, set check-in time
            check_in_time = current_datetime
            status = "late" if current_time > time(8, 0) else "present"

            attendance_data = {
                "employee": employee["_id"],
                "date": current_datetime,  # Store as full datetime
                "status": status,
                "checkInTime": check_in_time,
            }

            # Insert the new attendance record
            attendance_collection.insert_one(attendance_data)

            return f"Attendance marked with status: {status}"

        else:
            # If the record exists, update check-out time
            check_out_time = current_datetime

            # If check-out is after 5:00 PM and status is not already late, mark as present
            if attendance_record["status"] == "present" and current_time > time(17, 0):
                attendance_collection.update_one(
                    {"_id": attendance_record["_id"]},
                    {"$set": {"checkOutTime": check_out_time}}
                )
                return "Check-out time updated"
            else:
                attendance_collection.update_one(
                    {"_id": attendance_record["_id"]},
                    {"$set": {"checkOutTime": check_out_time}}
                )
                return "Check-out time updated, status remains late"

    except Exception as e:
        logging.error(f"Error in mark_attendance: {str(e)}")
        return None
    

# Register a customer by saving their image
@app.route('/register', methods=['POST'])
def register_customer():
    if 'image' not in request.files:
        return jsonify(create_response(400, "No image uploaded")), 400
    
    file = request.files['image']
    customer_tag = request.form.get('tag')

    if not customer_tag:
        return jsonify(create_response(400, "Customer name is required")), 400

    # Save the image in the registered_users directory
    save_path = os.path.join(REGISTERED_USERS_DIR, f"{customer_tag}.jpg")
    file.save(save_path)
    
    return jsonify(create_response(200, f"Customer {customer_tag} registered successfully!", {"file_path": save_path})), 200


# Recognize the customer by comparing the captured image with registered images and fetch their record from the database
@app.route('/recognize', methods=['POST'])
def recognize_customer():
    if 'image' not in request.files:
        return jsonify(create_response(400, "No image uploaded")), 400
    
    file = request.files['image']
    
    # Load the image using OpenCV
    image_np = np.fromstring(file.read(), np.uint8)
    img = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    
    # Use Mediapipe to detect the face
    results = face_detection.process(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    if not results.detections:
        return jsonify(create_response(400, "No face detected")), 400

    # Compare the uploaded face with all registered images (named by employee tag)
    registered_images = os.listdir(REGISTERED_USERS_DIR)
    for reg_image in registered_images:
        reg_img_path = os.path.join(REGISTERED_USERS_DIR, reg_image)
        try:
            # Use DeepFace for facial recognition
            result = DeepFace.verify(img, reg_img_path, model_name='VGG-Face', enforce_detection=False)
            if result['verified']:
                employee_tag = reg_image.split('.')[0]  # Extract employee tag from the image filename
                
                # Fetch the employee record from MongoDB using the employee tag
                employee = employees_collection.find_one({"tag": employee_tag})
                
                if employee:
                    employee_data = {
                        "name": employee.get("name"),
                        "email": employee.get("email"),
                        "designation": employee.get("designation"),
                        "department": employee.get("department"),
                        "tag": employee.get("tag"),
                    }

                    # Mark attendance
                    attendance_message = mark_attendance(employee)
                    if attendance_message:
                        return jsonify(create_response(200, "Customer recognized", employee_data)), 200
                    else:
                        # If attendance marking fails, return recognition without attendance update
                        return jsonify(create_response(500, "Customer recognized but attendance marking failed", employee_data)), 500

                else:
                    return jsonify(create_response(404, "Employee not found in the database")), 404
        
        except Exception as e:
            logging.error(f"Error in recognition process: {str(e)}")
            continue

    return jsonify(create_response(404, "No match found")), 404


# Get all employees
@app.route('/employees', methods=['GET'])
def get_all_employees():
    try:
        employees = list(employees_collection.find())

        if len(employees) == 0:
            return jsonify(create_response(404, "No employees found")), 404

        employee_list = []
        for employee in employees:
            employee_data = {
                "name": employee.get("name"),
                "email": employee.get("email"),
                "designation": employee.get("designation"),
                "department": employee.get("department"),
                "tag": employee.get("tag"),
            }
            employee_list.append(employee_data)

        return jsonify(create_response(200, "Employees retrieved successfully", employee_list)), 200

    except Exception as e:
        print("Error fetching employees:", str(e))
        return jsonify(create_response(500, "Internal Server Error")), 500

if __name__ == '__main__':
    app.run(debug=True)

