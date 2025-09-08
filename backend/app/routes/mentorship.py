# routes/mentorship.py

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import MentorshipSession

mentorship_bp = Blueprint('mentorship_bp', _name_)

@mentorship_bp.route('/mentorship-sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    sessions = MentorshipSession.query.all()
    return jsonify([
        {
            'id': s.session_id,
            'mentor_id': s.mentor_id,
            'mentee_id': s.mentee_id,
            'topic': s.topic
        } for s in sessions
    ])
