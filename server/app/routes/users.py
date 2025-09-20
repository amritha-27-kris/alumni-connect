from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.database import execute_query
from app.utils.auth import jwt_required_custom
import json

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile', methods=['GET'])
@jwt_required_custom
def get_profile():
    try:
        user = request.current_user
        
        # Get detailed profile information
        profile = execute_query("""
            SELECT user_id, email, first_name, last_name, role, graduation_year,
                   degree, major, current_company, current_position, location, bio,
                   skills, linkedin_url, github_url, portfolio_url, profile_image,
                   is_verified, created_at, updated_at
            FROM users WHERE user_id = %s
        """, (user['user_id'],), fetch_one=True)
        
        if profile['skills']:
            profile['skills'] = json.loads(profile['skills'])
        
        # Get user statistics
        stats = {}
        
        if user['role'] == 'alumni':
            # Get alumni stats
            opportunities_count = execute_query(
                "SELECT COUNT(*) as count FROM opportunities WHERE posted_by = %s",
                (user['user_id'],), fetch_one=True
            )['count']
            
            scholarships_count = execute_query(
                "SELECT COUNT(*) as count FROM scholarships WHERE posted_by = %s",
                (user['user_id'],), fetch_one=True
            )['count']
            
            mentorship_count = execute_query(
                "SELECT COUNT(*) as count FROM mentorship_programs WHERE mentor_id = %s",
                (user['user_id'],), fetch_one=True
            )['count']
            
            stats = {
                'opportunities_posted': opportunities_count,
                'scholarships_posted': scholarships_count,
                'mentorship_programs': mentorship_count
            }
            
        elif user['role'] == 'student':
            # Get student stats
            applications_count = execute_query(
                "SELECT COUNT(*) as count FROM applications WHERE user_id = %s",
                (user['user_id'],), fetch_one=True
            )['count']
            
            mentorship_sessions = execute_query(
                "SELECT COUNT(*) as count FROM mentorship_sessions WHERE mentee_id = %s",
                (user['user_id'],), fetch_one=True
            )['count']
            
            stats = {
                'applications_submitted': applications_count,
                'mentorship_sessions': mentorship_sessions
            }
        
        profile['stats'] = stats
        
        return jsonify({'profile': profile}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get profile', 'details': str(e)}), 500

@users_bp.route('/profile', methods=['PUT'])
@jwt_required_custom
def update_profile():
    try:
        user = request.current_user
        data = request.get_json()
        
        # Fields that can be updated
        updatable_fields = [
            'first_name', 'last_name', 'graduation_year', 'degree', 'major',
            'current_company', 'current_position', 'location', 'bio',
            'linkedin_url', 'github_url', 'portfolio_url'
        ]
        
        update_data = {}
        for field in updatable_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Handle skills separately (JSON field)
        if 'skills' in data:
            update_data['skills'] = json.dumps(data['skills'])
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Build update query
        set_clause = ', '.join([f"{field} = %s" for field in update_data.keys()])
        values = list(update_data.values()) + [user['user_id']]
        
        execute_query(
            f"UPDATE users SET {set_clause} WHERE user_id = %s",
            values
        )
        
        return jsonify({'message': 'Profile updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update profile', 'details': str(e)}), 500

@users_bp.route('/alumni', methods=['GET'])
def get_alumni():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '')
        company = request.args.get('company', '')
        
        offset = (page - 1) * limit
        
        # Build query conditions
        conditions = ["role = 'alumni'", "is_active = TRUE"]
        params = []
        
        if search:
            conditions.append("(first_name LIKE %s OR last_name LIKE %s OR current_company LIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        if company:
            conditions.append("current_company LIKE %s")
            params.append(f"%{company}%")
        
        where_clause = " AND ".join(conditions)
        
        # Get alumni list
        alumni = execute_query(f"""
            SELECT user_id, first_name, last_name, current_company, current_position,
                   location, bio, skills, linkedin_url, graduation_year, degree, major,
                   is_verified, profile_image
            FROM users 
            WHERE {where_clause}
            ORDER BY is_verified DESC, first_name ASC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        # Parse skills for each alumni
        for alum in alumni:
            if alum['skills']:
                alum['skills'] = json.loads(alum['skills'])
        
        # Get total count
        total = execute_query(f"""
            SELECT COUNT(*) as count FROM users WHERE {where_clause}
        """, params, fetch_one=True)['count']
        
        return jsonify({
            'alumni': alumni,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get alumni', 'details': str(e)}), 500

@users_bp.route('/students', methods=['GET'])
def get_students():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '')
        major = request.args.get('major', '')
        
        offset = (page - 1) * limit
        
        # Build query conditions
        conditions = ["role = 'student'", "is_active = TRUE"]
        params = []
        
        if search:
            conditions.append("(first_name LIKE %s OR last_name LIKE %s OR major LIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        if major:
            conditions.append("major LIKE %s")
            params.append(f"%{major}%")
        
        where_clause = " AND ".join(conditions)
        
        # Get students list
        students = execute_query(f"""
            SELECT user_id, first_name, last_name, graduation_year, degree, major,
                   location, bio, skills, linkedin_url, profile_image
            FROM users 
            WHERE {where_clause}
            ORDER BY graduation_year DESC, first_name ASC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        # Parse skills for each student
        for student in students:
            if student['skills']:
                student['skills'] = json.loads(student['skills'])
        
        # Get total count
        total = execute_query(f"""
            SELECT COUNT(*) as count FROM users WHERE {where_clause}
        """, params, fetch_one=True)['count']
        
        return jsonify({
            'students': students,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get students', 'details': str(e)}), 500

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        user = execute_query("""
            SELECT user_id, first_name, last_name, role, graduation_year, degree, major,
                   current_company, current_position, location, bio, skills, linkedin_url,
                   github_url, portfolio_url, profile_image, is_verified
            FROM users 
            WHERE user_id = %s AND is_active = TRUE
        """, (user_id,), fetch_one=True)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if user['skills']:
            user['skills'] = json.loads(user['skills'])
        
        return jsonify({'user': user}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user', 'details': str(e)}), 500