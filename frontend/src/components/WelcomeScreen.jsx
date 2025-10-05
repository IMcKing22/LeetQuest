import React from 'react';
import { useNavigate } from 'react-router-dom';
import './WelcomeScreen.css';

const WelcomeScreen = () => {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/topics');
  };

  return (
    <div className="welcome-screen">
      <div className="welcome-container">
        <div className="welcome-box">
          <h1 className="welcome-title">Welcome to LeetQuest!</h1>
          <p className="welcome-subtitle">Choose a Topic!</p>
          <p className="welcome-description">
            Embark on an epic coding adventure where every problem is a quest, 
            every solution is a victory, and every challenge makes you stronger!
          </p>
          <button className="get-started-button" onClick={handleGetStarted}>
            Start Your Quest! 🚀
          </button>
        </div>
        
        <div className="features">
          <div className="feature">
            <div className="feature-icon">🎯</div>
            <h3>Progressive Difficulty</h3>
            <p>Start with Easy problems and work your way up to Hard challenges</p>
          </div>
          <div className="feature">
            <div className="feature-icon">📚</div>
            <h3>Topic-Based Learning</h3>
            <p>Master specific algorithms and data structures through focused practice</p>
          </div>
          <div className="feature">
            <div className="feature-icon">🤖</div>
            <h3>AI Assistant</h3>
            <p>Get help from Bella, your friendly coding companion</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;
