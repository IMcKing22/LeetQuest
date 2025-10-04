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
        
        if (result.status === 'success') {
          setProblemData(result.data);
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

  const handleSolve = () => {
    setIsSolved(true);
  };

  const handleNextStory = () => {
    navigate('/story', { state: { topic, choice, completed: true } });
  };

  // Use real data from API or fallback to dummy data
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
                <h3>Your Solution</h3>
                <div className="editor-container">
                  <textarea 
                    className="code-input"
                    placeholder="// Write your solution here..."
                    rows={15}
                  />
                </div>
                <div className="editor-actions">
                  <button 
                    className="solve-button"
                    onClick={handleSolve}
                    disabled={isSolved}
                  >
                    {isSolved ? 'Solved!' : 'Submit Solution'}
                  </button>
                </div>
              </div>

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
};

export default ProblemScreen;
