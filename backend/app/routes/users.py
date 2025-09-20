from flask import Blueprint, jsonify, request
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from config import DB_CONFIG

users_bp = Blueprint("users", __name__)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@users_bp.route("/", methods=["GET"])
def get_users():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(users)

@users_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user:
        return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "message": "Invalid email"}), 401

@users_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")  # Default to student if not specified
    skills = data.get("skills", "")

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Name, email, and password are required"}), 400

    # Hash the password
    password_hash = generate_password_hash(password)

    db = get_db_connection()
    cursor = db.cursor()
    
    try:
        # Check if user already exists
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return jsonify({"success": False, "message": "User with this email already exists"}), 409
        
        # Insert new user
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role, skills) VALUES (%s, %s, %s, %s, %s)",
            (name, email, password_hash, role, skills)
        )
        db.commit()
        
        return jsonify({"success": True, "message": "User registered successfully"})
        
    except mysql.connector.Error as err:
        return jsonify({"success": False, "message": f"Database error: {str(err)}"}), 500
    finally:
        cursor.close()
        db.close()

@users_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required"}), 400

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user and check_password_hash(user['password_hash'], password):
        # Remove password_hash from response for security
        user_data = {k: v for k, v in user.items() if k != 'password_hash'}
        return jsonify({"success": True, "user": user_data})
    
    return jsonify({"success": False, "message": "Invalid email or password"}), 401
