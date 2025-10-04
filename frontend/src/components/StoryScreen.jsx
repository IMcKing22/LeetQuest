import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Avatar from './Avatar';
import './StoryScreen.css';

const StoryScreen = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { topic } = location.state || {};

  const handleMakeChoice = () => {
    navigate('/choice', { state: { topic } });
  };

  return (
    <div className="story-screen">
      <Avatar />
      <div className="story-container">
        <div className="story-box">
          <h2>Welcome to {topic?.name || 'Your Adventure'}!</h2>
          <div className="story-content">
            <p>
              You find yourself in a mysterious coding realm where algorithms hold the key to unlocking ancient secrets. 
              The path ahead is treacherous, filled with data structures and complex problems that will test your skills.
            </p>
            <p>
              As you venture deeper into this digital wilderness, you must choose your path wisely. Each decision will 
              lead you to new challenges and opportunities to grow as a programmer.
            </p>
            <p>
              The time has come to make your choice. Will you take the path of efficiency, or will you choose the 
              path of elegance? Your decision will determine the challenges that lie ahead.
            </p>
          </div>
          <button className="next-button" onClick={handleMakeChoice}>
            Make Your Choice
          </button>
        </div>
      </div>
    </div>
  );
};

export default StoryScreen;
