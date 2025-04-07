import React from 'react';

interface BotMessageProps {
  text: string;
}

const BotMessage: React.FC<BotMessageProps> = ({ text }) => (
  <div className="message-received bg-gray-100 dark:bg-gray-700 rounded-lg p-x3 max-w-[80%] self-start">
    <p className="text-sm text-gray-800 dark:text-gray-200">{text}</p>
  </div>
);

export default BotMessage; 