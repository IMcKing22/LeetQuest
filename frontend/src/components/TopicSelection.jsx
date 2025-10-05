import React from 'react';
import { useNavigate } from 'react-router-dom';
import Avatar from './Avatar';
import './TopicSelection.css';

const TopicSelection = () => {
  const navigate = useNavigate();

  const topics = [
    { name: 'Arrays & Hashing', completed: 0, total: 9 },
    { name: 'Two Pointers', completed: 0, total: 5 },
    { name: 'Sliding Window', completed: 0, total: 6 },
    { name: 'Stack', completed: 0, total: 7 },
    { name: 'Binary Search', completed: 0, total: 7 },
    { name: 'Linked List', completed: 0, total: 11 },
    { name: 'Trees', completed: 0, total: 15 },
    { name: 'Heap / Priority Queue', completed: 0, total: 7 },
    { name: 'Backtracking', completed: 0, total: 9 },
    { name: 'Tries', completed: 0, total: 3 },
    { name: 'Graphs', completed: 0, total: 13 },
    { name: 'Advanced Graphs', completed: 0, total: 6 },
    { name: '1-D Dynamic Programming', completed: 0, total: 12 },
    { name: '2-D Dynamic Programming', completed: 0, total: 11 },
    { name: 'Greedy', completed: 0, total: 8 },
    { name: 'Intervals', completed: 0, total: 6 },
    { name: 'Math & Geometry', completed: 0, total: 8 },
  ];

  const handleTopicClick = (topic) => {
    navigate('/story', { state: { topic } });
  };

  return (
    <div className="topic-selection">
      <div className="bella-header">
        <Avatar />
      </div>
      <div className="topics-container">
        <h2 className="topics-title">Choose Your Adventure Topic!</h2>
        <div className="topics-grid">
          {topics.map((topic, index) => {
            const progress = (topic.completed / topic.total) * 100;
            return (
              <div
                key={index}
                className="topic-card"
                onClick={() => handleTopicClick(topic)}
              >
                <div className="topic-info">
                  <span className="topic-name">{topic.name}</span>
                  <span className="topic-progress">({topic.completed}/{topic.total})</span>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{ width: `${progress}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default TopicSelection;
