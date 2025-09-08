

from flask import Blueprint, jsonify
from models import Opportunity

opp_bp = Blueprint('opp_bp', _name_)

@opp_bp.route('/opportunities', methods=['GET'])
def get_opportunities():
    opportunities = Opportunity.query.all()
    return jsonify([
        {
            'id': o.opp_id,
            'title': o.title,
            'type': o.type,
            'description': o.description,
            'posted_by': o.posted_by
        } for o in opportunities
    ])
