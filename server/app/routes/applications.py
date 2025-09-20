from flask import Blueprint, request, jsonify
from app.models.database import execute_query
from app.utils.auth import jwt_required_custom, role_required

applications_bp = Blueprint('applications', __name__)

@applications_bp.route('', methods=['POST'])
@jwt_required_custom
@role_required('student')
def submit_application():
    try:
        user = request.current_user
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['application_type']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        application_type = data['application_type']
        
        if application_type not in ['opportunity', 'scholarship']:
            return jsonify({'error': 'Application type must be "opportunity" or "scholarship"'}), 400
        
        # Validate type-specific requirements
        if application_type == 'opportunity':
            if not data.get('opportunity_id'):
                return jsonify({'error': 'opportunity_id is required for opportunity applications'}), 400
            
            # Check if opportunity exists and is active
            opportunity = execute_query(
                "SELECT opportunity_id, application_deadline FROM opportunities WHERE opportunity_id = %s AND is_active = TRUE",
                (data['opportunity_id'],), fetch_one=True
            )
            
            if not opportunity:
                return jsonify({'error': 'Opportunity not found or inactive'}), 404
            
            # Check if already applied
            existing_application = execute_query(
                "SELECT application_id FROM applications WHERE user_id = %s AND opportunity_id = %s",
                (user['user_id'], data['opportunity_id']), fetch_one=True
            )
            
            if existing_application:
                return jsonify({'error': 'You have already applied for this opportunity'}), 409
            
            opportunity_id = data['opportunity_id']
            scholarship_id = None
            
        else:  # scholarship
            if not data.get('scholarship_id'):
                return jsonify({'error': 'scholarship_id is required for scholarship applications'}), 400
            
            # Check if scholarship exists and is active
            scholarship = execute_query(
                "SELECT scholarship_id, application_deadline FROM scholarships WHERE scholarship_id = %s AND is_active = TRUE",
                (data['scholarship_id'],), fetch_one=True
            )
            
            if not scholarship:
                return jsonify({'error': 'Scholarship not found or inactive'}), 404
            
            # Check if already applied
            existing_application = execute_query(
                "SELECT application_id FROM applications WHERE user_id = %s AND scholarship_id = %s",
                (user['user_id'], data['scholarship_id']), fetch_one=True
            )
            
            if existing_application:
                return jsonify({'error': 'You have already applied for this scholarship'}), 409
            
            opportunity_id = None
            scholarship_id = data['scholarship_id']
        
        # Create application
        application_id = execute_query("""
            INSERT INTO applications (
                user_id, opportunity_id, scholarship_id, application_type,
                cover_letter, resume_url, additional_documents
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            user['user_id'], opportunity_id, scholarship_id, application_type,
            data.get('cover_letter', ''), data.get('resume_url', ''),
            data.get('additional_documents', '')
        ))
        
        # Get the created application with related information
        if application_type == 'opportunity':
            application = execute_query("""
                SELECT a.*, o.title, o.company, o.type as opportunity_type
                FROM applications a
                JOIN opportunities o ON a.opportunity_id = o.opportunity_id
                WHERE a.application_id = %s
            """, (application_id,), fetch_one=True)
        else:
            application = execute_query("""
                SELECT a.*, s.title, s.organization, s.amount
                FROM applications a
                JOIN scholarships s ON a.scholarship_id = s.scholarship_id
                WHERE a.application_id = %s
            """, (application_id,), fetch_one=True)
        
        return jsonify({
            'message': 'Application submitted successfully',
            'application': application
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to submit application', 'details': str(e)}), 500

@applications_bp.route('/my', methods=['GET'])
@jwt_required_custom
@role_required('student')
def get_my_applications():
    try:
        user = request.current_user
        application_type = request.args.get('type', '')
        status = request.args.get('status', '')
        
        # Build query conditions
        conditions = ["a.user_id = %s"]
        params = [user['user_id']]
        
        if application_type:
            conditions.append("a.application_type = %s")
            params.append(application_type)
        
        if status:
            conditions.append("a.status = %s")
            params.append(status)
        
        where_clause = " AND ".join(conditions)
        
        # Get applications with related information
        applications = execute_query(f"""
            SELECT a.application_id, a.application_type, a.status, a.cover_letter,
                   a.resume_url, a.submitted_at, a.updated_at,
                   CASE 
                       WHEN a.application_type = 'opportunity' THEN o.title
                       ELSE s.title
                   END as title,
                   CASE 
                       WHEN a.application_type = 'opportunity' THEN o.company
                       ELSE s.organization
                   END as organization,
                   CASE 
                       WHEN a.application_type = 'opportunity' THEN o.type
                       ELSE 'scholarship'
                   END as type,
                   CASE 
                       WHEN a.application_type = 'opportunity' THEN o.opportunity_id
                       ELSE s.scholarship_id
                   END as item_id
            FROM applications a
            LEFT JOIN opportunities o ON a.opportunity_id = o.opportunity_id
            LEFT JOIN scholarships s ON a.scholarship_id = s.scholarship_id
            WHERE {where_clause}
            ORDER BY a.submitted_at DESC
        """, params)
        
        return jsonify({'applications': applications}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get your applications', 'details': str(e)}), 500

@applications_bp.route('/<int:application_id>', methods=['GET'])
@jwt_required_custom
def get_application(application_id):
    try:
        user = request.current_user
        
        # Get application with related information
        application = execute_query("""
            SELECT a.*, u.first_name, u.last_name, u.email, u.major, u.graduation_year,
                   CASE 
                       WHEN a.application_type = 'opportunity' THEN o.title
                       ELSE s.title
                   END as title,
                   CASE 
                       WHEN a.application_type = 'opportunity' THEN o.company
                       ELSE s.organization
                   END as organization,
                   CASE 
                       WHEN a.application_type = 'opportunity' THEN o.posted_by
                       ELSE s.posted_by
                   END as posted_by
            FROM applications a
            JOIN users u ON a.user_id = u.user_id
            LEFT JOIN opportunities o ON a.opportunity_id = o.opportunity_id
            LEFT JOIN scholarships s ON a.scholarship_id = s.scholarship_id
            WHERE a.application_id = %s
        """, (application_id,), fetch_one=True)
        
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        # Check permissions - user can view their own applications or applications for their postings
        if application['user_id'] != user['user_id'] and application['posted_by'] != user['user_id']:
            return jsonify({'error': 'You can only view your own applications or applications for your postings'}), 403
        
        return jsonify({'application': application}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get application', 'details': str(e)}), 500

@applications_bp.route('/<int:application_id>/status', methods=['PUT'])
@jwt_required_custom
@role_required('alumni', 'mentor')
def update_application_status(application_id):
    try:
        user = request.current_user
        data = request.get_json()
        
        if not data.get('status'):
            return jsonify({'error': 'Status is required'}), 400
        
        valid_statuses = ['submitted', 'under_review', 'shortlisted', 'accepted', 'rejected']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Status must be one of: {", ".join(valid_statuses)}'}), 400
        
        # Get application and check if user owns the related opportunity/scholarship
        application = execute_query("""
            SELECT a.application_id, a.application_type,
                   CASE 
                       WHEN a.application_type = 'opportunity' THEN o.posted_by
                       ELSE s.posted_by
                   END as posted_by
            FROM applications a
            LEFT JOIN opportunities o ON a.opportunity_id = o.opportunity_id
            LEFT JOIN scholarships s ON a.scholarship_id = s.scholarship_id
            WHERE a.application_id = %s
        """, (application_id,), fetch_one=True)
        
        if not application:
            return jsonify({'error': 'Application not found'}), 404
        
        if application['posted_by'] != user['user_id']:
            return jsonify({'error': 'You can only update applications for your own postings'}), 403
        
        # Update application status
        execute_query(
            "UPDATE applications SET status = %s WHERE application_id = %s",
            (data['status'], application_id)
        )
        
        return jsonify({'message': 'Application status updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update application status', 'details': str(e)}), 500

@applications_bp.route('/received', methods=['GET'])
@jwt_required_custom
@role_required('alumni', 'mentor')
def get_received_applications():
    try:
        user = request.current_user
        application_type = request.args.get('type', '')
        status = request.args.get('status', '')
        
        # Build query conditions
        conditions = []
        params = []
        
        if application_type == 'opportunity':
            conditions.append("o.posted_by = %s")
            params.append(user['user_id'])
        elif application_type == 'scholarship':
            conditions.append("s.posted_by = %s")
            params.append(user['user_id'])
        else:
            conditions.append("(o.posted_by = %s OR s.posted_by = %s)")
            params.extend([user['user_id'], user['user_id']])
        
        if status:
            conditions.append("a.status = %s")
            params.append(status)
        
        where_clause = " AND ".join(conditions)
        
        # Get applications received for user's postings
        applications = execute_query(f"""
            SELECT a.application_id, a.application_type, a.status, a.cover_letter,
                   a.submitted_at, a.updated_at,
                   u.first_name, u.last_name, u.email, u.major, u.graduation_year,
                   u.skills, u.linkedin_url,
                   CASE 
                       WHEN a.application_type = 'opportunity' THEN o.title
                       ELSE s.title
                   END as title,
                   CASE 
                       WHEN a.application_type = 'opportunity' THEN o.company
                       ELSE s.organization
                   END as organization,
                   CASE 
                       WHEN a.application_type = 'opportunity' THEN o.opportunity_id
                       ELSE s.scholarship_id
                   END as item_id
            FROM applications a
            JOIN users u ON a.user_id = u.user_id
            LEFT JOIN opportunities o ON a.opportunity_id = o.opportunity_id
            LEFT JOIN scholarships s ON a.scholarship_id = s.scholarship_id
            WHERE {where_clause}
            ORDER BY a.submitted_at DESC
        """, params)
        
        return jsonify({'applications': applications}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get received applications', 'details': str(e)}), 500

@applications_bp.route('/stats', methods=['GET'])
@jwt_required_custom
def get_application_stats():
    try:
        user = request.current_user
        
        if user['role'] == 'student':
            # Get student application statistics
            stats = execute_query("""
                SELECT 
                    COUNT(*) as total_applications,
                    SUM(CASE WHEN status = 'submitted' THEN 1 ELSE 0 END) as submitted,
                    SUM(CASE WHEN status = 'under_review' THEN 1 ELSE 0 END) as under_review,
                    SUM(CASE WHEN status = 'shortlisted' THEN 1 ELSE 0 END) as shortlisted,
                    SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) as accepted,
                    SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected,
                    SUM(CASE WHEN application_type = 'opportunity' THEN 1 ELSE 0 END) as opportunity_applications,
                    SUM(CASE WHEN application_type = 'scholarship' THEN 1 ELSE 0 END) as scholarship_applications
                FROM applications 
                WHERE user_id = %s
            """, (user['user_id'],), fetch_one=True)
            
        else:
            # Get alumni/mentor application statistics for their postings
            stats = execute_query("""
                SELECT 
                    COUNT(*) as total_applications,
                    SUM(CASE WHEN a.status = 'submitted' THEN 1 ELSE 0 END) as submitted,
                    SUM(CASE WHEN a.status = 'under_review' THEN 1 ELSE 0 END) as under_review,
                    SUM(CASE WHEN a.status = 'shortlisted' THEN 1 ELSE 0 END) as shortlisted,
                    SUM(CASE WHEN a.status = 'accepted' THEN 1 ELSE 0 END) as accepted,
                    SUM(CASE WHEN a.status = 'rejected' THEN 1 ELSE 0 END) as rejected,
                    SUM(CASE WHEN a.application_type = 'opportunity' THEN 1 ELSE 0 END) as opportunity_applications,
                    SUM(CASE WHEN a.application_type = 'scholarship' THEN 1 ELSE 0 END) as scholarship_applications
                FROM applications a
                LEFT JOIN opportunities o ON a.opportunity_id = o.opportunity_id
                LEFT JOIN scholarships s ON a.scholarship_id = s.scholarship_id
                WHERE o.posted_by = %s OR s.posted_by = %s
            """, (user['user_id'], user['user_id']), fetch_one=True)
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get application statistics', 'details': str(e)}), 500