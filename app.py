from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import requests
import time
import pandas as pd
from uuid import uuid4

from responses_api.build import start_story
from responses_api.bridge import path_bridge, description_former_bridge, description_latter_bridge, journey_bridge
try:
    from leetscrape import GetQuestion, GetQuestionsList  # Optional: may not be installed
except Exception:
    GetQuestion = None
    GetQuestionsList = None

# Load LeetCode data from CSV files
def load_leetcode_data():
    """Load LeetCode problems from CSV files"""
    try:
        # Load the augmented data which has the most complete information
        df = pd.read_csv('responses_api/leetcode_resources/Augmented_LeetCode_Questions.csv')
        return df
    except Exception as e:
        print(f"Error loading LeetCode data: {e}")
        return None

# Global variable to store the data
leetcode_data = load_leetcode_data()

def get_problem_by_slug(slug):
    """Get problem data by slug from CSV"""
    if leetcode_data is None:
        return None
    
    problem = leetcode_data[leetcode_data['titleSlug'] == slug]
    if problem.empty:
        return None
    
    return problem.iloc[0].to_dict()

def get_problems_by_difficulty(difficulty):
    """Get all problems of a specific difficulty"""
    if leetcode_data is None:
        return []
    
    problems = leetcode_data[leetcode_data['difficulty'] == difficulty.lower()]
    return problems.to_dict('records')

def get_problems_by_topic(topic):
    """Get problems by topic/genre"""
    if leetcode_data is None:
        return []
    
    # Map topic names to CSV topic column - use the actual topics from CSV
    topic_mapping = {
        'Arrays & Hashing': 'arrays',
        'Two Pointers': 'arrays',  # Map to arrays since two_pointers doesn't exist
        'Sliding Window': 'sliding_window',
        'Stack': 'arrays',  # Map to arrays since stack doesn't exist
        'Binary Search': 'binary_search',
        'Linked List': 'linked_list',
        'Trees': 'tree',
        'Heap / Priority Queue': 'heap',
        'Backtracking': 'arrays',  # Map to arrays since backtracking doesn't exist
        'Tries': 'tree',  # Map to tree since tries doesn't exist
        'Graphs': 'graph',
        'Advanced Graphs': 'graph',
        '1-D Dynamic Programming': 'dp',
        '2-D Dynamic Programming': 'dp',
        'Greedy': 'arrays',  # Map to arrays since greedy doesn't exist
        'Intervals': 'arrays',  # Map to arrays since intervals doesn't exist
        'Math & Geometry': 'math'
    }
    
    csv_topic = topic_mapping.get(topic, topic.lower())
    problems = leetcode_data[leetcode_data['topic'] == csv_topic]
    
    # If no problems found for the specific topic, try to get problems with known difficulties
    if problems.empty:
        # Get problems with known difficulties (not "unknown")
        problems = leetcode_data[leetcode_data['difficulty'] != 'unknown']
        # Filter by tags if available
        if topic == 'Arrays & Hashing':
            problems = problems[problems['tags'].str.contains('arrays|hashmap', case=False, na=False)]
        elif topic == 'Linked List':
            problems = problems[problems['tags'].str.contains('linked_list', case=False, na=False)]
        elif topic == 'Trees':
            problems = problems[problems['tags'].str.contains('tree', case=False, na=False)]
        elif topic == 'Graphs':
            problems = problems[problems['tags'].str.contains('graph', case=False, na=False)]
        elif topic == 'Binary Search':
            problems = problems[problems['tags'].str.contains('binary_search', case=False, na=False)]
        elif topic == 'Sliding Window':
            problems = problems[problems['tags'].str.contains('sliding_window', case=False, na=False)]
        elif topic == 'Strings':
            problems = problems[problems['tags'].str.contains('string', case=False, na=False)]
    
    # If still no problems, get any problems with known difficulties
    if problems.empty:
        problems = leetcode_data[leetcode_data['difficulty'] != 'unknown']
    
    # Filter out problems with unknown difficulty
    problems = problems[problems['difficulty'] != 'unknown']
    
    # Sort by difficulty: easy first, then medium, then hard
    difficulty_order = {'easy': 0, 'medium': 1, 'hard': 2}
    problems = problems.sort_values(by='difficulty', key=lambda x: x.map(difficulty_order))
    
    return problems.to_dict('records')

