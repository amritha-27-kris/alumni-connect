

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import Story

stories_bp = Blueprint('stories_bp', _name_)

@stories_bp.route('/stories', methods=['GET'])
@jwt_required()
def get_stories():
    stories = Story.query.all()
    return jsonify([
        {
            'id': s.story_id,
            'user_id': s.user_id,
            'title': s.title,
            'content': s.content
        } for s in stories
    ])
