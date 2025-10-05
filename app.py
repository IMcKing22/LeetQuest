from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests
import time
from uuid import uuid4

from responses_api.build import start_story
from responses_api.bridge import path_bridge, description_former_bridge, description_latter_bridge, journey_bridge
#from leetscrape import GetQuestion, GetQuestionsList

def get_problem_signature(problem_slug, language):
    """Get proper function signature for each problem"""
    signatures = {
        'two-sum': {
            'python': 'def solution(nums: List[int], target: int) -> List[int]:',
            'javascript': 'function solution(nums, target) {',
            'java': 'public int[] solution(int[] nums, int target) {',
            'cpp': 'vector<int> solution(vector<int>& nums, int target) {',
            'c': 'int* solution(int* nums, int numsSize, int target, int* returnSize) {'
        },
        'container-with-most-water': {
            'python': 'def solution(height: List[int]) -> int:',
            'javascript': 'function solution(height) {',
            'java': 'public int solution(int[] height) {',
            'cpp': 'int solution(vector<int>& height) {',
            'c': 'int solution(int* height, int heightSize) {'
        },
        'longest-substring-without-repeating-characters': {
            'python': 'def solution(s: str) -> int:',
            'javascript': 'function solution(s) {',
            'java': 'public int solution(String s) {',
            'cpp': 'int solution(string s) {',
            'c': 'int solution(char* s) {'
        },
        'valid-parentheses': {
            'python': 'def solution(s: str) -> bool:',
            'javascript': 'function solution(s) {',
            'java': 'public boolean solution(String s) {',
            'cpp': 'bool solution(string s) {',
            'c': 'bool solution(char* s) {'
        },
        'binary-search': {
            'python': 'def solution(nums: List[int], target: int) -> int:',
            'javascript': 'function solution(nums, target) {',
            'java': 'public int solution(int[] nums, int target) {',
            'cpp': 'int solution(vector<int>& nums, int target) {',
            'c': 'int solution(int* nums, int numsSize, int target) {'
        },
        'add-two-numbers': {
            'python': 'def solution(l1: Optional[ListNode], l2: Optional[ListNode]) -> Optional[ListNode]:',
            'javascript': 'function solution(l1, l2) {',
            'java': 'public ListNode solution(ListNode l1, ListNode l2) {',
            'cpp': 'ListNode* solution(ListNode* l1, ListNode* l2) {',
            'c': 'struct ListNode* solution(struct ListNode* l1, struct ListNode* l2) {'
        },
        'binary-tree-inorder-traversal': {
            'python': 'def solution(root: Optional[TreeNode]) -> List[int]:',
            'javascript': 'function solution(root) {',
            'java': 'public List<Integer> solution(TreeNode root) {',
            'cpp': 'vector<int> solution(TreeNode* root) {',
            'c': 'int* solution(struct TreeNode* root, int* returnSize) {'
        },
        'kth-largest-element-in-an-array': {
            'python': 'def solution(nums: List[int], k: int) -> int:',
            'javascript': 'function solution(nums, k) {',
            'java': 'public int solution(int[] nums, int k) {',
            'cpp': 'int solution(vector<int>& nums, int k) {',
            'c': 'int solution(int* nums, int numsSize, int k) {'
        },
        'letter-combinations-of-a-phone-number': {
            'python': 'def solution(digits: str) -> List[str]:',
            'javascript': 'function solution(digits) {',
            'java': 'public List<String> solution(String digits) {',
            'cpp': 'vector<string> solution(string digits) {',
            'c': 'char** solution(char* digits, int* returnSize) {'
        },
        'number-of-islands': {
            'python': 'def solution(grid: List[List[str]]) -> int:',
            'javascript': 'function solution(grid) {',
            'java': 'public int solution(char[][] grid) {',
            'cpp': 'int solution(vector<vector<char>>& grid) {',
            'c': 'int solution(char** grid, int gridSize, int* gridColSize) {'
        },
        'climbing-stairs': {
            'python': 'def solution(n: int) -> int:',
            'javascript': 'function solution(n) {',
            'java': 'public int solution(int n) {',
            'cpp': 'int solution(int n) {',
            'c': 'int solution(int n) {'
        },
        'unique-paths': {
            'python': 'def solution(m: int, n: int) -> int:',
            'javascript': 'function solution(m, n) {',
            'java': 'public int solution(int m, int n) {',
            'cpp': 'int solution(int m, int n) {',
            'c': 'int solution(int m, int n) {'
        },
        'jump-game': {
            'python': 'def solution(nums: List[int]) -> bool:',
            'javascript': 'function solution(nums) {',
            'java': 'public boolean solution(int[] nums) {',
            'cpp': 'bool solution(vector<int>& nums) {',
            'c': 'bool solution(int* nums, int numsSize) {'
        },
        'merge-intervals': {
            'python': 'def solution(intervals: List[List[int]]) -> List[List[int]]:',
            'javascript': 'function solution(intervals) {',
            'java': 'public int[][] solution(int[][] intervals) {',
            'cpp': 'vector<vector<int>> solution(vector<vector<int>>& intervals) {',
            'c': 'int** solution(int** intervals, int intervalsSize, int* intervalsColSize, int* returnSize, int** returnColumnSizes) {'
        },
        'rotate-image': {
            'python': 'def solution(matrix: List[List[int]]) -> None:',
            'javascript': 'function solution(matrix) {',
            'java': 'public void solution(int[][] matrix) {',
            'cpp': 'void solution(vector<vector<int>>& matrix) {',
            'c': 'void solution(int** matrix, int matrixSize, int* matrixColSize) {'
        }
    }
    
    return signatures.get(problem_slug, {}).get(language, 'def solution():')

