from flask import Blueprint, jsonify, request
import mysql.connector
from config import DB_CONFIG

opportunities_bp = Blueprint("opportunities", __name__)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@opportunities_bp.route("/", methods=["GET"])
def get_opportunities():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM opportunities")
    opps = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(opps)

@opportunities_bp.route("/", methods=["POST"])
def add_opportunity():
    data = request.json
    title = data.get("title")
    opp_type = data.get("type")
    description = data.get("description")
    posted_by = data.get("posted_by")

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO opportunities (title, type, description, posted_by) VALUES (%s, %s, %s, %s)",
        (title, opp_type, description, posted_by)
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"message": "Opportunity added successfully"})


