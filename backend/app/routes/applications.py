

from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from models import Application

app_bp = Blueprint('app_bp', _name_)

@app_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_applications():
    applications = Application.query.all()
    return jsonify([
        {
            'id': a.app_id,
            'opp_id': a.opp_id,
            'user_id': a.user_id,
            'status': a.status
        } for a in applications
    ])
