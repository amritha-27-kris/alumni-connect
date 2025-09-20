from flask import Blueprint, jsonify, request
import mysql.connector
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