def get_default_test_cases(problem_slug):
    """Generate default test cases for common LeetCode problems"""
    test_cases_map = {
        'two-sum': [
            {'input': 'nums = [2,7,11,15], target = 9', 'output': '[0, 1]', 'explanation': 'Because nums[0] + nums[1] == 9, we return [0, 1].'},
            {'input': 'nums = [3,2,4], target = 6', 'output': '[1, 2]', 'explanation': 'Because nums[1] + nums[2] == 6, we return [1, 2].'},
            {'input': 'nums = [3,3], target = 6', 'output': '[0, 1]', 'explanation': 'Because nums[0] + nums[1] == 6, we return [0, 1].'}
        ],
        'container-with-most-water': [
            {'input': 'height = [1,8,6,2,5,4,8,3,7]', 'output': '49', 'explanation': 'The above vertical lines are represented by array [1,8,6,2,5,4,8,3,7]. In this case, the max area of water (blue section) the container can contain is 49.'},
            {'input': 'height = [1,1]', 'output': '1', 'explanation': 'The minimum height is 1, so the area is 1 * 1 = 1.'}
        ],
        'longest-substring-without-repeating-characters': [
            {'input': 's = "abcabcbb"', 'output': '3', 'explanation': 'The answer is "abc", with the length of 3.'},
            {'input': 's = "bbbbb"', 'output': '1', 'explanation': 'The answer is "b", with the length of 1.'},
            {'input': 's = "pwwkew"', 'output': '3', 'explanation': 'The answer is "wke", with the length of 3.'}
        ],
        'valid-parentheses': [
            {'input': 's = "()"', 'output': 'true', 'explanation': 'The string contains valid parentheses.'},
            {'input': 's = "()[]{}"', 'output': 'true', 'explanation': 'The string contains valid parentheses.'},
            {'input': 's = "(]"', 'output': 'false', 'explanation': 'The string contains invalid parentheses.'}
        ],
        'binary-search': [
            {'input': 'nums = [-1,0,3,5,9,12], target = 9', 'output': '4', 'explanation': '9 exists in nums and its index is 4'},
            {'input': 'nums = [-1,0,3,5,9,12], target = 2', 'output': '-1', 'explanation': '2 does not exist in nums so return -1'}
        ],
        'add-two-numbers': [
            {'input': 'l1 = [2,4,3], l2 = [5,6,4]', 'output': '[7,0,8]', 'explanation': '342 + 465 = 807'},
            {'input': 'l1 = [0], l2 = [0]', 'output': '[0]', 'explanation': '0 + 0 = 0'}
        ],
        'binary-tree-inorder-traversal': [
            {'input': 'root = [1,null,2,3]', 'output': '[1,3,2]', 'explanation': 'Inorder traversal of the binary tree.'},
            {'input': 'root = []', 'output': '[]', 'explanation': 'Empty tree has no nodes.'}
        ],
        'kth-largest-element-in-an-array': [
            {'input': 'nums = [3,2,1,5,6,4], k = 2', 'output': '5', 'explanation': 'The 2nd largest element is 5.'},
            {'input': 'nums = [3,2,3,1,2,4,5,5,6], k = 4', 'output': '4', 'explanation': 'The 4th largest element is 4.'}
        ],
        'letter-combinations-of-a-phone-number': [
            {'input': 'digits = "23"', 'output': '["ad","ae","af","bd","be","bf","cd","ce","cf"]', 'explanation': 'All possible letter combinations for "23".'},
            {'input': 'digits = ""', 'output': '[]', 'explanation': 'No digits provided.'}
        ],
        'implement-trie-prefix-tree': [
            {'input': 'operations = ["Trie","insert","search","search","startsWith","insert","search"]\nvalues = [[],"apple","apple","app","app","app","app"]', 'output': '[null,null,true,false,true,null,true]', 'explanation': 'Trie operations demonstration.'}
        ],
        'number-of-islands': [
            {'input': 'grid = [["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]', 'output': '1', 'explanation': 'There is one island in the grid.'},
            {'input': 'grid = [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]', 'output': '3', 'explanation': 'There are three islands in the grid.'}
        ],
        'course-schedule': [
            {'input': 'numCourses = 2, prerequisites = [[1,0]]', 'output': 'true', 'explanation': 'You can finish course 1 after course 0.'},
            {'input': 'numCourses = 2, prerequisites = [[1,0],[0,1]]', 'output': 'false', 'explanation': 'There is a cycle in the prerequisites.'}
        ],
        'climbing-stairs': [
            {'input': 'n = 2', 'output': '2', 'explanation': 'There are two ways to climb to the top: 1. 1 step + 1 step, 2. 2 steps'},
            {'input': 'n = 3', 'output': '3', 'explanation': 'There are three ways to climb to the top: 1. 1 step + 1 step + 1 step, 2. 1 step + 2 steps, 3. 2 steps + 1 step'}
        ],
        'unique-paths': [
            {'input': 'm = 3, n = 7', 'output': '28', 'explanation': 'There are 28 unique paths from top-left to bottom-right.'},
            {'input': 'm = 3, n = 2', 'output': '3', 'explanation': 'There are 3 unique paths from top-left to bottom-right.'}
        ],
        'jump-game': [
            {'input': 'nums = [2,3,1,1,4]', 'output': 'true', 'explanation': 'You can reach the last index by jumping 1 step from index 0 to 1, then 3 steps to the last index.'},
            {'input': 'nums = [3,2,1,0,4]', 'output': 'false', 'explanation': 'You will always arrive at index 3 no matter what. Its maximum jump length is 0, which makes it impossible to reach the last index.'}
        ],
        'merge-intervals': [
            {'input': 'intervals = [[1,3],[2,6],[8,10],[15,18]]', 'output': '[[1,6],[8,10],[15,18]]', 'explanation': 'Since intervals [1,3] and [2,6] overlap, merge them into [1,6].'},
            {'input': 'intervals = [[1,4],[4,5]]', 'output': '[[1,5]]', 'explanation': 'Intervals [1,4] and [4,5] are considered overlapping.'}
        ],
        'rotate-image': [
            {'input': 'matrix = [[1,2,3],[4,5,6],[7,8,9]]', 'output': '[[7,4,1],[8,5,2],[9,6,3]]', 'explanation': 'The matrix is rotated 90 degrees clockwise.'},
            {'input': 'matrix = [[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]]', 'output': '[[15,13,2,5],[14,3,4,1],[12,6,8,9],[16,7,10,11]]', 'explanation': 'The matrix is rotated 90 degrees clockwise.'}
        ]
    }
    
    return test_cases_map.get(problem_slug, [
        {'input': 'input = [1, 2, 3]', 'output': 'output', 'explanation': 'Default test case for this problem.'}
    ])

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

