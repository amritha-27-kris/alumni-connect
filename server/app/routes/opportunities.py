from flask import Blueprint, request, jsonify
from app.models.database import execute_query
from app.utils.auth import jwt_required_custom, role_required
from datetime import datetime

opportunities_bp = Blueprint('opportunities', __name__)

@opportunities_bp.route('', methods=['GET'])
def get_opportunities():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        opportunity_type = request.args.get('type', '')
        company = request.args.get('company', '')
        location = request.args.get('location', '')
        search = request.args.get('search', '')
        
        offset = (page - 1) * limit
        
        # Build query conditions
        conditions = ["o.is_active = TRUE"]
        params = []
        
        if opportunity_type:
            conditions.append("o.type = %s")
            params.append(opportunity_type)
        
        if company:
            conditions.append("o.company LIKE %s")
            params.append(f"%{company}%")
        
        if location:
            conditions.append("o.location LIKE %s")
            params.append(f"%{location}%")
        
        if search:
            conditions.append("(o.title LIKE %s OR o.description LIKE %s OR o.company LIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        where_clause = " AND ".join(conditions)
        
        # Get opportunities with poster information
        opportunities = execute_query(f"""
            SELECT o.opportunity_id, o.title, o.company, o.type, o.description,
                   o.requirements, o.location, o.salary_range, o.application_deadline,
                   o.created_at, o.updated_at,
                   u.first_name, u.last_name, u.current_position, u.profile_image
            FROM opportunities o
            JOIN users u ON o.posted_by = u.user_id
            WHERE {where_clause}
            ORDER BY o.created_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        # Get total count
        total = execute_query(f"""
            SELECT COUNT(*) as count 
            FROM opportunities o
            JOIN users u ON o.posted_by = u.user_id
            WHERE {where_clause}
        """, params, fetch_one=True)['count']
        
        return jsonify({
            'opportunities': opportunities,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get opportunities', 'details': str(e)}), 500

@opportunities_bp.route('', methods=['POST'])
@jwt_required_custom
@role_required('alumni', 'mentor')
def create_opportunity():
    try:
        user = request.current_user
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'company', 'type', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate opportunity type
        if data['type'] not in ['job', 'internship']:
            return jsonify({'error': 'Type must be either "job" or "internship"'}), 400
        
        # Parse application deadline
        application_deadline = None
        if data.get('application_deadline'):
            try:
                application_deadline = datetime.strptime(data['application_deadline'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Create opportunity
        opportunity_id = execute_query("""
            INSERT INTO opportunities (
                title, company, type, description, requirements, location,
                salary_range, application_deadline, posted_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['title'], data['company'], data['type'], data['description'],
            data.get('requirements', ''), data.get('location', ''),
            data.get('salary_range', ''), application_deadline, user['user_id']
        ))
        
        # Get the created opportunity
        opportunity = execute_query("""
            SELECT o.*, u.first_name, u.last_name, u.current_position
            FROM opportunities o
            JOIN users u ON o.posted_by = u.user_id
            WHERE o.opportunity_id = %s
        """, (opportunity_id,), fetch_one=True)
        
        return jsonify({
            'message': 'Opportunity created successfully',
            'opportunity': opportunity
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create opportunity', 'details': str(e)}), 500

@opportunities_bp.route('/<int:opportunity_id>', methods=['GET'])
def get_opportunity(opportunity_id):
    try:
        opportunity = execute_query("""
            SELECT o.*, u.first_name, u.last_name, u.current_position, u.current_company,
                   u.profile_image, u.linkedin_url
            FROM opportunities o
            JOIN users u ON o.posted_by = u.user_id
            WHERE o.opportunity_id = %s AND o.is_active = TRUE
        """, (opportunity_id,), fetch_one=True)
        
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        return jsonify({'opportunity': opportunity}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get opportunity', 'details': str(e)}), 500

@opportunities_bp.route('/<int:opportunity_id>', methods=['PUT'])
@jwt_required_custom
def update_opportunity(opportunity_id):
    try:
        user = request.current_user
        data = request.get_json()
        
        # Check if user owns this opportunity
        opportunity = execute_query(
            "SELECT posted_by FROM opportunities WHERE opportunity_id = %s",
            (opportunity_id,), fetch_one=True
        )
        
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        if opportunity['posted_by'] != user['user_id']:
            return jsonify({'error': 'You can only update your own opportunities'}), 403
        
        # Fields that can be updated
        updatable_fields = [
            'title', 'company', 'type', 'description', 'requirements',
            'location', 'salary_range', 'application_deadline'
        ]
        
        update_data = {}
        for field in updatable_fields:
            if field in data:
                if field == 'application_deadline' and data[field]:
                    try:
                        update_data[field] = datetime.strptime(data[field], '%Y-%m-%d').date()
                    except ValueError:
                        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
                else:
                    update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Build update query
        set_clause = ', '.join([f"{field} = %s" for field in update_data.keys()])
        values = list(update_data.values()) + [opportunity_id]
        
        execute_query(
            f"UPDATE opportunities SET {set_clause} WHERE opportunity_id = %s",
            values
        )
        
        return jsonify({'message': 'Opportunity updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update opportunity', 'details': str(e)}), 500

@opportunities_bp.route('/<int:opportunity_id>', methods=['DELETE'])
@jwt_required_custom
def delete_opportunity(opportunity_id):
    try:
        user = request.current_user
        
        # Check if user owns this opportunity
        opportunity = execute_query(
            "SELECT posted_by FROM opportunities WHERE opportunity_id = %s",
            (opportunity_id,), fetch_one=True
        )
        
        if not opportunity:
            return jsonify({'error': 'Opportunity not found'}), 404
        
        if opportunity['posted_by'] != user['user_id']:
            return jsonify({'error': 'You can only delete your own opportunities'}), 403
        
        # Soft delete by setting is_active to FALSE
        execute_query(
            "UPDATE opportunities SET is_active = FALSE WHERE opportunity_id = %s",
            (opportunity_id,)
        )
        
        return jsonify({'message': 'Opportunity deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to delete opportunity', 'details': str(e)}), 500

@opportunities_bp.route('/my', methods=['GET'])
@jwt_required_custom
@role_required('alumni', 'mentor')
def get_my_opportunities():
    try:
        user = request.current_user
        
        opportunities = execute_query("""
            SELECT o.*, 
                   (SELECT COUNT(*) FROM applications WHERE opportunity_id = o.opportunity_id) as application_count
            FROM opportunities o
            WHERE o.posted_by = %s
            ORDER BY o.created_at DESC
        """, (user['user_id'],))
        
        return jsonify({'opportunities': opportunities}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get your opportunities', 'details': str(e)}), 500