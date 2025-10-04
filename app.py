from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configure CORS (allow requests from React frontend)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"]
    }
})

# Configuration
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'True') == 'True'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# ============== Routes ==============

@app.route('/')
def home():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Flask API is running',
        'version': '1.0.0'
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """API health check"""
    return jsonify({
        'status': 'healthy',
        'service': 'flask-api'
    })

@app.route('/api/example', methods=['GET'])
def get_example():
    """Example GET endpoint"""
    return jsonify({
        'message': 'This is an example GET request',
        'data': [1, 2, 3, 4, 5]
    })

@app.route('/api/example', methods=['POST'])
def post_example():
    """Example POST endpoint"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    return jsonify({
        'message': 'Data received successfully',
        'received': data
    }), 201

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Example route with URL parameter"""
    # Mock user data
    users = {
        1: {'id': 1, 'name': 'Alice', 'email': 'alice@example.com'},
        2: {'id': 2, 'name': 'Bob', 'email': 'bob@example.com'},
    }
    
    user = users.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user)

# ============== Error Handlers ==============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Not found',
        'message': 'The requested resource was not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on the server'
    }), 500

# ============== Run App ==============

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )