import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Avatar from './Avatar';
import './ChoiceScreen.css';

const ChoiceScreen = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { topic } = location.state || {};

  const handleChoice = (choice) => {
    navigate('/problem', { state: { topic, choice } });
  };

  return (
    <div className="choice-screen">
      <Avatar />
      <div className="choice-container">
        <div className="story-sidebar">
          <div className="story-box">
            <h3>Your Journey So Far</h3>
            <p>
              You've chosen to explore the realm of {topic?.name || 'coding challenges'}. 
              The path ahead requires wisdom and skill. Choose your approach carefully.
            </p>
          </div>
        </div>
        
        <div className="choice-main">
          <div className="choice-box">
            <h2>Choose Your Path</h2>
            <div className="choices">
              <button 
                className="choice-button"
                onClick={() => handleChoice('efficient')}
              >
                <div className="choice-icon">⚡</div>
                <div className="choice-content">
                  <h3>Path of Efficiency</h3>
                  <p>Focus on optimal time and space complexity. Master the art of algorithmic efficiency.</p>
                </div>
              </button>
              
              <button 
                className="choice-button"
                onClick={() => handleChoice('elegant')}
              >
                <div className="choice-icon">✨</div>
                <div className="choice-content">
                  <h3>Path of Elegance</h3>
                  <p>Embrace clean, readable code. Find beauty in simplicity and clarity.</p>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChoiceScreen;
