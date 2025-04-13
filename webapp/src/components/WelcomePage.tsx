import React, { useRef } from 'react';
import './WelcomePage.scss';

interface WelcomePageProps {
  onQuestionSelect?: (question: string) => void;
}

const sampleQuestions = [
  "What are the hours for the westbound tracks?",
  "What are the navigation performance requirements for the NAT?",
  "Is datalink a requirement for flying the NAT?",
  "What is the Gander transition area?",
  "When should I send the RCL message?"
];

const WelcomePage: React.FC<WelcomePageProps> = ({ onQuestionSelect }) => {
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleQuestionSelect = (question: string) => {
    const inputElement = document.getElementById('message-input') as HTMLInputElement;
    if (inputElement) {
      // Create and dispatch a proper React input event
      const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
        window.HTMLInputElement.prototype,
        "value"
      )?.set;
      
      if (nativeInputValueSetter) {
        nativeInputValueSetter.call(inputElement, question);
        const inputEvent = new Event('input', { bubbles: true });
        inputElement.dispatchEvent(inputEvent);
        
        // Also trigger change event to ensure state updates
        const changeEvent = new Event('change', { bubbles: true });
        inputElement.dispatchEvent(changeEvent);
      }
    }
    // Call the optional callback if provided
    onQuestionSelect?.(question);
  };

  return (
    <div className="welcome-page">
      <div className="welcome-content">
        <h1>Welcome to Our Assistant</h1>
        <p className="explanation">
          I'm here to help you learn more about our platform. Feel free to ask me anything,
          or try one of the sample questions below to get started.
        </p>
      </div>
      
      <div className="sample-questions">
        <h2>Try asking me:</h2>
        <div className="chips-container">
          {sampleQuestions.map((question, index) => (
            <button
              key={index}
              className="question-chip"
              onClick={() => handleQuestionSelect(question)}
            >
              {question}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WelcomePage; 