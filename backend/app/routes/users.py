from flask import Blueprint, request, jsonify

user_bp = Blueprint('user_bp', __name__)

# In-memory "database" for demo
users_db = []

@user_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if any(u['email'] == email for u in users_db):
        return jsonify({"success": False, "message": "Email already exists"})
    
    users_db.append({"name": name, "email": email, "password": password})
    return jsonify({"success": True, "message": "Registered successfully"})

@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = next((u for u in users_db if u['email'] == email and u['password'] == password), None)
    if user:
        return jsonify({"success": True, "message": "Login successful"})
    else:
        return jsonify({"success": False, "message": "Invalid credentials"})
