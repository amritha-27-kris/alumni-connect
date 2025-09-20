from flask import Blueprint, request, jsonify
from app.models.database import execute_query
from app.utils.auth import jwt_required_custom

connections_bp = Blueprint('connections', __name__)

@connections_bp.route('', methods=['GET'])
@jwt_required_custom
def get_connections():
    try:
        user = request.current_user
        status = request.args.get('status', 'accepted')
        connection_type = request.args.get('type', 'all')  # 'sent', 'received', 'all'
        
        # Build query based on connection type
        if connection_type == 'sent':
            # Connections requested by current user
            connections = execute_query("""
                SELECT c.connection_id, c.status, c.message, c.created_at, c.updated_at,
                       u.user_id, u.first_name, u.last_name, u.current_position, u.current_company,
                       u.profile_image, u.linkedin_url, u.graduation_year, u.major
                FROM connections c
                JOIN users u ON c.recipient_id = u.user_id
                WHERE c.requester_id = %s AND c.status = %s
                ORDER BY c.created_at DESC
            """, (user['user_id'], status))
            
        elif connection_type == 'received':
            # Connection requests received by current user
            connections = execute_query("""
                SELECT c.connection_id, c.status, c.message, c.created_at, c.updated_at,
                       u.user_id, u.first_name, u.last_name, u.current_position, u.current_company,
                       u.profile_image, u.linkedin_url, u.graduation_year, u.major
                FROM connections c
                JOIN users u ON c.requester_id = u.user_id
                WHERE c.recipient_id = %s AND c.status = %s
                ORDER BY c.created_at DESC
            """, (user['user_id'], status))
            
        else:
            # All connections (both sent and received)
            connections = execute_query("""
                SELECT c.connection_id, c.status, c.message, c.created_at, c.updated_at,
                       CASE 
                           WHEN c.requester_id = %s THEN 'sent'
                           ELSE 'received'
                       END as connection_type,
                       CASE 
                           WHEN c.requester_id = %s THEN recipient.user_id
                           ELSE requester.user_id
                       END as other_user_id,
                       CASE 
                           WHEN c.requester_id = %s THEN recipient.first_name
                           ELSE requester.first_name
                       END as first_name,
                       CASE 
                           WHEN c.requester_id = %s THEN recipient.last_name
                           ELSE requester.last_name
                       END as last_name,
                       CASE 
                           WHEN c.requester_id = %s THEN recipient.current_position
                           ELSE requester.current_position
                       END as current_position,
                       CASE 
                           WHEN c.requester_id = %s THEN recipient.current_company
                           ELSE requester.current_company
                       END as current_company,
                       CASE 
                           WHEN c.requester_id = %s THEN recipient.profile_image
                           ELSE requester.profile_image
                       END as profile_image
                FROM connections c
                JOIN users requester ON c.requester_id = requester.user_id
                JOIN users recipient ON c.recipient_id = recipient.user_id
                WHERE (c.requester_id = %s OR c.recipient_id = %s) AND c.status = %s
                ORDER BY c.created_at DESC
            """, (user['user_id'], user['user_id'], user['user_id'], user['user_id'], 
                  user['user_id'], user['user_id'], user['user_id'], user['user_id'], user['user_id'], status))
        
        return jsonify({'connections': connections}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get connections', 'details': str(e)}), 500

@connections_bp.route('/request', methods=['POST'])
@jwt_required_custom
def send_connection_request():
    try:
        user = request.current_user
        data = request.get_json()
        
        if not data.get('recipient_id'):
            return jsonify({'error': 'recipient_id is required'}), 400
        
        recipient_id = data['recipient_id']
        
        # Check if recipient exists and is active
        recipient = execute_query(
            "SELECT user_id, first_name, last_name FROM users WHERE user_id = %s AND is_active = TRUE",
            (recipient_id,), fetch_one=True
        )
        
        if not recipient:
            return jsonify({'error': 'User not found'}), 404
        
        if recipient_id == user['user_id']:
            return jsonify({'error': 'Cannot send connection request to yourself'}), 400
        
        # Check if connection already exists
        existing_connection = execute_query("""
            SELECT connection_id, status FROM connections 
            WHERE (requester_id = %s AND recipient_id = %s) 
               OR (requester_id = %s AND recipient_id = %s)
        """, (user['user_id'], recipient_id, recipient_id, user['user_id']), fetch_one=True)
        
        if existing_connection:
            if existing_connection['status'] == 'accepted':
                return jsonify({'error': 'You are already connected with this user'}), 409
            elif existing_connection['status'] == 'pending':
                return jsonify({'error': 'Connection request already pending'}), 409
            else:
                # If previously declined, allow new request
                execute_query(
                    "UPDATE connections SET status = 'pending', message = %s WHERE connection_id = %s",
                    (data.get('message', ''), existing_connection['connection_id'])
                )
                return jsonify({'message': 'Connection request sent successfully'}), 200
        
        # Create new connection request
        connection_id = execute_query("""
            INSERT INTO connections (requester_id, recipient_id, message)
            VALUES (%s, %s, %s)
        """, (user['user_id'], recipient_id, data.get('message', '')))
        
        # Get the created connection
        connection = execute_query("""
            SELECT c.*, 
                   requester.first_name as requester_first_name, requester.last_name as requester_last_name,
                   recipient.first_name as recipient_first_name, recipient.last_name as recipient_last_name
            FROM connections c
            JOIN users requester ON c.requester_id = requester.user_id
            JOIN users recipient ON c.recipient_id = recipient.user_id
            WHERE c.connection_id = %s
        """, (connection_id,), fetch_one=True)
        
        return jsonify({
            'message': 'Connection request sent successfully',
            'connection': connection
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to send connection request', 'details': str(e)}), 500

@connections_bp.route('/<int:connection_id>/respond', methods=['PUT'])
@jwt_required_custom
def respond_to_connection_request(connection_id):
    try:
        user = request.current_user
        data = request.get_json()
        
        if not data.get('status'):
            return jsonify({'error': 'Status is required'}), 400
        
        if data['status'] not in ['accepted', 'declined']:
            return jsonify({'error': 'Status must be "accepted" or "declined"'}), 400
        
        # Get connection and check if user is the recipient
        connection = execute_query(
            "SELECT connection_id, recipient_id, status FROM connections WHERE connection_id = %s",
            (connection_id,), fetch_one=True
        )
        
        if not connection:
            return jsonify({'error': 'Connection request not found'}), 404
        
        if connection['recipient_id'] != user['user_id']:
            return jsonify({'error': 'You can only respond to connection requests sent to you'}), 403
        
        if connection['status'] != 'pending':
            return jsonify({'error': 'Connection request is not pending'}), 400
        
        # Update connection status
        execute_query(
            "UPDATE connections SET status = %s WHERE connection_id = %s",
            (data['status'], connection_id)
        )
        
        action = 'accepted' if data['status'] == 'accepted' else 'declined'
        return jsonify({'message': f'Connection request {action} successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to respond to connection request', 'details': str(e)}), 500

@connections_bp.route('/<int:connection_id>', methods=['DELETE'])
@jwt_required_custom
def remove_connection(connection_id):
    try:
        user = request.current_user
        
        # Get connection and check if user is involved
        connection = execute_query(
            "SELECT connection_id, requester_id, recipient_id FROM connections WHERE connection_id = %s",
            (connection_id,), fetch_one=True
        )
        
        if not connection:
            return jsonify({'error': 'Connection not found'}), 404
        
        if user['user_id'] not in [connection['requester_id'], connection['recipient_id']]:
            return jsonify({'error': 'You can only remove your own connections'}), 403
        
        # Delete connection
        execute_query("DELETE FROM connections WHERE connection_id = %s", (connection_id,))
        
        return jsonify({'message': 'Connection removed successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to remove connection', 'details': str(e)}), 500

@connections_bp.route('/suggestions', methods=['GET'])
@jwt_required_custom
def get_connection_suggestions():
    try:
        user = request.current_user
        limit = int(request.args.get('limit', 10))
        
        # Get users who are not already connected and have similar interests
        suggestions = execute_query("""
            SELECT DISTINCT u.user_id, u.first_name, u.last_name, u.current_position, 
                   u.current_company, u.profile_image, u.graduation_year, u.major, u.skills,
                   u.linkedin_url
            FROM users u
            WHERE u.user_id != %s 
              AND u.is_active = TRUE
              AND u.role IN ('alumni', 'mentor', 'student')
              AND u.user_id NOT IN (
                  SELECT CASE 
                      WHEN requester_id = %s THEN recipient_id 
                      ELSE requester_id 
                  END
                  FROM connections 
                  WHERE (requester_id = %s OR recipient_id = %s) 
                    AND status IN ('accepted', 'pending')
              )
            ORDER BY 
              CASE WHEN u.major = (SELECT major FROM users WHERE user_id = %s) THEN 1 ELSE 2 END,
              CASE WHEN u.role != %s THEN 1 ELSE 2 END,
              RAND()
            LIMIT %s
        """, (user['user_id'], user['user_id'], user['user_id'], user['user_id'], 
              user['user_id'], user['role'], limit))
        
        return jsonify({'suggestions': suggestions}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get connection suggestions', 'details': str(e)}), 500

@connections_bp.route('/stats', methods=['GET'])
@jwt_required_custom
def get_connection_stats():
    try:
        user = request.current_user
        
        stats = execute_query("""
            SELECT 
                COUNT(CASE WHEN status = 'accepted' THEN 1 END) as total_connections,
                COUNT(CASE WHEN status = 'pending' AND recipient_id = %s THEN 1 END) as pending_requests,
                COUNT(CASE WHEN status = 'pending' AND requester_id = %s THEN 1 END) as sent_requests
            FROM connections 
            WHERE requester_id = %s OR recipient_id = %s
        """, (user['user_id'], user['user_id'], user['user_id'], user['user_id']), fetch_one=True)
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get connection statistics', 'details': str(e)}), 500