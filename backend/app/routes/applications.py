from flask import Blueprint, jsonify, request
import mysql.connector
from config import DB_CONFIG

applications_bp = Blueprint("applications", __name__)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@applications_bp.route("/", methods=["POST"])
def apply_opportunity():
    data = request.json
    opp_id = data.get("opp_id")
    user_id = data.get("user_id")

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO applications (opp_id, user_id, status) VALUES (%s, %s, %s)",
        (opp_id, user_id, "applied")
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"message": "Application submitted"})



