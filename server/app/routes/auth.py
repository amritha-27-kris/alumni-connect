from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.database import execute_query
from app.utils.auth import hash_password, check_password, validate_email, validate_password
import json

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'password', 'first_name', 'last_name', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        role = data['role']
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if not validate_password(password):
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        # Validate role
        if role not in ['student', 'alumni', 'mentor']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Check if user already exists
        existing_user = execute_query(
            "SELECT user_id FROM users WHERE email = %s",
            (email,),
            fetch_one=True
        )
        
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Hash password
        password_hash = hash_password(password)
        
        # Prepare optional fields
        graduation_year = data.get('graduation_year')
        degree = data.get('degree', '').strip()
        major = data.get('major', '').strip()
        current_company = data.get('current_company', '').strip()
        current_position = data.get('current_position', '').strip()
        location = data.get('location', '').strip()
        bio = data.get('bio', '').strip()
        skills = json.dumps(data.get('skills', []))
        linkedin_url = data.get('linkedin_url', '').strip()
        
        # Insert new user
        user_id = execute_query("""
            INSERT INTO users (
                email, password_hash, first_name, last_name, role,
                graduation_year, degree, major, current_company, current_position,
                location, bio, skills, linkedin_url
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            email, password_hash, first_name, last_name, role,
            graduation_year, degree, major, current_company, current_position,
            location, bio, skills, linkedin_url
        ))
        
        # Create access token
        access_token = create_access_token(identity=user_id)
        
        # Get user data for response
        user = execute_query("""
            SELECT user_id, email, first_name, last_name, role, graduation_year,
                   degree, major, current_company, current_position, location, bio,
                   skills, linkedin_url, is_verified, created_at
            FROM users WHERE user_id = %s
        """, (user_id,), fetch_one=True)
        
        # Parse skills JSON
        if user['skills']:
            user['skills'] = json.loads(user['skills'])
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': user
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Registration failed', 'details': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Get user from database
        user = execute_query("""
            SELECT user_id, email, password_hash, first_name, last_name, role,
                   graduation_year, degree, major, current_company, current_position,
                   location, bio, skills, linkedin_url, is_verified, is_active
            FROM users WHERE email = %s
        """, (email,), fetch_one=True)
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user['is_active']:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Check password
        if not check_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create access token
        access_token = create_access_token(identity=user['user_id'])
        
        # Remove password hash from response
        del user['password_hash']
        
        # Parse skills JSON
        if user['skills']:
            user['skills'] = json.loads(user['skills'])
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'details': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        
        user = execute_query("""
            SELECT user_id, email, first_name, last_name, role, graduation_year,
                   degree, major, current_company, current_position, location, bio,
                   skills, linkedin_url, github_url, portfolio_url, profile_image,
                   is_verified, created_at, updated_at
            FROM users WHERE user_id = %s AND is_active = TRUE
        """, (user_id,), fetch_one=True)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Parse skills JSON
        if user['skills']:
            user['skills'] = json.loads(user['skills'])
        
        return jsonify({'user': user}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get user info', 'details': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # In a production app, you might want to blacklist the token
    # For now, we'll just return a success message
    return jsonify({'message': 'Logout successful'}), 200