SESSIONS = {} # temp session memory store
# ============= AI Integration Routes =============
@app.post("/api/start")
def api_start():
    topic = (request.get_json(silent=True) or {}).get("topic", "coding challenges")
    res = start_story(topic, generate_art=False)

    sid = str(uuid4())
    SESSIONS[sid] = {
        "topic": topic,
        "base_text": res["story_text"],
        "conversation_id": res.get("conversation_id"),
        "response_id": res.get("response_id"),
    }

    return jsonify({
        "sessionId": sid,
        "conversationId": res.get("conversation_id"),
        "responseId": res.get("response_id"),
        "story": res["story_text"],
    })

@app.post("/api/choices")
def api_choices():
    j = request.get_json(silent=True) or {}
    sess = SESSIONS.get(j.get("sessionId"))
    if not sess:
        return jsonify({"error": "session not found"}), 404
    base = sess["base_text"]; topic = sess["topic"]
    former_title = path_bridge(f"{topic} approach A").strip()
    latter_title = path_bridge(f"{topic} approach B").strip()
    former_desc  = description_former_bridge(base).strip()
    latter_desc  = description_latter_bridge(base).strip()
    journey      = journey_bridge(base).strip()
    return jsonify({"journey": journey, "former": {"title": former_title, "description": former_desc},
                    "latter": {"title": latter_title, "description": latter_desc}})

