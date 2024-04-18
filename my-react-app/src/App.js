import React, { useState } from 'react';
import axios from 'axios';
import './App.css'; // App.css 파일을 import

function App() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleQuestionChange = (event) => {
    setQuestion(event.target.value);
  };

  const handleSubmit = async () => {
    try {
      const response = await axios.post('http://192.168.1.104:7000/ask', { question });
      setAnswer(response.data.answer);
    } catch (error) {
      console.error('Error fetching the answer:', error);
      setAnswer('Failed to get the answer');
    }
  };

  return (
    <div className="App">
      <div className="chatbot-container">
        <h1>질문해주세요</h1>
        <input type="text" value={question} onChange={handleQuestionChange} placeholder="Enter your question" />
        <button onClick={handleSubmit}>Submit</button>
        <div className="answer">Answer: {answer}</div>
      </div>
    </div>
  );
}

export default App;
