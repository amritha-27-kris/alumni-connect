from flask import Blueprint, jsonify, request
import mysql.connector
from config import DB_CONFIG

mentorship_bp = Blueprint("mentorship", __name__)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@mentorship_bp.route("/", methods=["GET"])
def get_sessions():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM mentorship_sessions")
    sessions = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(sessions)

@mentorship_bp.route("/", methods=["POST"])
def create_session():
    data = request.json
    mentor_id = data.get("mentor_id")
    mentee_id = data.get("mentee_id")
    topic = data.get("topic")
    scheduled_at = data.get("scheduled_at")

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO mentorship_sessions (mentor_id, mentee_id, topic, scheduled_at) VALUES (%s, %s, %s, %s)",
        (mentor_id, mentee_id, topic, scheduled_at)
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"message": "Mentorship session created"})


