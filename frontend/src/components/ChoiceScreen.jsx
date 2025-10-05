import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Avatar from './Avatar';
import './ChoiceScreen.css';

const ChoiceScreen = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { topic } = location.state || {};
  
  const [story, setStory] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [path1, setPath1] = useState({ title: 'Path of Efficiency', description: 'Focus on optimal time and space complexity.' });
  const [path2, setPath2] = useState({ title: 'Path of Elegance', description: 'Embrace clean, readable code.' });
  const [loading, setLoading] = useState(true);
  const [currentJoke, setCurrentJoke] = useState(0);

  const jokes = [
    "Why don't programmers like nature? It has too many bugs! 🐛",
    "How many programmers does it take to change a light bulb? None, that's a hardware problem! 💡",
    "Why did the programmer quit his job? He didn't get arrays! 📊",
    "What do you call a programmer from Finland? Nerdic! 🇫🇮",
    "Why do Java developers wear glasses? Because they can't C#! 👓",
    "What's a programmer's favorite hangout place? The Foo Bar! 🍺",
    "Why did the developer go broke? Because he used up all his cache! 💰",
    "What do you call a programmer who doesn't comment their code? A silent partner! 🤐",
    "Why don't programmers like to party? They prefer to function! 🎉",
    "What's a programmer's favorite type of music? Algo-rhythms! 🎵"
  ];

  // Cycle through jokes while loading
  useEffect(() => {
    if (loading) {
      const jokeInterval = setInterval(() => {
        setCurrentJoke((prev) => (prev + 1) % jokes.length);
      }, 4000); // Change joke every 4 seconds
      
      return () => clearInterval(jokeInterval);
    }
  }, [loading, jokes.length]);

  useEffect(() => {
    const generateStory = async () => {
      try {
        setLoading(true);
        
        // Set fallback content immediately
        const fallbackStory = `🌟 Welcome to the Realm of ${topic?.name || 'Coding Challenges'}! 🌟

You stand at the entrance of an ancient coding temple, where legendary algorithms are said to be hidden within mystical data structures. The air crackles with computational energy as you prepare to embark on your quest.

Before you lies a grand hall with two shimmering portals, each leading to a different approach for mastering ${topic?.name || 'coding'}. The left portal glows with the warm light of systematic learning, while the right portal pulses with the vibrant energy of creative exploration.

Which path will you choose to begin your epic journey?`;

        const fallbackPath1 = {
          title: 'Path of Ancient Wisdom',
          description: 'Master the time-tested algorithms of legendary coders. Follow systematic approaches that have stood the test of time. Build your foundation with proven techniques and disciplined practice.'
        };

        const fallbackPath2 = {
          title: 'Path of Digital Dragons',
          description: 'Forge new solutions through creative experimentation. Embrace innovative approaches and bold thinking. Discover uncharted territories where coding magic awaits.'
        };

        // Set fallback content first
        setStory(fallbackStory);
        setPath1(fallbackPath1);
        setPath2(fallbackPath2);
        
        // Try to get AI-generated content in the background (non-blocking)
        try {
          const storyPromise = fetch('http://localhost:5002/api/start', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ topic: topic?.name || 'Arrays & Hashing' })
          });
          
          const storyTimeout = new Promise((_, reject) => 
            setTimeout(() => reject(new Error('Story generation timeout')), 3000)
          );
          
          const storyResponse = await Promise.race([storyPromise, storyTimeout]);
          if (storyResponse.ok) {
            const storyData = await storyResponse.json();
            if (storyData.sessionId) {
              setSessionId(storyData.sessionId);
            }
            if (storyData.story && storyData.story.length > 50) {
              setStory(storyData.story);
            }
          }
        } catch (storyError) {
          console.warn('Story generation failed, using fallback:', storyError);
        }
        
        // Try to get AI-generated paths in the background (non-blocking)
        try {
          const [path1Response, path2Response] = await Promise.all([
            fetch('http://localhost:5002/api/choices', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ choice: 'path1', topic: topic?.name || 'Arrays & Hashing', sessionId })
            }),
            fetch('http://localhost:5002/api/choices', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ choice: 'path2', topic: topic?.name || 'Arrays & Hashing', sessionId })
            })
          ]);
          
          if (path1Response.ok) {
            const path1Data = await path1Response.json();
            if (path1Data.path1Title && path1Data.path1Description) {
              setPath1({
                title: path1Data.path1Title,
                description: path1Data.path1Description
              });
            }
          }
          
          if (path2Response.ok) {
            const path2Data = await path2Response.json();
            if (path2Data.path2Title && path2Data.path2Description) {
              setPath2({
                title: path2Data.path2Title,
                description: path2Data.path2Description
              });
            }
          }
        } catch (pathError) {
          console.warn('Path generation failed, using fallbacks:', pathError);
        }
        
      } catch (error) {
        console.error('Error in story generation:', error);
      } finally {
        setLoading(false);
      }
    };

    generateStory();
  }, [topic]);

  const handleChoice = (choice) => {
    navigate('/problem', { state: { topic, choice, sessionId } });
  };

  if (loading) {
    return (
      <div className="choice-screen">
        <div className="bella-header">
          <Avatar />
        </div>
        <div className="choice-container loading">
          <div className="loading-message">
            <h2>Generating your adventure...</h2>
            <div className="joke-container">
              <p className="joke-text">"{jokes[currentJoke]}"</p>
              <p className="joke-subtitle">- Bella, your coding companion</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="choice-screen">
      <div className="bella-header">
        <Avatar />
      </div>
      <div className="choice-container">
        <div className="story-sidebar">
          <div className="story-box">
            <h3>Your Epic Adventure</h3>
            <div className="story-content">
              {story.split('\n').map((line, index) => (
                <p key={index}>{line}</p>
              ))}
            </div>
          </div>
        </div>
        
        <div className="choice-main">
          <div className="choice-box">
            <h2>Choose Your Path</h2>
            <div className="choices">
              <button 
                className="choice-button"
                onClick={() => handleChoice('path1')}
              >
                <div className="choice-icon">⚡</div>
                <div className="choice-content">
                  <h3>{path1.title}</h3>
                  <p>{path1.description}</p>
                </div>
              </button>
              
              <button 
                className="choice-button"
                onClick={() => handleChoice('path2')}
              >
                <div className="choice-icon">✨</div>
                <div className="choice-content">
                  <h3>{path2.title}</h3>
                  <p>{path2.description}</p>
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
