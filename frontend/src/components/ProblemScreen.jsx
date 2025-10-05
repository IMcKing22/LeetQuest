import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Editor from '@monaco-editor/react';
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
  const editorRef = useRef(null);
  
  // Bella's animation states
  const [bellaEmotion, setBellaEmotion] = useState('neutral');
  const [bellaIsTalking, setBellaIsTalking] = useState(false);
  const [speechBubble, setSpeechBubble] = useState({ visible: false, messages: [] });
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const [apiKey, setApiKey] = useState(import.meta.env.VITE_OPENAI_API_KEY || '');
  const [chatBoxOpen, setChatBoxOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [chatHistory, setChatHistory] = useState([]);

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

  // Bella's AI review functions
  const detectEmotionForReview = (text) => {
    const lower = text.toLowerCase();
    
    if (lower.includes('wrong') || lower.includes('error') || lower.includes('bug') || 
        lower.includes('issue') || lower.includes('problem')) {
      return 'sad';
    }
    if (lower.includes('great') || lower.includes('correct') || lower.includes('good') ||
        lower.includes('well done') || lower.includes('perfect')) {
      return 'happy';
    }
    if (lower.includes('however') || lower.includes('but') || lower.includes('consider')) {
      return 'thinking';
    }
    if (lower.includes('!') || lower.includes('important') || lower.includes('critical')) {
      return 'surprised';
    }
    
    return 'neutral';
  };

  const parseReviewIntoChunks = (review) => {
    const chunks = [];
    const lines = review.split('\n').filter(line => line.trim());
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (trimmed.startsWith('```') || trimmed.includes('```')) {
        // Code block
        const codeMatch = review.match(/```[\w]*\n([\s\S]*?)```/);
        if (codeMatch) {
          chunks.push({ text: codeMatch[1].trim(), isCode: true });
        }
      } else if (trimmed.length > 10) {
        // Regular text
        chunks.push({ text: trimmed, isCode: false });
      }
    }
    
    return chunks.length > 0 ? chunks : [{ text: review, isCode: false }];
  };

  const getMockReview = () => {
    return [
      { text: "Let me review your code! 👀", isCode: false },
      { text: "I found a few issues we should talk about.", isCode: false },
      { text: "First, I notice you're using a nested loop here. That gives you O(n²) time complexity.", isCode: false },
      { text: "for (let i = 0; i < arr.length; i++) {\n  for (let j = 0; j < arr.length; j++) {\n    // ...\n  }\n}", isCode: true },
      { text: "For this problem, you can optimize it to O(n) using a hash map to store values you've seen.", isCode: false },
      { text: "Also, watch out for edge cases! What happens if the array is empty or has only one element?", isCode: false },
      { text: "Try adding checks like: if (!arr || arr.length === 0) return []", isCode: false },
      { text: "With these fixes, your solution will be much faster! Give it another try! 💪", isCode: false }
    ];
  };

  const reviewWithOpenAI = async (codeToReview) => {
    try {
      const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          model: 'gpt-4o-mini',
          messages: [{
            role: 'system',
            content: 'You are Bella, a friendly code reviewer. Analyze the LeetCode solution and explain what is wrong in 3-5 simple, short chunks. Each chunk should be 1-2 sentences. Be encouraging but point out issues clearly. If it is completely off track, point it out. Format code snippets on separate lines. Do not repeat yourself.'
          }, {
            role: 'user',
            content: codeToReview
          }],
          temperature: 0.4
        })
      });
      
      const data = await response.json();
      const review = data.choices[0].message.content;
      
      return parseReviewIntoChunks(review);
      
    } catch (error) {
      console.error('OpenAI API Error:', error);
      return getMockReview();
    }
  };

  const startBellaReview = async () => {
    setBellaEmotion('thinking');
    setBellaIsTalking(true);
    
    let reviewChunks;
    if (apiKey.trim()) {
      reviewChunks = await reviewWithOpenAI(code);
    } else {
      reviewChunks = getMockReview();
    }
    
    setSpeechBubble({ visible: true, messages: reviewChunks });
    setCurrentMessageIndex(0);
    
    // Display messages one by one
    for (let i = 0; i < reviewChunks.length; i++) {
      const chunk = reviewChunks[i];
      
      // Set emotion based on chunk content
      const emotion = detectEmotionForReview(chunk.text);
      setBellaEmotion(emotion);
      
      // Calculate talk duration based on text length
      const duration = Math.min(chunk.text.length * 30, 2000);
      setBellaIsTalking(true);
      
      setCurrentMessageIndex(i);
      
      // Wait before next chunk
      await new Promise(resolve => setTimeout(resolve, duration + 1000));
    }
    
    setBellaIsTalking(false);
    setBellaEmotion('neutral');
    
    // Hide speech bubble after 5 seconds
    setTimeout(() => {
      setSpeechBubble({ visible: false, messages: [] });
    }, 5000);
  };

  // Function to generate appropriate starter code based on problem type
  const getStarterCode = (language, problemTitle) => {
    const title = (problemTitle || 'Two Sum').toLowerCase();
    
    if (title.includes('two sum')) {
      if (language === 'python') return `from typing import List

def solution(nums: List[int], target: int) -> List[int]:
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
      if (language === 'python') return `from typing import List

def solution(height: List[int]) -> int:
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
      if (language === 'python') return `def solution(s: str) -> int:
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
      if (language === 'python') return `def solution(s: str) -> bool:
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
      if (language === 'python') return `from typing import List

def solution(nums: List[int], target: int) -> int:
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
          setBellaEmotion('happy');
        } else {
          // Code failed - trigger Bella's review
          startBellaReview();
        }
      } else {
        setExecutionResults({
          status: 'error',
          message: result.message
        });
        // Code has errors - trigger Bella's review
        startBellaReview();
      }
    } catch (err) {
      console.error('Error executing code:', err);
      setExecutionResults({
        status: 'error',
        message: 'Failed to execute code: ' + err.message
      });
      // Network error - trigger Bella's review
      startBellaReview();
    } finally {
      setExecuting(false);
    }
  };

  const handleEditorDidMount = (editor, monaco) => {
    editorRef.current = editor;
    
    // Configure editor options
    editor.updateOptions({
      fontSize: 14,
      fontFamily: 'Monaco, Menlo, "Ubuntu Mono", monospace',
      lineNumbers: 'on',
      minimap: { enabled: false },
      scrollBeyondLastLine: false,
      automaticLayout: true,
      tabSize: 4,
      insertSpaces: true,
      wordWrap: 'on',
      bracketPairColorization: { enabled: true },
      guides: {
        bracketPairs: true,
        indentation: true
      }
    });

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Slash, () => {
      editor.trigger('keyboard', 'editor.action.commentLine', {});
    });

    editor.addCommand(monaco.KeyMod.Shift | monaco.KeyCode.Tab, () => {
      editor.trigger('keyboard', 'editor.action.outdentLines', {});
    });

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyA, () => {
      editor.trigger('keyboard', 'editor.action.selectAll', {});
    });

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      // Save functionality - could be used for auto-save
      console.log('Save triggered');
    });
  };

  const getLanguageForMonaco = (language) => {
    const languageMap = {
      'python': 'python',
      'javascript': 'javascript',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c'
    };
    return languageMap[language] || 'python';
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
          setBellaEmotion('happy');
        } else {
          alert('Your solution failed some test cases. Please fix the issues and try again.');
          // Code failed - trigger Bella's review
          startBellaReview();
        }
      } else {
        alert('Your code has errors. Please fix them and try again.');
        setExecutionResults({
          status: 'error',
          message: result.message
        });
        // Code has errors - trigger Bella's review
        startBellaReview();
      }
    } catch (err) {
      alert('Failed to execute code. Please try again.');
      setExecutionResults({
        status: 'error',
        message: 'Failed to execute code: ' + err.message
      });
      // Network error - trigger Bella's review
      startBellaReview();
    } finally {
      setExecuting(false);
    }
  };

  const nextMessage = () => {
    if (currentMessageIndex < speechBubble.messages.length - 1) {
      setCurrentMessageIndex(currentMessageIndex + 1);
    }
  };

  const handleChatSubmit = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = chatInput.trim();
    setChatInput('');
    
    // Add user message to chat history
    const newChatHistory = [...chatHistory, { type: 'user', message: userMessage }];
    setChatHistory(newChatHistory);
    
    setBellaEmotion('thinking');
    setBellaIsTalking(true);

    try {
      let bellaResponse;
      if (apiKey.trim()) {
        // Use OpenAI for chat response
        const response = await fetch('https://api.openai.com/v1/chat/completions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
          },
          body: JSON.stringify({
            model: 'gpt-4o-mini',
            messages: [{
              role: 'system',
              content: 'You are Bella, a friendly coding assistant. Help the user with their LeetCode problem. Be encouraging, helpful, and provide clear explanations. Keep responses concise but informative.'
            }, {
              role: 'user',
              content: userMessage
            }],
            temperature: 0.7
          })
        });
        
        const data = await response.json();
        bellaResponse = data.choices[0].message.content;
      } else {
        // Mock response for when no API key
        bellaResponse = "I'd love to help you with that! However, I need an API key to provide personalized assistance. For now, I can help with general coding tips and problem-solving strategies. What specific aspect of the problem would you like to discuss?";
      }
      
      // Add Bella's response to chat history
      setChatHistory([...newChatHistory, { type: 'bella', message: bellaResponse }]);
      setBellaEmotion('happy');
      
    } catch (error) {
      console.error('Chat error:', error);
      const errorResponse = "Sorry, I'm having trouble responding right now. Please try again later!";
      setChatHistory([...newChatHistory, { type: 'bella', message: errorResponse }]);
      setBellaEmotion('sad');
    } finally {
      setBellaIsTalking(false);
    }
  };

  const handleNextStory = () => {
    navigate('/story', { state: { topic, choice, completed: true } });
  };


  if (loading) {
    return (
      <div className="problem-screen">
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
    console.log('Rendering ProblemScreen with state:', { 
      topic, choice, loading, error, problemData, chatBoxOpen 
    });

    // Show loading state
    if (loading) {
      return (
        <div className="problem-screen">
          <div className="problem-container">
            <div className="loading-message">
              <h2>Loading problem...</h2>
              <p>Please wait while we fetch the problem data.</p>
            </div>
          </div>
        </div>
      );
    }

    // Show error state
    if (error) {
      return (
        <div className="problem-screen">
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

  return (
    <div className="problem-screen">
        <div className="problem-container">
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
          <div className={`problem-layout ${chatBoxOpen ? 'three-panel' : 'two-panel'}`}>
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

            <div className="problem-center">
              <div className="coding-section">
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
                  <Editor
                    height="400px"
                    language={getLanguageForMonaco(selectedLanguage)}
                    value={code}
                    onChange={(value) => setCode(value || '')}
                    onMount={handleEditorDidMount}
                    theme="vs-dark"
                    options={{
                      selectOnLineNumbers: true,
                      roundedSelection: false,
                      readOnly: false,
                      cursorStyle: 'line',
                      automaticLayout: true,
                      fontSize: 14,
                      tabSize: 4,
                      insertSpaces: true,
                      wordWrap: 'on'
                    }}
                  />
                </div>
                <div className="editor-actions">
                  <button 
                    className="help-button"
                    onClick={() => setChatBoxOpen(!chatBoxOpen)}
                  >
                    {chatBoxOpen ? 'Close Help' : 'Get Help'}
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

            {/* Bella Chat Box - Only shown when chatBoxOpen is true */}
            {chatBoxOpen && (
              <div className="problem-right">
                <div className="bella-chat-section">
                  <div className="bella-chat-header">
                    <div className="bella-avatar-large">
                      <Avatar name="Bella" emotion={bellaEmotion} isTalking={bellaIsTalking} />
                    </div>
                    <button 
                      className="bella-review-button"
                      onClick={startBellaReview}
                      disabled={bellaIsTalking}
                    >
                      {bellaIsTalking ? 'Bella is thinking...' : 'Code Review'}
                    </button>
                  </div>
                  
                  <div className="bella-chat-container">
                    {/* Chat History */}
                    <div className="chat-history">
                      {chatHistory.length === 0 && !speechBubble.visible && (
                        <div className="bella-welcome">
                          <div className="bella-avatar">
                            <span className="bella-emotion neutral">🤖</span>
                          </div>
                          <div className="bella-text">
                            <p>Hi! I'm Bella, your coding assistant. Ask me anything about the problem or click "Get Code Review" for feedback!</p>
                          </div>
                        </div>
                      )}
                      
                      {chatHistory.map((chat, index) => (
                        <div key={index} className={`chat-message ${chat.type}`}>
                          {chat.type === 'bella' && (
                            <div className="bella-avatar">
                              <span className={`bella-emotion ${bellaEmotion}`}>🤖</span>
                            </div>
                          )}
                          <div className="chat-text">
                            <p>{chat.message}</p>
                          </div>
                        </div>
                      ))}
                      
                      {speechBubble.visible && (
                        <div className="bella-message">
                          <div className="bella-avatar">
                            <span className={`bella-emotion ${bellaEmotion}`}>🤖</span>
                          </div>
                          <div className="bella-text">
                            <p>{speechBubble.messages[currentMessageIndex]?.text}</p>
                            {currentMessageIndex < speechBubble.messages.length - 1 && (
                              <button 
                                className="next-message-button"
                                onClick={nextMessage}
                              >
                                Next →
                              </button>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {/* Chat Input */}
                    <form onSubmit={handleChatSubmit} className="chat-input-form">
                      <div className="chat-input-container">
                        <input
                          type="text"
                          value={chatInput}
                          onChange={(e) => setChatInput(e.target.value)}
                          placeholder="Ask Bella anything about the problem..."
                          className="chat-input"
                          disabled={bellaIsTalking}
                        />
                        <button 
                          type="submit" 
                          className="chat-send-button"
                          disabled={bellaIsTalking || !chatInput.trim()}
                        >
                          {bellaIsTalking ? '...' : 'Send'}
                        </button>
                      </div>
                    </form>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
  } catch (renderError) {
    console.error('Error rendering ProblemScreen:', renderError);
    return (
      <div className="problem-screen">
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