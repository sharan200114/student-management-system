import os

from datetime import timedelta
from dotenv import load_dotenv

from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from flask import Flask, jsonify, request
from flask_cors import CORS
from mysql.connector import Error, IntegrityError

from database import get_db_connection

load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

if not app.config["JWT_SECRET_KEY"]:
    raise RuntimeError("JWT_SECRET_KEY is missing from .env")

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)

bcrypt = Bcrypt(app)

jwt = JWTManager(app)

# Allow requests from our frontend development server
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5500",
            "http://127.0.0.1:5500"
        ]
    }
})


# ==========================================
# ADMIN LOGIN API
# ==========================================

@app.route("/api/auth/login", methods=["POST"])
def admin_login():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return response("Invalid JSON request.", status=400)

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return response("Email and password are required.", status=400)

    email = email.strip().lower()

    if not email or not password or len(email) > 150 or len(password) > 128:
        return response("Invalid email or password.", status=400)

    connection = get_db_connection()

    if not connection:
        return response("Database connection failed.", status=503)

    try:

        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, full_name, email, password_hash
            FROM admins
            WHERE email = %s
        """, (email,))

        admin = cursor.fetchone()

        cursor.close()

        if not admin or not bcrypt.check_password_hash(
            admin["password_hash"], password
        ):
            return response("Invalid email or password.", status=401)

        access_token = create_access_token(
            identity=str(admin["id"])
        )

        return response(
            "Login successful.",
            {
                "access_token": access_token,
                "admin": {
                    "id": admin["id"],
                    "full_name": admin["full_name"],
                    "email": admin["email"]
                }
            }
        )

    except Error:
        app.logger.exception("Login database error")
        return response("Unable to process login.", status=500)

    finally:
        connection.close()

# Standard JSON response
def response(message, data=None, status=200):
    return jsonify({
        "success": status < 400,
        "message": message,
        "data": data
    }), status


# Validate student input
def validate_student(data):

    if not isinstance(data, dict):
        return None, "Request must contain a JSON object."

    required_fields = [
        "full_name",
        "email",
        "gender",
        "course"
    ]

    for field in required_fields:
        if not isinstance(data.get(field), str) or not data[field].strip():
            return None, f"{field} is required."

    student = {
        "full_name": data["full_name"].strip(),
        "email": data["email"].strip().lower(),
        "phone": data.get("phone", "").strip()
            if isinstance(data.get("phone", ""), str) else "",
        "gender": data["gender"].strip(),
        "course": data["course"].strip()
    }

    if len(student["full_name"]) > 150:
        return None, "Full name must not exceed 150 characters."

    if len(student["email"]) > 150 or "@" not in student["email"]:
        return None, "Enter a valid email address."

    if len(student["phone"]) > 20:
        return None, "Phone number must not exceed 20 characters."

    if student["gender"] not in ["Male", "Female", "Other"]:
        return None, "Invalid gender."

    if len(student["course"]) > 100:
        return None, "Course must not exceed 100 characters."

    return student, None


# API Home
@app.route("/api", methods=["GET"])
def api_home():
    return response("Student Management API is running.")


# GET: Retrieve all students
@app.route("/api/students", methods=["GET"])
@jwt_required()
def get_students():

    connection = get_db_connection()

    if not connection:
        return response("Database connection failed.", status=503)

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, full_name, email, phone,
                   gender, course, created_at
            FROM students
            ORDER BY id DESC
        """)

        students = cursor.fetchall()

        cursor.close()

        return response(
            "Students retrieved successfully.",
            students
        )

    except Error:
        app.logger.exception("Could not retrieve students")
        return response("Unable to retrieve students.", status=500)

    finally:
        connection.close()


# GET: Retrieve one student
@app.route("/api/students/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student(student_id):

    connection = get_db_connection()

    if not connection:
        return response("Database connection failed.", status=503)

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, full_name, email, phone,
                   gender, course, created_at
            FROM students
            WHERE id = %s
        """, (student_id,))

        student = cursor.fetchone()

        cursor.close()

        if not student:
            return response("Student not found.", status=404)

        return response("Student retrieved successfully.", student)

    except Error:
        app.logger.exception("Could not retrieve student")
        return response("Unable to retrieve student.", status=500)

    finally:
        connection.close()


# POST: Create a new student
@app.route("/api/students", methods=["POST"])
@jwt_required()
def create_student():

    data = request.get_json(silent=True)

    student, error = validate_student(data)

    if error:
        return response(error, status=400)

    connection = get_db_connection()

    if not connection:
        return response("Database connection failed.", status=503)

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO students
            (full_name, email, phone, gender, course)
            VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            student["full_name"],
            student["email"],
            student["phone"],
            student["gender"],
            student["course"]
        )

        cursor.execute(query, values)
        connection.commit()

        new_id = cursor.lastrowid

        cursor.close()

        return response(
            "Student created successfully.",
            {"id": new_id},
            201
        )

    except IntegrityError:
        connection.rollback()
        return response("This email is already registered.", status=409)

    except Error:
        connection.rollback()
        app.logger.exception("Could not create student")
        return response("Unable to create student.", status=500)

    finally:
        connection.close()


# PUT: Update an existing student
@app.route("/api/students/<int:student_id>", methods=["PUT"])
@jwt_required()
def update_student(student_id):

    data = request.get_json(silent=True)

    student, error = validate_student(data)

    if error:
        return response(error, status=400)

    connection = get_db_connection()

    if not connection:
        return response("Database connection failed.", status=503)

    try:
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE students
            SET full_name = %s,
                email = %s,
                phone = %s,
                gender = %s,
                course = %s
            WHERE id = %s
        """, (
            student["full_name"],
            student["email"],
            student["phone"],
            student["gender"],
            student["course"],
            student_id
        ))

        if cursor.rowcount == 0:
            cursor.execute(
                "SELECT id FROM students WHERE id = %s",
                (student_id,)
            )

            exists = cursor.fetchone()

            cursor.close()

            if not exists:
                return response("Student not found.", status=404)

            connection.commit()
            return response("Student information is already up to date.")

        connection.commit()
        cursor.close()

        return response("Student updated successfully.")

    except IntegrityError:
        connection.rollback()
        return response("This email is already registered.", status=409)

    except Error:
        connection.rollback()
        app.logger.exception("Could not update student")
        return response("Unable to update student.", status=500)

    finally:
        connection.close()


# DELETE: Delete a student
@app.route("/api/students/<int:student_id>", methods=["DELETE"])
@jwt_required()
def delete_student(student_id):

    connection = get_db_connection()

    if not connection:
        return response("Database connection failed.", status=503)

    try:
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM students WHERE id = %s",
            (student_id,)
        )

        deleted = cursor.rowcount

        connection.commit()
        cursor.close()

        if deleted == 0:
            return response("Student not found.", status=404)

        return response("Student deleted successfully.")

    except Error:
        connection.rollback()
        app.logger.exception("Could not delete student")
        return response("Unable to delete student.", status=500)

    finally:
        connection.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
