from flask import Blueprint, jsonify, request
import mysql.connector
from config import DB_CONFIG

stories_bp = Blueprint("stories", __name__)

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@stories_bp.route("/", methods=["GET"])
def get_stories():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM stories")
    stories = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(stories)

@stories_bp.route("/", methods=["POST"])
def add_story():
    data = request.json
    title = data.get("title")
    content = data.get("content")
    posted_by = data.get("posted_by")

    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO stories (title, content, posted_by) VALUES (%s, %s, %s)",
        (title, content, posted_by)
    )
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"message": "Story posted successfully"})


