from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests
import time
from leetscrape import GetQuestion, GetQuestionsList

# Initialize Flask app
app = Flask(__name__)

# Configure CORS (allow requests from React frontend)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:5174"]
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
        test_cases = getattr(q, 'TestCases', getattr(q, 'testCases', getattr(q, 'examples', [])))
        
        # Add default test cases for two-sum if none exist
        if problem_slug == 'two-sum' and not test_cases:
            test_cases = [
                {
                    'input': 'nums = [2,7,11,15], target = 9',
                    'output': '[0, 1]',
                    'explanation': 'Because nums[0] + nums[1] == 9, we return [0, 1].'
                },
                {
                    'input': 'nums = [3,2,4], target = 6',
                    'output': '[1, 2]',
                    'explanation': 'Because nums[1] + nums[2] == 6, we return [1, 2].'
                },
                {
                    'input': 'nums = [3,3], target = 6',
                    'output': '[0, 1]',
                    'explanation': 'Because nums[0] + nums[1] == 6, we return [0, 1].'
                }
            ]
        
        problem_data = {
            'title': getattr(q, 'title', 'Unknown Title'),
            'difficulty': getattr(q, 'difficulty', 'Unknown'),
            'likes': getattr(q, 'likes', 0),
            'content': getattr(q, 'Body', getattr(q, 'content', 'No content available')),
            'codeSnippets': getattr(q, 'codeSnippets', []),
            'testCases': test_cases,
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

@app.route('/api/leetcode/execute', methods=['POST'])
def execute_code():
    """Execute code using Judge0 API and validate against test cases"""
    try:
        data = request.get_json()
        code = data.get('code', '')
        language_id = data.get('languageId', 71)  # Default to Python
        test_cases = data.get('testCases', [])

        if not code:
            return jsonify({
                'status': 'error',
                'message': 'No code provided'
            }), 400

        results = []
        all_passed = True
        code_output = ""

        for i, test_case in enumerate(test_cases):
            try:
                input_data = test_case.get('input', '')
                expected_output = test_case.get('output', '')

                # Create test code based on language
                if language_id == 71:  # Python
                    test_code = f"""
{code}

# Test the function
try:
    input_params = {parse_input_string(input_data)}
    result = solution(*input_params)
    print(str(result))
except Exception as e:
    print(f"Error: {{e}}")
"""
                elif language_id == 63:  # JavaScript
                    # Parse input for JavaScript
                    parsed_input = parse_input_string(input_data)
                    if isinstance(parsed_input, tuple):
                        test_code = f"""
{code}

// Test the function
try {{
    const result = solution({parsed_input[0]}, {parsed_input[1]});
    console.log(JSON.stringify(result));
}} catch (e) {{
    console.log(`Error: ${{e.message}}`);
}}
"""
                    else:
                        test_code = f"""
{code}

// Test the function
try {{
    const result = solution({parsed_input});
    console.log(JSON.stringify(result));
}} catch (e) {{
    console.log(`Error: ${{e.message}}`);
}}
"""
                else:
                    # For other languages, use a simple test
                    test_code = f"""
{code}

// Test output
print("Test case {i + 1} executed");
"""

                judge0_result = submit_to_judge0(test_code, language_id)

                if judge0_result['status'] == 'success':
                    actual_output = judge0_result['output'].strip()
                    passed = actual_output == expected_output
                    all_passed = all_passed and passed
                    
                    # Store the raw output for display
                    if i == 0:  # Only store output from first test case to avoid duplication
                        code_output = actual_output

                    results.append({
                        'testCase': i + 1,
                        'input': input_data,
                        'expectedOutput': expected_output,
                        'actualOutput': actual_output,
                        'passed': passed
                    })
                else:
                    error_msg = f'Judge0 Error: {judge0_result.get("error", "Unknown error")}'
                    if i == 0:  # Store error output for display
                        code_output = error_msg
                    
                    results.append({
                        'testCase': i + 1,
                        'input': input_data,
                        'expectedOutput': expected_output,
                        'actualOutput': error_msg,
                        'passed': False
                    })
                    all_passed = False

            except Exception as exec_error:
                results.append({
                    'testCase': i + 1,
                    'input': test_case.get('input', ''),
                    'expectedOutput': test_case.get('output', ''),
                    'actualOutput': f'Execution Error: {str(exec_error)}',
                    'passed': False
                })
                all_passed = False

        return jsonify({
            'status': 'success',
            'allPassed': all_passed,
            'results': results,
            'codeOutput': code_output,
            'message': 'All test cases passed!' if all_passed else 'Some test cases failed.'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

def submit_to_judge0(code, language_id=71):
    """Submit code to Judge0 API for execution"""
    try:
        # Judge0 API endpoint
        url = "https://ce.judge0.com/submissions"
        
        # Submit the code
        payload = {
            "source_code": code,
            "language_id": language_id,
            "stdin": "",
            "cpu_time_limit": "2.0",
            "memory_limit": 128000
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Submit code
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            submission_data = response.json()
            token = submission_data['token']
            
            # Wait for result
            result_url = f"https://ce.judge0.com/submissions/{token}"
            
            max_attempts = 10
            for attempt in range(max_attempts):
                time.sleep(1)  # Wait 1 second
                result_response = requests.get(result_url)
                
                if result_response.status_code == 200:
                    result_data = result_response.json()
                    
                    if result_data['status']['id'] <= 2:  # Still processing
                        continue
                    elif result_data['status']['id'] == 3:  # Accepted
                        return {
                            'status': 'success',
                            'output': result_data.get('stdout', '').strip(),
                            'error': result_data.get('stderr', '')
                        }
                    else:  # Error
                        return {
                            'status': 'error',
                            'error': result_data.get('stderr', '') or result_data['status']['description']
                        }
            
            return {
                'status': 'error',
                'error': 'Timeout waiting for execution result'
            }
        else:
            return {
                'status': 'error',
                'error': f'Failed to submit code: {response.status_code}'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'error': f'Judge0 API error: {str(e)}'
        }

def parse_input_string(input_str):
    """Parse input string like 'nums = [2,7,11,15], target = 9' into Python objects"""
    try:
        import re
        import ast
        
        # More sophisticated parsing to handle arrays with commas
        # Split by comma, but be careful about commas inside brackets
        parts = []
        current_part = ""
        bracket_depth = 0
        
        for char in input_str:
            if char == '[':
                bracket_depth += 1
            elif char == ']':
                bracket_depth -= 1
            elif char == ',' and bracket_depth == 0:
                parts.append(current_part.strip())
                current_part = ""
                continue
            current_part += char
        
        if current_part.strip():
            parts.append(current_part.strip())
        
        # Parse each part as a variable assignment
        values = []
        for part in parts:
            if '=' in part:
                var_name, var_value = part.split('=', 1)
                var_name = var_name.strip()
                var_value = var_value.strip()
                
                try:
                    # Try to evaluate as Python literal
                    value = ast.literal_eval(var_value)
                    values.append(value)
                except:
                    # Manual parsing for common cases
                    if var_value.startswith('[') and var_value.endswith(']'):
                        # Array parsing
                        content = var_value[1:-1]
                        if content:
                            items = [item.strip() for item in content.split(',')]
                            parsed_items = []
                            for item in items:
                                try:
                                    parsed_items.append(ast.literal_eval(item))
                                except:
                                    parsed_items.append(item)
                            values.append(parsed_items)
                        else:
                            values.append([])
                    elif var_value.startswith('"') and var_value.endswith('"'):
                        values.append(var_value[1:-1])
                    elif var_value.isdigit() or (var_value.startswith('-') and var_value[1:].isdigit()):
                        values.append(int(var_value))
                    else:
                        values.append(var_value)
            else:
                # Single value without assignment
                try:
                    values.append(ast.literal_eval(part))
                except:
                    values.append(part)
        
        return tuple(values) if len(values) > 1 else values[0] if values else None
        
    except Exception as e:
        return input_str

# ============== Run App ==============

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5002))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )