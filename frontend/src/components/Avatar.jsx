import React from 'react';
import './Avatar.css';

const Avatar = () => {
  return (
    <div className="avatar-container">
      <div className="avatar">
        <div className="avatar-face">
          <div className="avatar-eyes">
            <div className="eye"></div>
            <div className="eye"></div>
          </div>
          <div className="avatar-smile"></div>
        </div>
      </div>
      <div className="avatar-name">CodeMaster</div>
    </div>
  );
};

export default Avatar;
