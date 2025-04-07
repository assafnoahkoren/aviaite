import React from 'react';

interface UserMessageProps {
  text: string;
}

const UserMessage: React.FC<UserMessageProps> = ({ text }) => (
  <div className="message-sent bg-blue-500 dark:bg-blue-600 rounded-lg p-x3 max-w-[80%] self-end text-white">
    <p className="text-sm">{text}</p>
  </div>
);

export default UserMessage; 