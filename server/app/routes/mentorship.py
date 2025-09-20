from flask import Blueprint, request, jsonify
from app.models.database import execute_query
from app.utils.auth import jwt_required_custom, role_required
from datetime import datetime
import json

mentorship_bp = Blueprint('mentorship', __name__)

@mentorship_bp.route('/programs', methods=['GET'])
def get_mentorship_programs():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        search = request.args.get('search', '')
        expertise = request.args.get('expertise', '')
        
        offset = (page - 1) * limit
        
        # Build query conditions
        conditions = ["mp.is_active = TRUE"]
        params = []
        
        if search:
            conditions.append("(mp.title LIKE %s OR mp.description LIKE %s OR u.first_name LIKE %s OR u.last_name LIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param, search_param])
        
        if expertise:
            conditions.append("mp.expertise_areas LIKE %s")
            params.append(f"%{expertise}%")
        
        where_clause = " AND ".join(conditions)
        
        # Get mentorship programs with mentor information
        programs = execute_query(f"""
            SELECT mp.program_id, mp.title, mp.description, mp.expertise_areas,
                   mp.max_mentees, mp.duration_weeks, mp.created_at,
                   u.user_id as mentor_id, u.first_name, u.last_name, u.current_position,
                   u.current_company, u.profile_image, u.linkedin_url,
                   (SELECT COUNT(*) FROM mentorship_sessions ms WHERE ms.program_id = mp.program_id) as current_mentees
            FROM mentorship_programs mp
            JOIN users u ON mp.mentor_id = u.user_id
            WHERE {where_clause}
            ORDER BY mp.created_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        # Parse expertise areas JSON
        for program in programs:
            if program['expertise_areas']:
                try:
                    program['expertise_areas'] = json.loads(program['expertise_areas'])
                except:
                    program['expertise_areas'] = []
        
        # Get total count
        total = execute_query(f"""
            SELECT COUNT(*) as count 
            FROM mentorship_programs mp
            JOIN users u ON mp.mentor_id = u.user_id
            WHERE {where_clause}
        """, params, fetch_one=True)['count']
        
        return jsonify({
            'programs': programs,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get mentorship programs', 'details': str(e)}), 500

@mentorship_bp.route('/programs', methods=['POST'])
@jwt_required_custom
@role_required('alumni', 'mentor')
def create_mentorship_program():
    try:
        user = request.current_user
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'expertise_areas']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate expertise areas
        expertise_areas = data['expertise_areas']
        if not isinstance(expertise_areas, list) or len(expertise_areas) == 0:
            return jsonify({'error': 'Expertise areas must be a non-empty list'}), 400
        
        # Validate numeric fields
        max_mentees = data.get('max_mentees', 5)
        duration_weeks = data.get('duration_weeks', 12)
        
        try:
            max_mentees = int(max_mentees)
            duration_weeks = int(duration_weeks)
            if max_mentees < 1 or duration_weeks < 1:
                raise ValueError()
        except ValueError:
            return jsonify({'error': 'max_mentees and duration_weeks must be positive integers'}), 400
        
        # Create mentorship program
        program_id = execute_query("""
            INSERT INTO mentorship_programs (
                mentor_id, title, description, expertise_areas, max_mentees, duration_weeks
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user['user_id'], data['title'], data['description'],
            json.dumps(expertise_areas), max_mentees, duration_weeks
        ))
        
        # Get the created program
        program = execute_query("""
            SELECT mp.*, u.first_name, u.last_name, u.current_position
            FROM mentorship_programs mp
            JOIN users u ON mp.mentor_id = u.user_id
            WHERE mp.program_id = %s
        """, (program_id,), fetch_one=True)
        
        if program['expertise_areas']:
            program['expertise_areas'] = json.loads(program['expertise_areas'])
        
        return jsonify({
            'message': 'Mentorship program created successfully',
            'program': program
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create mentorship program', 'details': str(e)}), 500

@mentorship_bp.route('/sessions', methods=['GET'])
@jwt_required_custom
def get_mentorship_sessions():
    try:
        user = request.current_user
        status = request.args.get('status', '')
        
        # Build query based on user role
        if user['role'] == 'student':
            # Get sessions where user is mentee
            conditions = ["ms.mentee_id = %s"]
            params = [user['user_id']]
        else:
            # Get sessions where user is mentor
            conditions = ["ms.mentor_id = %s"]
            params = [user['user_id']]
        
        if status:
            conditions.append("ms.status = %s")
            params.append(status)
        
        where_clause = " AND ".join(conditions)
        
        sessions = execute_query(f"""
            SELECT ms.*, mp.title as program_title,
                   mentor.first_name as mentor_first_name, mentor.last_name as mentor_last_name,
                   mentor.current_position as mentor_position, mentor.profile_image as mentor_image,
                   mentee.first_name as mentee_first_name, mentee.last_name as mentee_last_name,
                   mentee.major as mentee_major, mentee.graduation_year as mentee_graduation_year
            FROM mentorship_sessions ms
            LEFT JOIN mentorship_programs mp ON ms.program_id = mp.program_id
            JOIN users mentor ON ms.mentor_id = mentor.user_id
            JOIN users mentee ON ms.mentee_id = mentee.user_id
            WHERE {where_clause}
            ORDER BY ms.scheduled_date DESC, ms.created_at DESC
        """, params)
        
        return jsonify({'sessions': sessions}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get mentorship sessions', 'details': str(e)}), 500

@mentorship_bp.route('/request', methods=['POST'])
@jwt_required_custom
@role_required('student')
def request_mentorship():
    try:
        user = request.current_user
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['mentor_id', 'session_type', 'title', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate session type
        valid_types = ['resume_review', 'interview_prep', 'career_guidance', 'skill_development', 'networking']
        if data['session_type'] not in valid_types:
            return jsonify({'error': f'Session type must be one of: {", ".join(valid_types)}'}), 400
        
        # Check if mentor exists and is active
        mentor = execute_query(
            "SELECT user_id, role FROM users WHERE user_id = %s AND is_active = TRUE",
            (data['mentor_id'],), fetch_one=True
        )
        
        if not mentor:
            return jsonify({'error': 'Mentor not found'}), 404
        
        if mentor['role'] not in ['alumni', 'mentor']:
            return jsonify({'error': 'User is not a mentor'}), 400
        
        # Parse scheduled date if provided
        scheduled_date = None
        if data.get('scheduled_date'):
            try:
                scheduled_date = datetime.strptime(data['scheduled_date'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}), 400
        
        # Create mentorship session request
        session_id = execute_query("""
            INSERT INTO mentorship_sessions (
                program_id, mentor_id, mentee_id, title, description, session_type,
                scheduled_date, duration_minutes, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'requested')
        """, (
            data.get('program_id'), data['mentor_id'], user['user_id'],
            data['title'], data['description'], data['session_type'],
            scheduled_date, data.get('duration_minutes', 60)
        ))
        
        # Get the created session
        session = execute_query("""
            SELECT ms.*, 
                   mentor.first_name as mentor_first_name, mentor.last_name as mentor_last_name,
                   mentee.first_name as mentee_first_name, mentee.last_name as mentee_last_name
            FROM mentorship_sessions ms
            JOIN users mentor ON ms.mentor_id = mentor.user_id
            JOIN users mentee ON ms.mentee_id = mentee.user_id
            WHERE ms.session_id = %s
        """, (session_id,), fetch_one=True)
        
        return jsonify({
            'message': 'Mentorship request sent successfully',
            'session': session
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to request mentorship', 'details': str(e)}), 500

@mentorship_bp.route('/sessions/<int:session_id>', methods=['PUT'])
@jwt_required_custom
def update_mentorship_session(session_id):
    try:
        user = request.current_user
        data = request.get_json()
        
        # Get session details
        session = execute_query(
            "SELECT mentor_id, mentee_id, status FROM mentorship_sessions WHERE session_id = %s",
            (session_id,), fetch_one=True
        )
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check permissions
        if user['user_id'] not in [session['mentor_id'], session['mentee_id']]:
            return jsonify({'error': 'You can only update your own sessions'}), 403
        
        # Fields that can be updated
        updatable_fields = ['status', 'scheduled_date', 'duration_minutes', 'meeting_link', 'notes']
        
        # Only mentors can approve/reject requests
        if data.get('status') in ['scheduled', 'cancelled'] and user['user_id'] != session['mentor_id']:
            return jsonify({'error': 'Only mentors can change session status'}), 403
        
        update_data = {}
        for field in updatable_fields:
            if field in data:
                if field == 'scheduled_date' and data[field]:
                    try:
                        update_data[field] = datetime.strptime(data[field], '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}), 400
                else:
                    update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Build update query
        set_clause = ', '.join([f"{field} = %s" for field in update_data.keys()])
        values = list(update_data.values()) + [session_id]
        
        execute_query(
            f"UPDATE mentorship_sessions SET {set_clause} WHERE session_id = %s",
            values
        )
        
        return jsonify({'message': 'Session updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update session', 'details': str(e)}), 500

@mentorship_bp.route('/sessions/<int:session_id>/feedback', methods=['POST'])
@jwt_required_custom
def submit_feedback(session_id):
    try:
        user = request.current_user
        data = request.get_json()
        
        # Get session details
        session = execute_query(
            "SELECT mentor_id, mentee_id, status FROM mentorship_sessions WHERE session_id = %s",
            (session_id,), fetch_one=True
        )
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        if session['status'] != 'completed':
            return jsonify({'error': 'Can only provide feedback for completed sessions'}), 400
        
        # Check if user is part of this session
        if user['user_id'] not in [session['mentor_id'], session['mentee_id']]:
            return jsonify({'error': 'You can only provide feedback for your own sessions'}), 403
        
        # Validate rating
        rating = data.get('feedback_rating')
        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            except ValueError:
                return jsonify({'error': 'Rating must be a number'}), 400
        
        # Update session with feedback
        execute_query("""
            UPDATE mentorship_sessions 
            SET feedback_rating = %s, feedback_comment = %s 
            WHERE session_id = %s
        """, (rating, data.get('feedback_comment', ''), session_id))
        
        return jsonify({'message': 'Feedback submitted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to submit feedback', 'details': str(e)}), 500

@mentorship_bp.route('/mentors', methods=['GET'])
def get_available_mentors():
    try:
        expertise = request.args.get('expertise', '')
        search = request.args.get('search', '')
        
        # Build query conditions
        conditions = ["u.role IN ('alumni', 'mentor')", "u.is_active = TRUE"]
        params = []
        
        if search:
            conditions.append("(u.first_name LIKE %s OR u.last_name LIKE %s OR u.current_company LIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        if expertise:
            conditions.append("(u.skills LIKE %s OR mp.expertise_areas LIKE %s)")
            expertise_param = f"%{expertise}%"
            params.extend([expertise_param, expertise_param])
        
        where_clause = " AND ".join(conditions)
        
        mentors = execute_query(f"""
            SELECT DISTINCT u.user_id, u.first_name, u.last_name, u.current_position,
                   u.current_company, u.location, u.bio, u.skills, u.linkedin_url,
                   u.profile_image, u.graduation_year,
                   COUNT(DISTINCT mp.program_id) as program_count,
                   COUNT(DISTINCT ms.session_id) as session_count
            FROM users u
            LEFT JOIN mentorship_programs mp ON u.user_id = mp.mentor_id AND mp.is_active = TRUE
            LEFT JOIN mentorship_sessions ms ON u.user_id = ms.mentor_id
            WHERE {where_clause}
            GROUP BY u.user_id
            ORDER BY program_count DESC, session_count DESC, u.first_name ASC
        """, params)
        
        # Parse skills JSON
        for mentor in mentors:
            if mentor['skills']:
                try:
                    mentor['skills'] = json.loads(mentor['skills'])
                except:
                    mentor['skills'] = []
        
        return jsonify({'mentors': mentors}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get mentors', 'details': str(e)}), 500