def get_problem_signature(problem_slug, language):
    """Get proper function signature for each problem"""
    signatures = {
        'two-sum': {
            'python': 'def solution(nums):',
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
        'remove-duplicates-from-sorted-array': {
            'python': 'def solution(nums: List[int]) -> int:',
            'javascript': 'function solution(nums) {',
            'java': 'public int solution(int[] nums) {',
            'cpp': 'int solution(vector<int>& nums) {',
            'c': 'int solution(int* nums, int numsSize) {'
        },
        'linked-list-cycle': {
            'python': 'def solution(head: Optional[ListNode]) -> bool:',
            'javascript': 'function solution(head) {',
            'java': 'public boolean solution(ListNode head) {',
            'cpp': 'bool solution(ListNode *head) {',
            'c': 'bool solution(struct ListNode *head) {'
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

def get_default_problem_data(problem_slug):
    """Generate default problem data for common LeetCode problems"""
    problems_map = {
        'two-sum': {
            'title': 'Two Sum',
            'difficulty': 'Easy',
            'content': '''<p>Given an array of integers <code>nums</code> and an integer <code>target</code>, return <em>indices of the two numbers such that they add up to</em> <code>target</code>.</p>

<p>You may assume that each input would have <strong>exactly one solution</strong>, and you may not use the same element twice.</p>

<p>You can return the answer in any order.</p>

<p>&nbsp;</p>
<p><strong>Example 1:</strong></p>
<pre><strong>Input:</strong> nums = [2,7,11,15], target = 9
<strong>Output:</strong> [0,1]
<strong>Explanation:</strong> Because nums[0] + nums[1] == 9, we return [0, 1].
</pre>

<p><strong>Example 2:</strong></p>
<pre><strong>Input:</strong> nums = [3,2,4], target = 6
<strong>Output:</strong> [1,2]
</pre>

<p><strong>Example 3:</strong></p>
<pre><strong>Input:</strong> nums = [3,3], target = 6
<strong>Output:</strong> [0,1]
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>
<ul>
	<li><code>2 &lt;= nums.length &lt;= 10<sup>4</sup></code></li>
	<li><code>-10<sup>9</sup> &lt;= nums[i] &lt;= 10<sup>9</sup></code></li>
	<li><code>-10<sup>9</sup> &lt;= target &lt;= 10<sup>9</sup></code></li>
	<li><strong>Only one valid answer exists.</strong></li>
</ul>''',
            'testCases': [
                {'input': 'nums = [2,7,11,15], target = 9', 'output': '[0, 1]', 'explanation': 'Because nums[0] + nums[1] == 9, we return [0, 1].'},
                {'input': 'nums = [3,2,4], target = 6', 'output': '[1, 2]', 'explanation': 'Because nums[1] + nums[2] == 6, we return [1, 2].'},
                {'input': 'nums = [3,3], target = 6', 'output': '[0, 1]', 'explanation': 'Because nums[0] + nums[1] == 6, we return [0, 1].'}
            ]
        },
        'container-with-most-water': {
            'title': 'Container With Most Water',
            'difficulty': 'Medium',
            'content': '''<p>You are given an integer array <code>height</code> of length <code>n</code>. There are <code>n</code> vertical lines drawn such that the two endpoints of the <code>i<sup>th</sup></code> line are <code>(i, 0)</code> and <code>(i, height[i])</code>.</p>

<p>Find two lines that together with the x-axis form a container, such that the container contains the most water.</p>

<p>Return <em>the maximum amount of water a container can store</em>.</p>

<p><strong>Notice</strong> that you may not slant the container.</p>

<p>&nbsp;</p>
<p><strong>Example 1:</strong></p>
<img alt="" src="https://s3-lc-upload.s3.amazonaws.com/uploads/2018/07/17/question_11.jpg" style="width: 600px; height: 287px;" />
<pre><strong>Input:</strong> height = [1,8,6,2,5,4,8,3,7]
<strong>Output:</strong> 49
<strong>Explanation:</strong> The above vertical lines are represented by array [1,8,6,2,5,4,8,3,7]. In this case, the max area of water (blue section) the container can contain is 49.
</pre>

<p><strong>Example 2:</strong></p>
<pre><strong>Input:</strong> height = [1,1]
<strong>Output:</strong> 1
</pre>

<p>&nbsp;</p>
<p><strong>Constraints:</strong></p>
<ul>
	<li><code>n == height.length</code></li>
	<li><code>2 &lt;= n &lt;= 10<sup>5</sup></code></li>
	<li><code>0 &lt;= height[i] &lt;= 10<sup>4</sup></code></li>
</ul>''',
            'testCases': [
                {'input': 'height = [1,8,6,2,5,4,8,3,7]', 'output': '49', 'explanation': 'The above vertical lines are represented by array [1,8,6,2,5,4,8,3,7]. In this case, the max area of water (blue section) the container can contain is 49.'},
                {'input': 'height = [1,1]', 'output': '1', 'explanation': 'The minimum height is 1, so the area is 1 * 1 = 1.'}
            ]
        }
    }
    
    # Return the problem data if it exists, otherwise return a default
    if problem_slug in problems_map:
        return problems_map[problem_slug]
    else:
        return {
            'title': 'Sample Problem',
            'difficulty': 'Easy',
            'content': '<p>This is a sample problem. The actual problem data is not available.</p>',
            'testCases': [
                {'input': 'input = [1, 2, 3]', 'output': 'output', 'explanation': 'Default test case for this problem.'}
            ]
        }

def get_default_test_cases(problem_slug, problem_title=None):
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
        'remove-duplicates-from-sorted-array': [
            {'input': 'nums = [1,1,2]', 'output': '2', 'explanation': 'Your function should return length = 2, with the first two elements of nums being 1 and 2 respectively.'},
            {'input': 'nums = [0,0,1,1,1,2,2,3,3,4]', 'output': '5', 'explanation': 'Your function should return length = 5, with the first five elements of nums being modified to 0, 1, 2, 3, and 4 respectively.'}
        ],
        'linked-list-cycle': [
            {'input': 'head = [3,2,0,-4], pos = 1', 'output': 'true', 'explanation': 'There is a cycle in the linked list, where the tail connects to the 1st node (0-indexed).'},
            {'input': 'head = [1,2], pos = 0', 'output': 'true', 'explanation': 'There is a cycle in the linked list, where the tail connects to the 0th node.'},
            {'input': 'head = [1], pos = -1', 'output': 'false', 'explanation': 'There is no cycle in the linked list.'}
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
        ],
        'maximum-subarray': [
            {'input': 'nums = [-2,1,-3,4,-1,2,1,-5,4]', 'output': '6', 'explanation': 'The subarray [4,-1,2,1] has the largest sum = 6.'},
            {'input': 'nums = [1]', 'output': '1', 'explanation': 'The array has only one element, so the maximum sum is 1.'},
            {'input': 'nums = [5,4,-1,7,8]', 'output': '23', 'explanation': 'The entire array has the largest sum = 23.'}
        ],
        'best-time-to-buy-and-sell-stock': [
            {'input': 'prices = [7,1,5,3,6,4]', 'output': '5', 'explanation': 'Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.'},
            {'input': 'prices = [7,6,4,3,1]', 'output': '0', 'explanation': 'In this case, no transactions are done and the max profit = 0.'}
        ],
        'house-robber': [
            {'input': 'nums = [1,2,3,1]', 'output': '4', 'explanation': 'Rob house 1 (money = 1) and then rob house 3 (money = 3). Total amount you can rob = 1 + 3 = 4.'},
            {'input': 'nums = [2,7,9,3,1]', 'output': '12', 'explanation': 'Rob house 1 (money = 2), rob house 3 (money = 9) and rob house 5 (money = 1). Total amount you can rob = 2 + 9 + 1 = 12.'}
        ],
        'longest-palindromic-substring': [
            {'input': 's = "babad"', 'output': '"bab"', 'explanation': '"aba" is also a valid answer.'},
            {'input': 's = "cbbd"', 'output': '"bb"', 'explanation': 'The longest palindromic substring is "bb".'}
        ],
        'merge-two-sorted-lists': [
            {'input': 'list1 = [1,2,4], list2 = [1,3,4]', 'output': '[1,1,2,3,4,4]', 'explanation': 'Merged list contains all elements from both lists in sorted order.'},
            {'input': 'list1 = [], list2 = []', 'output': '[]', 'explanation': 'Both lists are empty, so the result is empty.'},
            {'input': 'list1 = [], list2 = [0]', 'output': '[0]', 'explanation': 'One list is empty, so the result is the other list.'}
        ]
    }
    
    # Try to find by slug first
    if problem_slug in test_cases_map:
        return test_cases_map[problem_slug]
    
    # Try to find by title keywords if title is provided
    if problem_title:
        title_lower = problem_title.lower()
        for slug, test_cases in test_cases_map.items():
            # Check if any keywords from the slug appear in the title
            keywords = slug.split('-')
            if any(keyword in title_lower for keyword in keywords):
                return test_cases
    
    # Generate generic test cases based on common patterns
    if problem_title:
        title_lower = problem_title.lower()
        if 'sum' in title_lower and 'two' in title_lower:
            return test_cases_map['two-sum']
        elif 'container' in title_lower or 'water' in title_lower:
            return test_cases_map['container-with-most-water']
        elif 'parentheses' in title_lower or 'valid' in title_lower:
            return test_cases_map['valid-parentheses']
        elif 'merge' in title_lower and 'list' in title_lower:
            return test_cases_map['merge-two-sorted-lists']
        elif 'maximum' in title_lower and 'subarray' in title_lower:
            return test_cases_map['maximum-subarray']
        elif 'stock' in title_lower or 'buy' in title_lower:
            return test_cases_map['best-time-to-buy-and-sell-stock']
        elif 'stairs' in title_lower or 'climbing' in title_lower:
            return test_cases_map['climbing-stairs']
        elif 'robber' in title_lower or 'house' in title_lower:
            return test_cases_map['house-robber']
        elif 'substring' in title_lower and 'repeating' in title_lower:
            return test_cases_map['longest-substring-without-repeating-characters']
        elif 'palindromic' in title_lower or 'palindrome' in title_lower:
            return test_cases_map['longest-palindromic-substring']
    
    # Default fallback
    return [
        {'input': 'input = [1, 2, 3]', 'output': '[1, 2, 3]', 'explanation': 'Default test case for this problem.'}
    ]

# Initialize Flask app
app = Flask(__name__)

# Configure CORS (allow requests from React frontend)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
            "http://127.0.0.1:5176"
        ]
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
    topic = j.get("topic", "Arrays & Hashing")
    choice = j.get("choice", "path1")
    
    # Generate creative path titles and descriptions
    if choice == "path1":
        former_title = path_bridge(f"{topic} approach A").strip()
        former_desc = description_former_bridge(f"{topic} systematic approach").strip()
        return jsonify({
            "path1Title": former_title,
            "path1Description": former_desc,
        })
    else:
        latter_title = path_bridge(f"{topic} approach B").strip()
        latter_desc = description_latter_bridge(f"{topic} creative approach").strip()
        return jsonify({
            "path2Title": latter_title,
            "path2Description": latter_desc,
        })

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

@app.post("/api/story/easy-completion")
def api_story_easy_completion():
    """Generate story continuation after completing Easy problems"""
    j = request.get_json(silent=True) or {}
    conversation_id = j.get("conversationId")
    response_id = j.get("responseId")
    previous_story = j.get("previousStory", "")
    
    from responses_api.build import continue_story_easy_completion
    res = continue_story_easy_completion(
        conversation_id=conversation_id,
        response_id=response_id,
        previous_story=previous_story
    )
    
    return jsonify({
        "story": res["story_text"],
        "conversationId": res.get("conversation_id"),
        "responseId": res.get("response_id"),
    })

@app.post("/api/story/medium-completion")
def api_story_medium_completion():
    """Generate story continuation after completing Medium problems"""
    j = request.get_json(silent=True) or {}
    conversation_id = j.get("conversationId")
    response_id = j.get("responseId")
    previous_story = j.get("previousStory", "")
    
    from responses_api.build import continue_story_medium_completion
    res = continue_story_medium_completion(
        conversation_id=conversation_id,
        response_id=response_id,
        previous_story=previous_story
    )
    
    return jsonify({
        "story": res["story_text"],
        "conversationId": res.get("conversation_id"),
        "responseId": res.get("response_id"),
    })

@app.post("/api/story/hard-completion")
def api_story_hard_completion():
    """Generate story conclusion after completing Hard problems"""
    j = request.get_json(silent=True) or {}
    conversation_id = j.get("conversationId")
    response_id = j.get("responseId")
    previous_story = j.get("previousStory", "")
    
    from responses_api.build import continue_story_hard_completion
    res = continue_story_hard_completion(
        conversation_id=conversation_id,
        response_id=response_id,
        previous_story=previous_story
    )
    
    return jsonify({
        "story": res["story_text"],
        "conversationId": res.get("conversation_id"),
        "responseId": res.get("response_id"),
    })
# ============== LeetCode API Routes ==============

@app.route('/api/leetcode/<problem_slug>', methods=['GET'])
def get_leetcode_problem(problem_slug):
    """Fetch LeetCode problem data by slug from CSV data"""
    try:
        # Try to get problem from CSV data first
        problem = get_problem_by_slug(problem_slug)
        
        if problem:
            # Safely handle tags field which might be NaN
            tags = problem.get('tags', '')
            if pd.isna(tags) or tags == '':
                tags = ''
                topic_tags = []
            else:
                topic_tags = str(tags).split(',') if tags else []
            
            # Try to get function signature from our predefined signatures
            function_signature = None
            try:
                function_signature = get_problem_signature(problem_slug, 'python')
            except Exception as e:
                print(f"Could not get function signature for {problem_slug}: {e}")
                function_signature = None
            
            # Convert CSV data to expected format
            problem_data = {
                'title': problem.get('title', 'Unknown Title'),
                'difficulty': problem.get('difficulty', 'Unknown').title(),
                'content': f"<p>Problem: {problem.get('title', 'Unknown')}</p><p>Topic: {problem.get('topic', 'Unknown')}</p><p>Tags: {tags if tags else 'None'}</p>",
                'testCases': get_default_test_cases(problem_slug, problem.get('title', '')),  # Use proper test cases
                'topicTags': topic_tags,
                'url': problem.get('url', ''),
                'qid': problem.get('QID', 0),
                'functionSignature': function_signature  # Add function signature
            }
        else:
            # Fallback to default data if not found in CSV
            problem_data = get_default_problem_data(problem_slug)
            # Always ensure default has test cases and a basic function signature
            if 'functionSignature' not in problem_data:
                problem_data['functionSignature'] = get_problem_signature(problem_slug, 'python')
        
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
    """Get list of available LeetCode problems from CSV data"""
    try:
        if leetcode_data is None:
            # Fallback to a small default list when CSV isn't available
            problems = [
                {
                    'slug': 'two-sum',
                    'title': 'Two Sum',
                    'difficulty': 'Easy',
                    'acceptanceRate': 0.5,
                    'paidOnly': False,
                    'topicTags': ['arrays','hashmap'],
                    'qid': 1,
                    'topic': 'arrays'
                },
                {
                    'slug': 'container-with-most-water',
                    'title': 'Container With Most Water',
                    'difficulty': 'Medium',
                    'acceptanceRate': 0.5,
                    'paidOnly': False,
                    'topicTags': ['two_pointers'],
                    'qid': 2,
                    'topic': 'arrays'
                }
            ]
            return jsonify({'status': 'success', 'data': problems})
        
        # Convert CSV data to expected format
        problems = []
        for _, row in leetcode_data.iterrows():
            # Safely handle tags field which might be NaN
            tags = row.get('tags', '')
            if pd.isna(tags) or tags == '':
                topic_tags = []
            else:
                topic_tags = str(tags).split(',') if tags else []
            
            problems.append({
                'slug': row['titleSlug'],
                'title': row['title'],
                'difficulty': row['difficulty'].title(),
                'acceptanceRate': 0.5,  # Default value since not in CSV
                'paidOnly': False,  # Default value since not in CSV
                'topicTags': topic_tags,
                'qid': row['QID'],
                'topic': row['topic']
            })
        
        return jsonify({
            'status': 'success',
            'data': problems
        })
        
    except Exception as e:
        print(f"Error fetching problems: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch problems list: {str(e)}'
        }), 500

