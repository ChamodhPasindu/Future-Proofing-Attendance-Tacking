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
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
                "checkOutTime":check_in_time
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
                "id": str(employee.get("_id"))
            }
            employee_list.append(employee_data)

        return jsonify(create_response(200, "Employees retrieved successfully", employee_list)), 200

    except Exception as e:
        print("Error fetching employees:", str(e))
        return jsonify(create_response(500, "Internal Server Error")), 500


@app.route('/attendance/today', methods=['GET'])
def get_today_attendance():
    try:
        # Get the current date (without the time component)
        current_date = datetime.now().date()

        # Fetch attendance records for today
        today_attendance = attendance_collection.find({
            "date": {
                "$gte": datetime.combine(current_date, time(0, 0)),
                "$lt": datetime.combine(current_date, time(23, 59))
            }
        })

        # Prepare the list to store attendance data
        attendance_list = []

        # Iterate over each attendance record
        for record in today_attendance:
            # Fetch employee details from the employee collection using the employee ID
            employee = employees_collection.find_one({"_id": ObjectId(record["employee"])})

            if employee:
                # Convert checkInTime and checkOutTime to ISO 8601 format if they exist
                check_in_time = record.get("checkInTime").strftime('%Y-%m-%dT%H:%M:%S') if record.get("checkInTime") else None
                check_out_time = record.get("checkOutTime").strftime('%Y-%m-%dT%H:%M:%S') if record.get("checkOutTime") else None

                attendance_data = {
                    "employee_name": employee.get("name"),
                    "employee_tag": employee.get("tag"),
                    "status": record.get("status"),
                    "checkInTime": check_in_time,
                    "checkOutTime": check_out_time,
                    "notes": record.get("notes", "")
                }
                attendance_list.append(attendance_data)

        # If no attendance records are found for today
        if not attendance_list:
            return jsonify(create_response(404, "No attendance records found for today")), 404

        # Return the attendance list for today
        return jsonify(create_response(200, "Today's attendance fetched successfully", attendance_list)), 200

    except Exception as e:
        logging.error(f"Error fetching today's attendance: {str(e)}")
        return jsonify(create_response(500, "Internal Server Error")), 500


@app.route('/attendance/employees', methods=['GET'])
def get_driver_attendance():
    try:
        # Extract query parameters
        employee_id = request.args.get('employee_id')
        year = int(request.args.get('year'))
        month = int(request.args.get('month'))

        if not employee_id or not year or not month:
            return jsonify({"code": 400, "message": "Missing required parameters"}), 400

        # Define the date range for the specified year and month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        # Query attendance collection
        attendance_records = attendance_collection.find({
            "employee": ObjectId(employee_id),
            "date": {
                "$gte": start_date,
                "$lt": end_date
            }
        })

        # Format the result as a list of dictionaries
        records = []
        for record in attendance_records:
            records.append({
                "checkInTime": record.get("checkInTime").strftime('%Y-%m-%d %H:%M:%S') if record.get("checkInTime") else None,
                "checkOutTime": record.get("checkOutTime").strftime('%Y-%m-%d %H:%M:%S') if record.get("checkOutTime") else None,
                "status": record.get("status"),
                "notes": record.get("notes", ""),
                "date": record.get("date").strftime('%Y-%m-%d'),
            })

        if not records:
            return jsonify({"code": 404, "message": "No records found for the specified employee"}), 404

        # Return the formatted attendance records
        return jsonify({"code": 200, "data": records, "message": "employee attendance fetched successfully"}), 200

    except Exception as e:
        print(f"Error fetching employee attendance: {str(e)}")
        return jsonify({"code": 500, "message": "Internal Server Error"}), 500
    

if __name__ == '__main__':
    app.run(debug=True)