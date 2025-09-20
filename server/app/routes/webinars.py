from flask import Blueprint, request, jsonify
from app.models.database import execute_query
from app.utils.auth import jwt_required_custom, role_required
from datetime import datetime

webinars_bp = Blueprint('webinars', __name__)

@webinars_bp.route('', methods=['GET'])
def get_webinars():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        upcoming_only = request.args.get('upcoming_only', 'false').lower() == 'true'
        search = request.args.get('search', '')
        
        offset = (page - 1) * limit
        
        # Build query conditions
        conditions = ["w.is_active = TRUE"]
        params = []
        
        if upcoming_only:
            conditions.append("w.scheduled_date >= NOW()")
        
        if search:
            conditions.append("(w.title LIKE %s OR w.description LIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        where_clause = " AND ".join(conditions)
        
        # Get webinars with host information
        webinars = execute_query(f"""
            SELECT w.webinar_id, w.title, w.description, w.scheduled_date,
                   w.duration_minutes, w.max_participants, w.registration_required,
                   w.created_at,
                   u.first_name, u.last_name, u.current_position, u.current_company,
                   u.profile_image,
                   (SELECT COUNT(*) FROM webinar_registrations wr WHERE wr.webinar_id = w.webinar_id) as registered_count
            FROM webinars w
            JOIN users u ON w.host_id = u.user_id
            WHERE {where_clause}
            ORDER BY w.scheduled_date ASC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        # Get total count
        total = execute_query(f"""
            SELECT COUNT(*) as count 
            FROM webinars w
            JOIN users u ON w.host_id = u.user_id
            WHERE {where_clause}
        """, params, fetch_one=True)['count']
        
        return jsonify({
            'webinars': webinars,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get webinars', 'details': str(e)}), 500

@webinars_bp.route('', methods=['POST'])
@jwt_required_custom
@role_required('alumni', 'mentor')
def create_webinar():
    try:
        user = request.current_user
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'scheduled_date']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Parse scheduled date
        try:
            scheduled_date = datetime.strptime(data['scheduled_date'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}), 400
        
        # Validate numeric fields
        duration_minutes = data.get('duration_minutes', 90)
        max_participants = data.get('max_participants', 100)
        
        try:
            duration_minutes = int(duration_minutes)
            max_participants = int(max_participants)
            if duration_minutes < 1 or max_participants < 1:
                raise ValueError()
        except ValueError:
            return jsonify({'error': 'duration_minutes and max_participants must be positive integers'}), 400
        
        # Create webinar
        webinar_id = execute_query("""
            INSERT INTO webinars (
                title, description, host_id, scheduled_date, duration_minutes,
                max_participants, meeting_link, registration_required
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data['title'], data['description'], user['user_id'], scheduled_date,
            duration_minutes, max_participants, data.get('meeting_link', ''),
            data.get('registration_required', True)
        ))
        
        # Get the created webinar
        webinar = execute_query("""
            SELECT w.*, u.first_name, u.last_name, u.current_position
            FROM webinars w
            JOIN users u ON w.host_id = u.user_id
            WHERE w.webinar_id = %s
        """, (webinar_id,), fetch_one=True)
        
        return jsonify({
            'message': 'Webinar created successfully',
            'webinar': webinar
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create webinar', 'details': str(e)}), 500

@webinars_bp.route('/<int:webinar_id>', methods=['GET'])
def get_webinar(webinar_id):
    try:
        webinar = execute_query("""
            SELECT w.*, u.first_name, u.last_name, u.current_position, u.current_company,
                   u.profile_image, u.linkedin_url,
                   (SELECT COUNT(*) FROM webinar_registrations wr WHERE wr.webinar_id = w.webinar_id) as registered_count
            FROM webinars w
            JOIN users u ON w.host_id = u.user_id
            WHERE w.webinar_id = %s AND w.is_active = TRUE
        """, (webinar_id,), fetch_one=True)
        
        if not webinar:
            return jsonify({'error': 'Webinar not found'}), 404
        
        return jsonify({'webinar': webinar}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get webinar', 'details': str(e)}), 500

@webinars_bp.route('/<int:webinar_id>/register', methods=['POST'])
@jwt_required_custom
def register_for_webinar(webinar_id):
    try:
        user = request.current_user
        
        # Check if webinar exists and is active
        webinar = execute_query("""
            SELECT webinar_id, max_participants, registration_required, scheduled_date,
                   (SELECT COUNT(*) FROM webinar_registrations WHERE webinar_id = %s) as registered_count
            FROM webinars 
            WHERE webinar_id = %s AND is_active = TRUE
        """, (webinar_id, webinar_id), fetch_one=True)
        
        if not webinar:
            return jsonify({'error': 'Webinar not found'}), 404
        
        if not webinar['registration_required']:
            return jsonify({'error': 'This webinar does not require registration'}), 400
        
        # Check if webinar is in the future
        if webinar['scheduled_date'] <= datetime.now():
            return jsonify({'error': 'Cannot register for past webinars'}), 400
        
        # Check if there's space
        if webinar['registered_count'] >= webinar['max_participants']:
            return jsonify({'error': 'Webinar is full'}), 400
        
        # Check if already registered
        existing_registration = execute_query(
            "SELECT registration_id FROM webinar_registrations WHERE webinar_id = %s AND user_id = %s",
            (webinar_id, user['user_id']), fetch_one=True
        )
        
        if existing_registration:
            return jsonify({'error': 'You are already registered for this webinar'}), 409
        
        # Register user
        execute_query(
            "INSERT INTO webinar_registrations (webinar_id, user_id) VALUES (%s, %s)",
            (webinar_id, user['user_id'])
        )
        
        return jsonify({'message': 'Successfully registered for webinar'}), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to register for webinar', 'details': str(e)}), 500

@webinars_bp.route('/<int:webinar_id>/unregister', methods=['DELETE'])
@jwt_required_custom
def unregister_from_webinar(webinar_id):
    try:
        user = request.current_user
        
        # Check if registration exists
        registration = execute_query(
            "SELECT registration_id FROM webinar_registrations WHERE webinar_id = %s AND user_id = %s",
            (webinar_id, user['user_id']), fetch_one=True
        )
        
        if not registration:
            return jsonify({'error': 'You are not registered for this webinar'}), 404
        
        # Remove registration
        execute_query(
            "DELETE FROM webinar_registrations WHERE webinar_id = %s AND user_id = %s",
            (webinar_id, user['user_id'])
        )
        
        return jsonify({'message': 'Successfully unregistered from webinar'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to unregister from webinar', 'details': str(e)}), 500

@webinars_bp.route('/my-registrations', methods=['GET'])
@jwt_required_custom
def get_my_registrations():
    try:
        user = request.current_user
        
        registrations = execute_query("""
            SELECT w.webinar_id, w.title, w.description, w.scheduled_date,
                   w.duration_minutes, w.meeting_link,
                   u.first_name, u.last_name, u.current_position,
                   wr.registered_at, wr.attended
            FROM webinar_registrations wr
            JOIN webinars w ON wr.webinar_id = w.webinar_id
            JOIN users u ON w.host_id = u.user_id
            WHERE wr.user_id = %s AND w.is_active = TRUE
            ORDER BY w.scheduled_date ASC
        """, (user['user_id'],))
        
        return jsonify({'registrations': registrations}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get your registrations', 'details': str(e)}), 500

@webinars_bp.route('/my-webinars', methods=['GET'])
@jwt_required_custom
@role_required('alumni', 'mentor')
def get_my_webinars():
    try:
        user = request.current_user
        
        webinars = execute_query("""
            SELECT w.*, 
                   (SELECT COUNT(*) FROM webinar_registrations wr WHERE wr.webinar_id = w.webinar_id) as registered_count
            FROM webinars w
            WHERE w.host_id = %s
            ORDER BY w.scheduled_date DESC
        """, (user['user_id'],))
        
        return jsonify({'webinars': webinars}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get your webinars', 'details': str(e)}), 500