@app.route('/api/leetcode/problems/<difficulty>', methods=['GET'])
def get_problems_by_difficulty_endpoint(difficulty):
    """Get problems by difficulty level"""
    try:
        problems = get_problems_by_difficulty(difficulty.lower())
        
        # Convert to expected format
        formatted_problems = []
        for problem in problems:
            # Safely handle tags field which might be NaN
            tags = problem.get('tags', '')
            if pd.isna(tags) or tags == '':
                tags_list = []
            else:
                tags_list = str(tags).split(',') if tags else []
            
            formatted_problems.append({
                'slug': problem['titleSlug'],
                'title': problem['title'],
                'difficulty': problem['difficulty'].title(),
                'topic': problem['topic'],
                'tags': tags_list,
                'qid': problem['QID']
            })
        
        if not formatted_problems:
            # Fallback: provide at least Two Sum for any difficulty request
            fallback = [{
                'slug': 'two-sum',
                'title': 'Two Sum',
                'difficulty': 'Easy',
                'topic': 'arrays',
                'tags': ['arrays','hashmap'],
                'qid': 1
            }]
            return jsonify({'status': 'success', 'data': fallback})
        return jsonify({'status': 'success', 'data': formatted_problems})
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch {difficulty} problems: {str(e)}'
        }), 500

