import React from 'react';
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
      <div className="welcome-content text-gray-500 bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
			Welcome to your flight guide. Feel free to ask me anything.
      </div>
      
      <div className="sample-questions">
        <div className="flex items-center gap-4 my-2">
          <div className="h-px flex-1 bg-gray-300 dark:bg-gray-600"></div>
          <h2>Try asking me</h2>
          <div className="h-px flex-1 bg-gray-300 dark:bg-gray-600"></div>
        </div>
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