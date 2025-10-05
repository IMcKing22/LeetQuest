import React, { useState, useEffect, useRef } from 'react';
import './Avatar.css';

const EMOTIONS = {
  neutral: {
    leftEye: { rx: 15, ry: 20 },
    rightEye: { rx: 15, ry: 20 },
    mouth: 'M 150 250 Q 200 260 250 250'
  },
  happy: {
    leftEye: { rx: 12, ry: 18 },
    rightEye: { rx: 12, ry: 18 },
    mouth: 'M 150 250 Q 200 290 250 250'
  },
  sad: {
    leftEye: { rx: 15, ry: 20 },
    rightEye: { rx: 15, ry: 20 },
    mouth: 'M 150 270 Q 200 250 250 270'
  },
  surprised: {
    leftEye: { rx: 20, ry: 25 },
    rightEye: { rx: 20, ry: 25 },
    mouth: 'M 180 260 Q 200 280 220 260'
  },
  thinking: {
    leftEye: { rx: 13, ry: 18 },
    rightEye: { rx: 13, ry: 18 },
    mouth: 'M 150 260 Q 200 255 250 260'
  }
};

const Avatar = ({ name = "Bella", emotion = "neutral", isTalking = false }) => {
  const [currentEmotion, setCurrentEmotion] = useState(emotion);
  const [isBlinking, setIsBlinking] = useState(false);
  const leftEyeRef = useRef(null);
  const rightEyeRef = useRef(null);
  const mouthRef = useRef(null);

  const easeInOutCubic = (t) => {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  };

  const animateElement = (element, props, duration) => {
    if (!element) return;
    
    const startProps = {};
    for (let prop in props) {
      startProps[prop] = parseFloat(element.getAttribute(prop));
    }
    
    const startTime = Date.now();
    
    const update = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const eased = easeInOutCubic(progress);
      
      for (let prop in props) {
        const value = startProps[prop] + (props[prop] - startProps[prop]) * eased;
        element.setAttribute(prop, value);
      }
      
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    };
    
    update();
  };

  const animatePath = (element, targetPath, duration) => {
    if (!element) return;
    
    const startTime = Date.now();
    
    const update = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      
      if (progress >= 1) {
        element.setAttribute('d', targetPath);
      } else {
        if (progress > 0.5) {
          element.setAttribute('d', targetPath);
        }
      }
      
      if (progress < 1) {
        requestAnimationFrame(update);
      }
    };
    
    update();
  };

  const setEmotion = (newEmotion) => {
    if (!EMOTIONS[newEmotion]) return;
    
    setCurrentEmotion(newEmotion);
    const config = EMOTIONS[newEmotion];
    
    animateElement(leftEyeRef.current, { rx: config.leftEye.rx, ry: config.leftEye.ry }, 300);
    animateElement(rightEyeRef.current, { rx: config.rightEye.rx, ry: config.rightEye.ry }, 300);
    animatePath(mouthRef.current, config.mouth, 300);
  };

  const blink = () => {
    if (isBlinking) return;
    setIsBlinking(true);
    
    animateElement(leftEyeRef.current, { ry: 2 }, 100);
    animateElement(rightEyeRef.current, { ry: 2 }, 100);
    
    setTimeout(() => {
      const config = EMOTIONS[currentEmotion];
      animateElement(leftEyeRef.current, { ry: config.leftEye.ry }, 100);
      animateElement(rightEyeRef.current, { ry: config.rightEye.ry }, 100);
      setIsBlinking(false);
    }, 150);
  };

  // Handle emotion changes
  useEffect(() => {
    setEmotion(emotion);
  }, [emotion]);

  // Handle talking animation
  useEffect(() => {
    if (!isTalking || !mouthRef.current) return;

    const mouth = mouthRef.current;
    const config = EMOTIONS[currentEmotion];
    const baseMouth = config.mouth;
    
    let talkInterval;
    let isOpen = false;
    
    const talkCycle = () => {
      const mouthPath = isOpen 
        ? 'M 160 260 Q 200 280 240 260'
        : 'M 170 265 Q 200 270 230 265';
      
      mouth.setAttribute('d', mouthPath);
      isOpen = !isOpen;
    };
    
    talkInterval = setInterval(talkCycle, 200);
    
    return () => {
      clearInterval(talkInterval);
      if (mouth) {
        mouth.setAttribute('d', baseMouth);
      }
    };
  }, [isTalking, currentEmotion]);

  // Random blinking
  useEffect(() => {
    const blinkInterval = setInterval(() => {
      if (Math.random() < 0.3) {
        blink();
      }
    }, 3000);

    return () => clearInterval(blinkInterval);
  }, [currentEmotion, isBlinking]);

  return (
    <div className="avatar-container">
      <div className="bella-face-container">
        <svg 
          width="120" 
          height="120" 
          viewBox="0 0 400 400" 
          className="bella-face"
        >
          <circle cx="200" cy="200" r="150" fill="none" stroke="#9ca3af" strokeWidth="2"/>
          
          <g id="leftEye">
            <ellipse 
              ref={leftEyeRef}
              cx="150" 
              cy="160" 
              rx="15" 
              ry="20" 
              fill="none" 
              stroke="white" 
              strokeWidth="3"
            />
            <circle cx="150" cy="160" r="5" fill="white"/>
          </g>
          
          <g id="rightEye">
            <ellipse 
              ref={rightEyeRef}
              cx="250" 
              cy="160" 
              rx="15" 
              ry="20" 
              fill="none" 
              stroke="white" 
              strokeWidth="3"
            />
            <circle cx="250" cy="160" r="5" fill="white"/>
          </g>
          
          <path 
            ref={mouthRef}
            d="M 150 250 Q 200 260 250 250" 
            fill="none" 
            stroke="white" 
            strokeWidth="3" 
            strokeLinecap="round"
          />
        </svg>
      </div>
      
      <div className="avatar-name">{name}</div>
    </div>
  );
};

export default Avatar;