@app.route('/api/leetcode/topic/<path:topic>', methods=['GET'])
def get_problems_by_topic_endpoint(topic):
    """Get problems by topic"""
    try:
        # Decode URL encoding
        from urllib.parse import unquote
        topic = unquote(topic)
        
        problems = get_problems_by_topic(topic)
        
        # Convert to expected format
        formatted_problems = []
        for problem in problems:
            # Safely handle tags field which might be NaN
            tags = problem.get('tags', '')
            if pd.isna(tags) or tags == '':
                tags_list = []
            else:
                tags_list = str(tags).split(',') if tags else []
            
            formatted_problems.append({
                'slug': problem['titleSlug'],
                'title': problem['title'],
                'difficulty': problem['difficulty'].title(),
                'topic': problem['topic'],
                'tags': tags_list,
                'qid': problem['QID']
            })
        
        if not formatted_problems:
            # Fallback to at least one easy and one medium problem
            formatted_problems = [
                {
                    'slug': 'two-sum',
                    'title': 'Two Sum',
                    'difficulty': 'Easy',
                    'topic': 'arrays',
                    'tags': ['arrays','hashmap'],
                    'qid': 1
                },
                {
                    'slug': 'container-with-most-water',
                    'title': 'Container With Most Water',
                    'difficulty': 'Medium',
                    'topic': 'arrays',
                    'tags': ['two_pointers'],
                    'qid': 2
                }
            ]
        return jsonify({'status': 'success', 'data': formatted_problems})
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to fetch {topic} problems: {str(e)}'
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