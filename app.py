from flask import Flask, jsonify
from flask_cors import CORS
import os
from leetscrape import GetQuestion, GetQuestionsList

# Initialize Flask app
app = Flask(__name__)

# Configure CORS (allow requests from React frontend)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173"]
    }
})

# Global cache for problems list
problems_cache = None

# ============== LeetCode API Routes ==============

@app.route('/api/leetcode/<problem_slug>', methods=['GET'])
def get_leetcode_problem(problem_slug):
    """Fetch LeetCode problem data by slug from real LeetCode API"""
    try:
        # Fetch the question data from LeetCode
        q = GetQuestion(titleSlug=problem_slug).scrape()
        
        # Extract problem data
        problem_data = {
            'title': getattr(q, 'title', 'Unknown Title'),
            'difficulty': getattr(q, 'difficulty', 'Unknown'),
            'likes': getattr(q, 'likes', 0),
            'content': getattr(q, 'Body', getattr(q, 'content', 'No content available')),
            'codeSnippets': getattr(q, 'codeSnippets', []),
            'testCases': getattr(q, 'TestCases', getattr(q, 'testCases', getattr(q, 'examples', []))),
            'hints': getattr(q, 'Hints', []),
            'topicTags': getattr(q, 'topicTags', []),
            'isPaidOnly': getattr(q, 'isPaidOnly', False)
        }
        
        return jsonify({
            'status': 'success',
            'data': problem_data
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch problem "{problem_slug}": {str(e)}'
        }), 500

@app.route('/api/leetcode/two-sum', methods=['GET'])
def get_two_sum():
    """Get Two Sum problem specifically"""
    return get_leetcode_problem('two-sum')

@app.route('/api/leetcode/problems', methods=['GET'])
def get_available_problems():
    """Get list of available LeetCode problems using leetscrape"""
    global problems_cache
    
    try:
        # Use cache if available, otherwise fetch from leetscrape
        if problems_cache is None:
            print("Fetching problems list from LeetCode...")
            ls = GetQuestionsList()
            ls.scrape()  # Scrape the list of questions
            
            # Convert to the format expected by frontend
            problems = []
            for _, row in ls.questions.iterrows():
                problems.append({
                    'slug': row['titleSlug'],
                    'title': row['title'],
                    'difficulty': row['difficulty'],
                    'acceptanceRate': row.get('acceptanceRate', 0),
                    'paidOnly': row.get('paidOnly', False),
                    'topicTags': row.get('topicTags', []),
                    'qid': row.get('QID', 0)
                })
            
            # Cache the results
            problems_cache = problems
            print(f"Successfully fetched {len(problems)} problems from LeetCode")
        else:
            print("Using cached problems list")
        
        return jsonify({
            'status': 'success',
            'data': problems_cache
        })
        
    except Exception as e:
        print(f"Error fetching problems: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch problems list: {str(e)}'
        }), 500

# ============== Run App ==============

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )