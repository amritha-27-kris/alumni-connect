from flask import Blueprint, request, jsonify
from app.models.database import execute_query
from app.utils.auth import jwt_required_custom

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('', methods=['GET'])
@jwt_required_custom
def get_messages():
    try:
        user = request.current_user
        message_type = request.args.get('type', 'received')  # 'sent' or 'received'
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        offset = (page - 1) * limit
        
        if message_type == 'sent':
            messages = execute_query("""
                SELECT m.message_id, m.subject, m.content, m.is_read, m.sent_at,
                       u.first_name, u.last_name, u.profile_image, u.current_position
                FROM messages m
                JOIN users u ON m.recipient_id = u.user_id
                WHERE m.sender_id = %s
                ORDER BY m.sent_at DESC
                LIMIT %s OFFSET %s
            """, (user['user_id'], limit, offset))
        else:
            messages = execute_query("""
                SELECT m.message_id, m.subject, m.content, m.is_read, m.sent_at,
                       u.first_name, u.last_name, u.profile_image, u.current_position
                FROM messages m
                JOIN users u ON m.sender_id = u.user_id
                WHERE m.recipient_id = %s
                ORDER BY m.sent_at DESC
                LIMIT %s OFFSET %s
            """, (user['user_id'], limit, offset))
        
        # Get total count
        if message_type == 'sent':
            total = execute_query(
                "SELECT COUNT(*) as count FROM messages WHERE sender_id = %s",
                (user['user_id'],), fetch_one=True
            )['count']
        else:
            total = execute_query(
                "SELECT COUNT(*) as count FROM messages WHERE recipient_id = %s",
                (user['user_id'],), fetch_one=True
            )['count']
        
        return jsonify({
            'messages': messages,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get messages', 'details': str(e)}), 500

@messages_bp.route('', methods=['POST'])
@jwt_required_custom
def send_message():
    try:
        user = request.current_user
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['recipient_id', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if recipient exists and is active
        recipient = execute_query(
            "SELECT user_id, first_name, last_name FROM users WHERE user_id = %s AND is_active = TRUE",
            (data['recipient_id'],), fetch_one=True
        )
        
        if not recipient:
            return jsonify({'error': 'Recipient not found'}), 404
        
        if recipient['user_id'] == user['user_id']:
            return jsonify({'error': 'Cannot send message to yourself'}), 400
        
        # Send message
        message_id = execute_query("""
            INSERT INTO messages (sender_id, recipient_id, subject, content)
            VALUES (%s, %s, %s, %s)
        """, (
            user['user_id'], data['recipient_id'],
            data.get('subject', ''), data['content']
        ))
        
        # Get the sent message
        message = execute_query("""
            SELECT m.*, 
                   sender.first_name as sender_first_name, sender.last_name as sender_last_name,
                   recipient.first_name as recipient_first_name, recipient.last_name as recipient_last_name
            FROM messages m
            JOIN users sender ON m.sender_id = sender.user_id
            JOIN users recipient ON m.recipient_id = recipient.user_id
            WHERE m.message_id = %s
        """, (message_id,), fetch_one=True)
        
        return jsonify({
            'message': 'Message sent successfully',
            'sent_message': message
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to send message', 'details': str(e)}), 500

@messages_bp.route('/<int:message_id>', methods=['GET'])
@jwt_required_custom
def get_message(message_id):
    try:
        user = request.current_user
        
        # Get message with sender and recipient information
        message = execute_query("""
            SELECT m.*, 
                   sender.first_name as sender_first_name, sender.last_name as sender_last_name,
                   sender.profile_image as sender_image, sender.current_position as sender_position,
                   recipient.first_name as recipient_first_name, recipient.last_name as recipient_last_name,
                   recipient.profile_image as recipient_image, recipient.current_position as recipient_position
            FROM messages m
            JOIN users sender ON m.sender_id = sender.user_id
            JOIN users recipient ON m.recipient_id = recipient.user_id
            WHERE m.message_id = %s
        """, (message_id,), fetch_one=True)
        
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        # Check permissions - user must be sender or recipient
        if user['user_id'] not in [message['sender_id'], message['recipient_id']]:
            return jsonify({'error': 'You can only view your own messages'}), 403
        
        # Mark as read if user is the recipient
        if user['user_id'] == message['recipient_id'] and not message['is_read']:
            execute_query(
                "UPDATE messages SET is_read = TRUE WHERE message_id = %s",
                (message_id,)
            )
            message['is_read'] = True
        
        return jsonify({'message': message}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get message', 'details': str(e)}), 500

@messages_bp.route('/<int:message_id>/read', methods=['PUT'])
@jwt_required_custom
def mark_as_read(message_id):
    try:
        user = request.current_user
        
        # Check if message exists and user is the recipient
        message = execute_query(
            "SELECT recipient_id FROM messages WHERE message_id = %s",
            (message_id,), fetch_one=True
        )
        
        if not message:
            return jsonify({'error': 'Message not found'}), 404
        
        if message['recipient_id'] != user['user_id']:
            return jsonify({'error': 'You can only mark your own received messages as read'}), 403
        
        # Mark as read
        execute_query(
            "UPDATE messages SET is_read = TRUE WHERE message_id = %s",
            (message_id,)
        )
        
        return jsonify({'message': 'Message marked as read'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to mark message as read', 'details': str(e)}), 500

@messages_bp.route('/conversations', methods=['GET'])
@jwt_required_custom
def get_conversations():
    try:
        user = request.current_user
        
        # Get unique conversations (users the current user has exchanged messages with)
        conversations = execute_query("""
            SELECT DISTINCT
                CASE 
                    WHEN m.sender_id = %s THEN m.recipient_id
                    ELSE m.sender_id
                END as other_user_id,
                u.first_name, u.last_name, u.profile_image, u.current_position,
                (SELECT content FROM messages m2 
                 WHERE (m2.sender_id = %s AND m2.recipient_id = other_user_id) 
                    OR (m2.sender_id = other_user_id AND m2.recipient_id = %s)
                 ORDER BY m2.sent_at DESC LIMIT 1) as last_message,
                (SELECT sent_at FROM messages m2 
                 WHERE (m2.sender_id = %s AND m2.recipient_id = other_user_id) 
                    OR (m2.sender_id = other_user_id AND m2.recipient_id = %s)
                 ORDER BY m2.sent_at DESC LIMIT 1) as last_message_time,
                (SELECT COUNT(*) FROM messages m2 
                 WHERE m2.sender_id = other_user_id AND m2.recipient_id = %s AND m2.is_read = FALSE) as unread_count
            FROM messages m
            JOIN users u ON (CASE WHEN m.sender_id = %s THEN m.recipient_id ELSE m.sender_id END) = u.user_id
            WHERE m.sender_id = %s OR m.recipient_id = %s
            ORDER BY last_message_time DESC
        """, (user['user_id'], user['user_id'], user['user_id'], user['user_id'], 
              user['user_id'], user['user_id'], user['user_id'], user['user_id'], user['user_id']))
        
        return jsonify({'conversations': conversations}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get conversations', 'details': str(e)}), 500

@messages_bp.route('/conversation/<int:other_user_id>', methods=['GET'])
@jwt_required_custom
def get_conversation_messages(other_user_id):
    try:
        user = request.current_user
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        offset = (page - 1) * limit
        
        # Get messages between current user and other user
        messages = execute_query("""
            SELECT m.message_id, m.sender_id, m.recipient_id, m.subject, m.content,
                   m.is_read, m.sent_at,
                   sender.first_name as sender_first_name, sender.last_name as sender_last_name,
                   sender.profile_image as sender_image
            FROM messages m
            JOIN users sender ON m.sender_id = sender.user_id
            WHERE (m.sender_id = %s AND m.recipient_id = %s) 
               OR (m.sender_id = %s AND m.recipient_id = %s)
            ORDER BY m.sent_at DESC
            LIMIT %s OFFSET %s
        """, (user['user_id'], other_user_id, other_user_id, user['user_id'], limit, offset))
        
        # Mark received messages as read
        execute_query("""
            UPDATE messages 
            SET is_read = TRUE 
            WHERE sender_id = %s AND recipient_id = %s AND is_read = FALSE
        """, (other_user_id, user['user_id']))
        
        # Get other user info
        other_user = execute_query("""
            SELECT user_id, first_name, last_name, profile_image, current_position, current_company
            FROM users WHERE user_id = %s AND is_active = TRUE
        """, (other_user_id,), fetch_one=True)
        
        if not other_user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'messages': messages,
            'other_user': other_user
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get conversation messages', 'details': str(e)}), 500

@messages_bp.route('/unread-count', methods=['GET'])
@jwt_required_custom
def get_unread_count():
    try:
        user = request.current_user
        
        unread_count = execute_query(
            "SELECT COUNT(*) as count FROM messages WHERE recipient_id = %s AND is_read = FALSE",
            (user['user_id'],), fetch_one=True
        )['count']
        
        return jsonify({'unread_count': unread_count}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get unread count', 'details': str(e)}), 500