# example continue route
@app.post("/api/continue")
def api_continue():
    j = request.get_json(silent=True) or {}
    sid = j.get("sessionId")
    user_input = j.get("input", "Continue.")
    sess = SESSIONS.get(sid)
    if not sess:
        return jsonify({"error":"session not found"}), 404

    from responses_api.build import continue_story
    out = continue_story(
        conversation_id=sess.get("conversation_id"),
        response_id=sess.get("response_id"),
        user_input=user_input
    )
    # update stored ids for next turn
    sess["conversation_id"] = out.get("conversation_id") or sess.get("conversation_id")
    sess["response_id"] = out.get("response_id") or sess.get("response_id")
    return jsonify(out)

# ============== LeetCode API Routes ==============

@app.route('/api/leetcode/<problem_slug>', methods=['GET'])
def get_leetcode_problem(problem_slug):
    """Fetch LeetCode problem data by slug from real LeetCode API"""
    try:
        # Fetch the question data from LeetCode
        q = GetQuestion(titleSlug=problem_slug).scrape()
        
        # Extract problem data
        test_cases = getattr(q, 'TestCases', getattr(q, 'testCases', getattr(q, 'examples', [])))
        
        # Add default test cases for common problems if none exist
        if not test_cases:
            test_cases = get_default_test_cases(problem_slug)
        
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
                    parsed_input = parse_input_string(input_data)
                    if isinstance(parsed_input, tuple):
                        test_code = f"""
{code}

# Test the function
try:
    input_params = {parsed_input}
    result = solution(*input_params)
    print(str(result))
except Exception as e:
    print(f"Error: {{e}}")
"""
                    else:
                        # Handle string inputs properly
                        if isinstance(parsed_input, str):
                            test_code = f"""
{code}

# Test the function
try:
    input_param = {repr(parsed_input)}
    result = solution(input_param)
    print(str(result))
except Exception as e:
    print(f"Error: {{e}}")
"""
                        else:
                            test_code = f"""
{code}

# Test the function
try:
    input_param = {parsed_input}
    result = solution(input_param)
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
                    
                    # Normalize outputs for comparison (True -> true, False -> false)
                    normalized_actual = normalize_output(actual_output)
                    normalized_expected = normalize_output(expected_output)
                    
                    passed = normalized_actual == normalized_expected
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

def normalize_output(output):
    """Normalize output for comparison (e.g., True -> true, False -> false)"""
    if output == "True":
        return "true"
    elif output == "False":
        return "false"
    elif output == "None":
        return "null"
    return output

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