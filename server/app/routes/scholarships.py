from flask import Blueprint, request, jsonify
from app.models.database import execute_query
from app.utils.auth import jwt_required_custom, role_required
from datetime import datetime

scholarships_bp = Blueprint('scholarships', __name__)

@scholarships_bp.route('', methods=['GET'])
def get_scholarships():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '')
        organization = request.args.get('organization', '')
        min_amount = request.args.get('min_amount', '')
        
        offset = (page - 1) * limit
        
        # Build query conditions
        conditions = ["s.is_active = TRUE", "s.application_deadline >= CURDATE()"]
        params = []
        
        if search:
            conditions.append("(s.title LIKE %s OR s.description LIKE %s OR s.organization LIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        if organization:
            conditions.append("s.organization LIKE %s")
            params.append(f"%{organization}%")
        
        if min_amount:
            try:
                min_amount_val = float(min_amount)
                conditions.append("s.amount >= %s")
                params.append(min_amount_val)
            except ValueError:
                pass
        
        where_clause = " AND ".join(conditions)
        
        # Get scholarships with poster information
        scholarships = execute_query(f"""
            SELECT s.scholarship_id, s.title, s.organization, s.amount, s.description,
                   s.eligibility_criteria, s.application_deadline, s.application_url,
                   s.created_at, s.updated_at,
                   u.first_name, u.last_name, u.current_position, u.profile_image
            FROM scholarships s
            JOIN users u ON s.posted_by = u.user_id
            WHERE {where_clause}
            ORDER BY s.application_deadline ASC, s.amount DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        # Get total count
        total = execute_query(f"""
            SELECT COUNT(*) as count 
            FROM scholarships s
            JOIN users u ON s.posted_by = u.user_id
            WHERE {where_clause}
        """, params, fetch_one=True)['count']
        
        return jsonify({
            'scholarships': scholarships,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get scholarships', 'details': str(e)}), 500

@scholarships_bp.route('', methods=['POST'])
@jwt_required_custom
@role_required('alumni', 'mentor')
def create_scholarship():
    try:
        user = request.current_user
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'organization', 'description', 'eligibility_criteria', 'application_deadline']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse application deadline
        try:
            application_deadline = datetime.strptime(data['application_deadline'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # Validate amount if provided
        amount = None
        if data.get('amount'):
            try:
                amount = float(data['amount'])
                if amount < 0:
                    return jsonify({'error': 'Amount must be positive'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid amount format'}), 400
        
        # Create scholarship
        scholarship_id = execute_query("""
            INSERT INTO scholarships (
                title, organization, amount, description, eligibility_criteria,
                application_deadline, application_url, posted_by
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['title'], data['organization'], amount, data['description'],
            data['eligibility_criteria'], application_deadline,
            data.get('application_url', ''), user['user_id']
        ))
        
        # Get the created scholarship
        scholarship = execute_query("""
            SELECT s.*, u.first_name, u.last_name, u.current_position
            FROM scholarships s
            JOIN users u ON s.posted_by = u.user_id
            WHERE s.scholarship_id = %s
        """, (scholarship_id,), fetch_one=True)
        
        return jsonify({
            'message': 'Scholarship created successfully',
            'scholarship': scholarship
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create scholarship', 'details': str(e)}), 500

@scholarships_bp.route('/<int:scholarship_id>', methods=['GET'])
def get_scholarship(scholarship_id):
    try:
        scholarship = execute_query("""
            SELECT s.*, u.first_name, u.last_name, u.current_position, u.current_company,
                   u.profile_image, u.linkedin_url
            FROM scholarships s
            JOIN users u ON s.posted_by = u.user_id
            WHERE s.scholarship_id = %s AND s.is_active = TRUE
        """, (scholarship_id,), fetch_one=True)
        
        if not scholarship:
            return jsonify({'error': 'Scholarship not found'}), 404
        
        return jsonify({'scholarship': scholarship}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get scholarship', 'details': str(e)}), 500

@scholarships_bp.route('/eligible', methods=['GET'])
@jwt_required_custom
@role_required('student')
def get_eligible_scholarships():
    try:
        user = request.current_user
        
        # Get user profile for eligibility checking
        user_profile = execute_query("""
            SELECT graduation_year, degree, major, skills
            FROM users WHERE user_id = %s
        """, (user['user_id'],), fetch_one=True)
        
        # For now, return all active scholarships
        # In a real implementation, you would implement complex eligibility logic
        scholarships = execute_query("""
            SELECT s.*, u.first_name, u.last_name, u.current_position,
                   CASE 
                       WHEN a.scholarship_id IS NOT NULL THEN TRUE 
                       ELSE FALSE 
                   END as already_applied
            FROM scholarships s
            JOIN users u ON s.posted_by = u.user_id
            LEFT JOIN applications a ON s.scholarship_id = a.scholarship_id AND a.user_id = %s
            WHERE s.is_active = TRUE AND s.application_deadline >= CURDATE()
            ORDER BY s.application_deadline ASC
        """, (user['user_id'],))
        
        return jsonify({
            'scholarships': scholarships,
            'user_profile': user_profile
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get eligible scholarships', 'details': str(e)}), 500

@scholarships_bp.route('/<int:scholarship_id>', methods=['PUT'])
@jwt_required_custom
def update_scholarship(scholarship_id):
    try:
        user = request.current_user
        data = request.get_json()
        
        # Check if user owns this scholarship
        scholarship = execute_query(
            "SELECT posted_by FROM scholarships WHERE scholarship_id = %s",
            (scholarship_id,), fetch_one=True
        )
        
        if not scholarship:
            return jsonify({'error': 'Scholarship not found'}), 404
        
        if scholarship['posted_by'] != user['user_id']:
            return jsonify({'error': 'You can only update your own scholarships'}), 403
        
        # Fields that can be updated
        updatable_fields = [
            'title', 'organization', 'amount', 'description', 'eligibility_criteria',
            'application_deadline', 'application_url'
        ]
        
        update_data = {}
        for field in updatable_fields:
            if field in data:
                if field == 'application_deadline' and data[field]:
                    try:
                        update_data[field] = datetime.strptime(data[field], '%Y-%m-%d').date()
                    except ValueError:
                        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
                elif field == 'amount' and data[field]:
                    try:
                        amount = float(data[field])
                        if amount < 0:
                            return jsonify({'error': 'Amount must be positive'}), 400
                        update_data[field] = amount
                    except ValueError:
                        return jsonify({'error': 'Invalid amount format'}), 400
                else:
                    update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Build update query
        set_clause = ', '.join([f"{field} = %s" for field in update_data.keys()])
        values = list(update_data.values()) + [scholarship_id]
        
        execute_query(
            f"UPDATE scholarships SET {set_clause} WHERE scholarship_id = %s",
            values
        )
        
        return jsonify({'message': 'Scholarship updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update scholarship', 'details': str(e)}), 500

@scholarships_bp.route('/my', methods=['GET'])
@jwt_required_custom
@role_required('alumni', 'mentor')
def get_my_scholarships():
    try:
        user = request.current_user
        
        scholarships = execute_query("""
            SELECT s.*, 
                   (SELECT COUNT(*) FROM applications WHERE scholarship_id = s.scholarship_id) as application_count
            FROM scholarships s
            WHERE s.posted_by = %s
            ORDER BY s.created_at DESC
        """, (user['user_id'],))
        
        return jsonify({'scholarships': scholarships}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get your scholarships', 'details': str(e)}), 500