from flask import Blueprint, request, jsonify
from app.models.database import execute_query
from app.utils.auth import jwt_required_custom
import json

stories_bp = Blueprint('stories', __name__)

@stories_bp.route('', methods=['GET'])
def get_stories():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        category = request.args.get('category', '')
        search = request.args.get('search', '')
        featured_only = request.args.get('featured_only', 'false').lower() == 'true'
        
        offset = (page - 1) * limit
        
        # Build query conditions
        conditions = ["s.is_published = TRUE"]
        params = []
        
        if category:
            conditions.append("s.category = %s")
            params.append(category)
        
        if search:
            conditions.append("(s.title LIKE %s OR s.content LIKE %s)")
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        
        if featured_only:
            conditions.append("s.is_featured = TRUE")
        
        where_clause = " AND ".join(conditions)
        
        # Get stories with author information
        stories = execute_query(f"""
            SELECT s.story_id, s.title, s.content, s.category, s.tags, s.is_featured,
                   s.likes_count, s.views_count, s.created_at, s.updated_at,
                   u.first_name, u.last_name, u.current_position, u.current_company,
                   u.profile_image, u.graduation_year
            FROM success_stories s
            JOIN users u ON s.author_id = u.user_id
            WHERE {where_clause}
            ORDER BY s.is_featured DESC, s.created_at DESC
            LIMIT %s OFFSET %s
        """, params + [limit, offset])
        
        # Parse tags JSON and truncate content for list view
        for story in stories:
            if story['tags']:
                try:
                    story['tags'] = json.loads(story['tags'])
                except:
                    story['tags'] = []
            
            # Truncate content for list view (first 200 characters)
            if len(story['content']) > 200:
                story['content_preview'] = story['content'][:200] + '...'
            else:
                story['content_preview'] = story['content']
        
        # Get total count
        total = execute_query(f"""
            SELECT COUNT(*) as count 
            FROM success_stories s
            JOIN users u ON s.author_id = u.user_id
            WHERE {where_clause}
        """, params, fetch_one=True)['count']
        
        return jsonify({
            'stories': stories,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': total,
                'pages': (total + limit - 1) // limit
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get stories', 'details': str(e)}), 500

@stories_bp.route('', methods=['POST'])
@jwt_required_custom
def create_story():
    try:
        user = request.current_user
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'content', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate category
        valid_categories = ['job_placement', 'scholarship', 'career_change', 'skill_development', 'networking']
        if data['category'] not in valid_categories:
            return jsonify({'error': f'Category must be one of: {", ".join(valid_categories)}'}), 400
        
        # Validate and process tags
        tags = data.get('tags', [])
        if not isinstance(tags, list):
            return jsonify({'error': 'Tags must be a list'}), 400
        
        # Create story
        story_id = execute_query("""
            INSERT INTO success_stories (
                author_id, title, content, category, tags, is_published
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            user['user_id'], data['title'], data['content'], data['category'],
            json.dumps(tags), data.get('is_published', True)
        ))
        
        # Get the created story
        story = execute_query("""
            SELECT s.*, u.first_name, u.last_name, u.current_position
            FROM success_stories s
            JOIN users u ON s.author_id = u.user_id
            WHERE s.story_id = %s
        """, (story_id,), fetch_one=True)
        
        if story['tags']:
            story['tags'] = json.loads(story['tags'])
        
        return jsonify({
            'message': 'Story created successfully',
            'story': story
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create story', 'details': str(e)}), 500

@stories_bp.route('/<int:story_id>', methods=['GET'])
def get_story(story_id):
    try:
        # Increment view count
        execute_query(
            "UPDATE success_stories SET views_count = views_count + 1 WHERE story_id = %s",
            (story_id,)
        )
        
        # Get story with author information
        story = execute_query("""
            SELECT s.*, u.first_name, u.last_name, u.current_position, u.current_company,
                   u.profile_image, u.linkedin_url, u.graduation_year
            FROM success_stories s
            JOIN users u ON s.author_id = u.user_id
            WHERE s.story_id = %s AND s.is_published = TRUE
        """, (story_id,), fetch_one=True)
        
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        if story['tags']:
            story['tags'] = json.loads(story['tags'])
        
        return jsonify({'story': story}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get story', 'details': str(e)}), 500

@stories_bp.route('/<int:story_id>/like', methods=['POST'])
@jwt_required_custom
def like_story(story_id):
    try:
        user = request.current_user
        
        # Check if story exists
        story = execute_query(
            "SELECT story_id FROM success_stories WHERE story_id = %s AND is_published = TRUE",
            (story_id,), fetch_one=True
        )
        
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        # Check if already liked
        existing_like = execute_query(
            "SELECT like_id FROM story_likes WHERE story_id = %s AND user_id = %s",
            (story_id, user['user_id']), fetch_one=True
        )
        
        if existing_like:
            return jsonify({'error': 'You have already liked this story'}), 409
        
        # Add like
        execute_query(
            "INSERT INTO story_likes (story_id, user_id) VALUES (%s, %s)",
            (story_id, user['user_id'])
        )
        
        # Update likes count
        execute_query(
            "UPDATE success_stories SET likes_count = likes_count + 1 WHERE story_id = %s",
            (story_id,)
        )
        
        # Get updated likes count
        updated_story = execute_query(
            "SELECT likes_count FROM success_stories WHERE story_id = %s",
            (story_id,), fetch_one=True
        )
        
        return jsonify({
            'message': 'Story liked successfully',
            'likes_count': updated_story['likes_count']
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to like story', 'details': str(e)}), 500

@stories_bp.route('/<int:story_id>/unlike', methods=['DELETE'])
@jwt_required_custom
def unlike_story(story_id):
    try:
        user = request.current_user
        
        # Check if like exists
        existing_like = execute_query(
            "SELECT like_id FROM story_likes WHERE story_id = %s AND user_id = %s",
            (story_id, user['user_id']), fetch_one=True
        )
        
        if not existing_like:
            return jsonify({'error': 'You have not liked this story'}), 404
        
        # Remove like
        execute_query(
            "DELETE FROM story_likes WHERE story_id = %s AND user_id = %s",
            (story_id, user['user_id'])
        )
        
        # Update likes count
        execute_query(
            "UPDATE success_stories SET likes_count = GREATEST(likes_count - 1, 0) WHERE story_id = %s",
            (story_id,)
        )
        
        # Get updated likes count
        updated_story = execute_query(
            "SELECT likes_count FROM success_stories WHERE story_id = %s",
            (story_id,), fetch_one=True
        )
        
        return jsonify({
            'message': 'Story unliked successfully',
            'likes_count': updated_story['likes_count']
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to unlike story', 'details': str(e)}), 500

@stories_bp.route('/my-stories', methods=['GET'])
@jwt_required_custom
def get_my_stories():
    try:
        user = request.current_user
        
        stories = execute_query("""
            SELECT s.*, 
                   (SELECT COUNT(*) FROM story_likes sl WHERE sl.story_id = s.story_id) as actual_likes_count
            FROM success_stories s
            WHERE s.author_id = %s
            ORDER BY s.created_at DESC
        """, (user['user_id'],))
        
        # Parse tags JSON
        for story in stories:
            if story['tags']:
                try:
                    story['tags'] = json.loads(story['tags'])
                except:
                    story['tags'] = []
        
        return jsonify({'stories': stories}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get your stories', 'details': str(e)}), 500

@stories_bp.route('/<int:story_id>', methods=['PUT'])
@jwt_required_custom
def update_story(story_id):
    try:
        user = request.current_user
        data = request.get_json()
        
        # Check if user owns this story
        story = execute_query(
            "SELECT author_id FROM success_stories WHERE story_id = %s",
            (story_id,), fetch_one=True
        )
        
        if not story:
            return jsonify({'error': 'Story not found'}), 404
        
        if story['author_id'] != user['user_id']:
            return jsonify({'error': 'You can only update your own stories'}), 403
        
        # Fields that can be updated
        updatable_fields = ['title', 'content', 'category', 'tags', 'is_published']
        
        update_data = {}
        for field in updatable_fields:
            if field in data:
                if field == 'tags':
                    if not isinstance(data[field], list):
                        return jsonify({'error': 'Tags must be a list'}), 400
                    update_data[field] = json.dumps(data[field])
                elif field == 'category':
                    valid_categories = ['job_placement', 'scholarship', 'career_change', 'skill_development', 'networking']
                    if data[field] not in valid_categories:
                        return jsonify({'error': f'Category must be one of: {", ".join(valid_categories)}'}), 400
                    update_data[field] = data[field]
                else:
                    update_data[field] = data[field]
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        # Build update query
        set_clause = ', '.join([f"{field} = %s" for field in update_data.keys()])
        values = list(update_data.values()) + [story_id]
        
        execute_query(
            f"UPDATE success_stories SET {set_clause} WHERE story_id = %s",
            values
        )
        
        return jsonify({'message': 'Story updated successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to update story', 'details': str(e)}), 500

@stories_bp.route('/categories', methods=['GET'])
def get_story_categories():
    try:
        categories = [
            {'value': 'job_placement', 'label': 'Job Placement'},
            {'value': 'scholarship', 'label': 'Scholarship'},
            {'value': 'career_change', 'label': 'Career Change'},
            {'value': 'skill_development', 'label': 'Skill Development'},
            {'value': 'networking', 'label': 'Networking'}
        ]
        
        return jsonify({'categories': categories}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get categories', 'details': str(e)}), 500