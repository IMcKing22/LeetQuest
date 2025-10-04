import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import TopicSelection from './components/TopicSelection';
import StoryScreen from './components/StoryScreen';
import ChoiceScreen from './components/ChoiceScreen';
import ProblemScreen from './components/ProblemScreen';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Routes>
          <Route path="/" element={<TopicSelection />} />
          <Route path="/story" element={<StoryScreen />} />
          <Route path="/choice" element={<ChoiceScreen />} />
          <Route path="/problem" element={<ProblemScreen />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
