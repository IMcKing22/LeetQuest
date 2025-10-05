import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Avatar from './Avatar';
import './ProblemScreen.css';

const ProblemScreen = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { topic, choice } = location.state || {};
  const [isSolved, setIsSolved] = useState(false);
  const [problemData, setProblemData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [code, setCode] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [executing, setExecuting] = useState(false);
  const [executionResults, setExecutionResults] = useState(null);

  console.log('ProblemScreen rendered with:', { topic, choice, loading, error, problemData });

  // Define displayProblem early to avoid hoisting issues
  const displayProblem = problemData || {
    title: "Two Sum",
    difficulty: "Easy",
    content: `Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.`,
    testCases: [
      {
        input: "nums = [2,7,11,15], target = 9",
        output: "[0,1]",
        explanation: "Because nums[0] + nums[1] == 9, we return [0, 1]."
      },
      {
        input: "nums = [3,2,4], target = 6",
        output: "[1,2]",
        explanation: "Because nums[1] + nums[2] == 6, we return [1, 2]."
      }
    ]
  };

  // Function to generate appropriate starter code based on problem type
  const getStarterCode = (language, problemTitle) => {
    const title = (problemTitle || 'Two Sum').toLowerCase();
    
    if (title.includes('two sum')) {
      if (language === 'python') return `def solution(nums, target):
    # Your code here
    pass`;
      if (language === 'javascript') return `function solution(nums, target) {
    // Your code here
    
}`;
      if (language === 'java') return `class Solution {
    public int[] solution(int[] nums, int target) {
        // Your code here
        return new int[0];
    }
}`;
      if (language === 'cpp') return `class Solution {
public:
    vector<int> solution(vector<int>& nums, int target) {
        // Your code here
        return {};
    }
};`;
      if (language === 'c') return `int* solution(int* nums, int numsSize, int target, int* returnSize) {
    // Your code here
    *returnSize = 0;
    return NULL;
}`;
    }
    
    if (title.includes('container') || title.includes('water')) {
      if (language === 'python') return `def solution(height):
    # Your code here
    pass`;
      if (language === 'javascript') return `function solution(height) {
    // Your code here
    
}`;
      if (language === 'java') return `class Solution {
    public int solution(int[] height) {
        // Your code here
        return 0;
    }
}`;
      if (language === 'cpp') return `class Solution {
public:
    int solution(vector<int>& height) {
        // Your code here
        return 0;
    }
};`;
    }
    
    if (title.includes('longest') || title.includes('substring')) {
      if (language === 'python') return `def solution(s):
    # Your code here
    pass`;
      if (language === 'javascript') return `function solution(s) {
    // Your code here
    
}`;
      if (language === 'java') return `class Solution {
    public int solution(String s) {
        // Your code here
        return 0;
    }
}`;
      if (language === 'cpp') return `class Solution {
public:
    int solution(string s) {
        // Your code here
        return 0;
    }
};`;
    }
    
    if (title.includes('valid') || title.includes('parentheses')) {
      if (language === 'python') return `def solution(s):
    # Your code here
    pass`;
      if (language === 'javascript') return `function solution(s) {
    // Your code here
    
}`;
      if (language === 'java') return `class Solution {
    public boolean solution(String s) {
        // Your code here
        return false;
    }
}`;
      if (language === 'cpp') return `class Solution {
public:
    bool solution(string s) {
        // Your code here
        return false;
    }
};`;
    }
    
    if (title.includes('binary search')) {
      if (language === 'python') return `def solution(nums, target):
    # Your code here
    pass`;
      if (language === 'javascript') return `function solution(nums, target) {
    // Your code here
    
}`;
      if (language === 'java') return `class Solution {
    public int solution(int[] nums, int target) {
        // Your code here
        return -1;
    }
}`;
      if (language === 'cpp') return `class Solution {
public:
    int solution(vector<int>& nums, int target) {
        // Your code here
        return -1;
    }
};`;
    }
    
    // Default starter code
    if (language === 'python') return `def solution():
    # Your code here
    pass`;
    if (language === 'javascript') return `function solution() {
    // Your code here
    
}`;
    if (language === 'java') return `class Solution {
    public int solution() {
        // Your code here
        return 0;
    }
}`;
    if (language === 'cpp') return `class Solution {
public:
    int solution() {
        // Your code here
        return 0;
    }
};`;
    if (language === 'c') return `int solution() {
    // Your code here
    return 0;
}`;
  };

  // Programming language configurations
  const languages = {
    python: {
      name: 'Python',
      extension: 'py',
      languageId: 71
    },
    javascript: {
      name: 'JavaScript',
      extension: 'js',
      languageId: 63
    },
    java: {
      name: 'Java',
      extension: 'java',
      languageId: 62
    },
    cpp: {
      name: 'C++',
      extension: 'cpp',
      languageId: 54
    },
    c: {
      name: 'C',
      extension: 'c',
      languageId: 50
    }
  };

  // Initialize code with starter code when language changes or problem changes
  useEffect(() => {
    try {
      const starterCode = getStarterCode(selectedLanguage, displayProblem?.title || 'Two Sum');
      setCode(starterCode);
      console.log('Set starter code:', starterCode);
    } catch (err) {
      console.error('Error setting starter code:', err);
      setCode('def solution():\n    # Your code here\n    pass');
    }
  }, [selectedLanguage, displayProblem?.title]);

  useEffect(() => {
    const fetchProblem = async () => {
      try {
        setLoading(true);
        // Determine which problem to fetch based on topic/choice
        let problemSlug = 'two-sum'; // default
        
        // You can customize this logic based on topic and choice
        if (topic?.name === 'Arrays & Hashing') {
          problemSlug = 'two-sum';
        } else if (topic?.name === 'Two Pointers') {
          problemSlug = 'container-with-most-water';
        } else if (topic?.name === 'Sliding Window') {
          problemSlug = 'longest-substring-without-repeating-characters';
        } else if (topic?.name === 'Stack') {
          problemSlug = 'valid-parentheses';
        } else if (topic?.name === 'Binary Search') {
          problemSlug = 'binary-search';
        } else if (topic?.name === 'Linked List') {
          problemSlug = 'add-two-numbers';
        } else if (topic?.name === 'Trees') {
          problemSlug = 'binary-tree-inorder-traversal';
        } else if (topic?.name === 'Heap / Priority Queue') {
          problemSlug = 'kth-largest-element-in-an-array';
        } else if (topic?.name === 'Backtracking') {
          problemSlug = 'letter-combinations-of-a-phone-number';
        } else if (topic?.name === 'Tries') {
          problemSlug = 'implement-trie-prefix-tree';
        } else if (topic?.name === 'Graphs') {
          problemSlug = 'number-of-islands';
        } else if (topic?.name === 'Advanced Graphs') {
          problemSlug = 'course-schedule';
        } else if (topic?.name === '1-D Dynamic Programming') {
          problemSlug = 'climbing-stairs';
        } else if (topic?.name === '2-D Dynamic Programming') {
          problemSlug = 'unique-paths';
        } else if (topic?.name === 'Greedy') {
          problemSlug = 'jump-game';
        } else if (topic?.name === 'Intervals') {
          problemSlug = 'merge-intervals';
        } else if (topic?.name === 'Math & Geometry') {
          problemSlug = 'rotate-image';
        }
        
        const response = await fetch(`http://localhost:5002/api/leetcode/${problemSlug}`);
        const result = await response.json();
        
        console.log('Fetched problem data:', result);
        
        if (result.status === 'success') {
          setProblemData(result.data);
          console.log('Set problemData:', result.data);
        } else {
          setError(result.message);
        }
      } catch (err) {
        setError('Failed to fetch problem data');
        console.error('Error fetching problem:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProblem();
  }, [topic, choice]);

  const handleExecuteCode = async () => {
    if (!code.trim()) {
      alert('Please write some code first!');
      return;
    }

    setExecuting(true);
    setExecutionResults(null);

    const requestData = {
      code: code,
      language: selectedLanguage,
      languageId: languages[selectedLanguage].languageId,
      testCases: displayProblem.testCases || []
    };

    console.log('Sending request:', requestData);
    console.log('displayProblem:', displayProblem);

    try {
      const response = await fetch('http://localhost:5002/api/leetcode/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      const result = await response.json();
      console.log('Received response:', result);

      if (result.status === 'success') {
        setExecutionResults(result);
        if (result.allPassed) {
          setIsSolved(true);
        }
      } else {
        setExecutionResults({
          status: 'error',
          message: result.message
        });
      }
    } catch (err) {
      console.error('Error executing code:', err);
      setExecutionResults({
        status: 'error',
        message: 'Failed to execute code: ' + err.message
      });
    } finally {
      setExecuting(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = e.target;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const value = textarea.value;
      
      // Insert tab character
      const newValue = value.substring(0, start) + '    ' + value.substring(end);
      setCode(newValue);
      
      // Set cursor position after the inserted tab
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      }, 0);
    }
  };

  const handleSolve = async () => {
    if (!code.trim()) {
      alert('Please write some code first!');
      return;
    }

    // First run the code to check if it works
    setExecuting(true);
    setExecutionResults(null);

    const requestData = {
      code: code,
      language: selectedLanguage,
      languageId: languages[selectedLanguage].languageId,
      testCases: displayProblem.testCases || []
    };

    try {
      const response = await fetch('http://localhost:5002/api/leetcode/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      const result = await response.json();

      if (result.status === 'success') {
        setExecutionResults(result);
        if (result.allPassed) {
          setIsSolved(true);
        } else {
          alert('Your solution failed some test cases. Please fix the issues and try again.');
        }
      } else {
        alert('Your code has errors. Please fix them and try again.');
        setExecutionResults({
          status: 'error',
          message: result.message
        });
      }
    } catch (err) {
      alert('Failed to execute code. Please try again.');
      setExecutionResults({
        status: 'error',
        message: 'Failed to execute code: ' + err.message
      });
    } finally {
      setExecuting(false);
    }
  };

  const handleNextStory = () => {
    navigate('/story', { state: { topic, choice, completed: true } });
  };


  if (loading) {
    return (
      <div className="problem-screen">
        <Avatar />
        <div className="problem-container">
          <div className="loading-message">
            <h2>Loading problem...</h2>
            <p>Fetching the latest challenge for you!</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="problem-screen">
        <Avatar />
        <div className="problem-container">
          <div className="error-message">
            <h2>Error loading problem</h2>
            <p>{error}</p>
            <button onClick={() => window.location.reload()}>Retry</button>
          </div>
        </div>
      </div>
    );
  }

  // Add error boundary for the main render
  try {

  return (
    <div className="problem-screen">
      <div className="problem-container">
        <Avatar />
        <div className="problem-header">
          <div className="problem-title-section">
            <h1>{displayProblem.title}</h1>
            <span className={`difficulty ${displayProblem.difficulty.toLowerCase()}`}>
              {displayProblem.difficulty}
            </span>
          </div>
          <div className="problem-meta">
            <span>Topic: {topic?.name}</span>
            <span>Path: {choice === 'efficient' ? 'Efficiency' : 'Elegance'}</span>
          </div>
        </div>

        <div className="problem-content">
          <div className="problem-layout">
            <div className="problem-left">
              <div className="problem-description">
                <h3>Problem Description</h3>
                <div 
                  className="description-text"
                  dangerouslySetInnerHTML={{ __html: displayProblem.content }}
                />
              </div>

              {displayProblem.testCases && displayProblem.testCases.length > 0 && (
                <div className="problem-examples">
                  <h3>Examples</h3>
                  {displayProblem.testCases.map((example, index) => (
                    <div key={index} className="example">
                      <div className="example-header">
                        <strong>Example {index + 1}:</strong>
                      </div>
                      <div className="example-content">
                        <div className="example-input">
                          <strong>Input:</strong> <code>{example.input}</code>
                        </div>
                        <div className="example-output">
                          <strong>Output:</strong> <code>{example.output}</code>
                        </div>
                        <div className="example-explanation">
                          <strong>Explanation:</strong> {example.explanation}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="problem-right">
              <div className="code-editor">
                <div className="editor-header">
                  <h3>Your Solution</h3>
                  <div className="language-selector">
                    <label htmlFor="language-select">Language: </label>
                    <select 
                      id="language-select"
                      value={selectedLanguage} 
                      onChange={(e) => setSelectedLanguage(e.target.value)}
                      className="language-dropdown"
                    >
                      {Object.entries(languages).map(([key, lang]) => (
                        <option key={key} value={key}>{lang.name}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="editor-container">
                  <textarea 
                    className="code-input"
                    placeholder="// Write your solution here..."
                    rows={15}
                    value={code}
                    onChange={(e) => setCode(e.target.value)}
                    onKeyDown={handleKeyDown}
                    spellCheck={false}
                  />
                </div>
                <div className="editor-actions">
                  <button 
                    className="run-button"
                    onClick={handleExecuteCode}
                    disabled={executing || isSolved}
                  >
                    {executing ? 'Running...' : 'Run Code'}
                  </button>
                  <button 
                    className="solve-button"
                    onClick={handleSolve}
                    disabled={executing || isSolved}
                  >
                    {executing ? 'Checking...' : isSolved ? 'Solved!' : 'Submit Solution'}
                  </button>
                </div>
              </div>

              {executionResults && (
                <div className="execution-results">
                  <h3>Execution Results</h3>
                  
                  {/* Code Output Section */}
                  <div className="code-output-section">
                    <h4>Code Output:</h4>
                    <div className="code-output">
                      <pre>{executionResults.codeOutput || 'No output'}</pre>
                    </div>
                  </div>

                  {/* Test Results Section */}
                  <div className="test-results-section">
                    <h4>Test Results:</h4>
                    {executionResults.status === 'error' ? (
                      <div className="error-result">
                        <p><strong>Error:</strong> {executionResults.message}</p>
                      </div>
                    ) : (
                      <div className="test-results">
                        <div className={`result-summary ${executionResults.allPassed ? 'passed' : 'failed'}`}>
                          {executionResults.allPassed ? '✅ All tests passed!' : '❌ Some tests failed'}
                        </div>
                        {executionResults.results && executionResults.results.map((result, index) => (
                          <div key={index} className={`test-case ${result.passed ? 'passed' : 'failed'}`}>
                            <div className="test-header">
                              <strong>Test Case {result.testCase}:</strong>
                              <span className={`status ${result.passed ? 'passed' : 'failed'}`}>
                                {result.passed ? '✅ PASS' : '❌ FAIL'}
                              </span>
                            </div>
                            <div className="test-details">
                              <div><strong>Input:</strong> <code>{result.input}</code></div>
                              <div><strong>Expected:</strong> <code>{result.expectedOutput}</code></div>
                              <div><strong>Actual:</strong> <code>{result.actualOutput}</code></div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {isSolved && (
                <div className="success-message">
                  <div className="success-content">
                    <h3>🎉 Congratulations!</h3>
                    <p>You've successfully solved the problem! Your journey continues...</p>
                    <button className="next-story-button" onClick={handleNextStory}>
                      Continue Story
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
  } catch (renderError) {
    console.error('Error rendering ProblemScreen:', renderError);
    return (
      <div className="problem-screen">
        <Avatar />
        <div className="problem-container">
          <div className="error-message">
            <h2>Error rendering problem screen</h2>
            <p>Something went wrong. Please refresh the page.</p>
            <button onClick={() => window.location.reload()}>Refresh</button>
          </div>
        </div>
      </div>
    );
  }
};

export default ProblemScreen;
