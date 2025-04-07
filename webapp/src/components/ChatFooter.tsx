import React, { useState } from 'react';

interface ChatFooterProps {
  onSendMessage?: (message: string) => void;
}

const ChatFooter: React.FC<ChatFooterProps> = ({ onSendMessage }) => {
  const [message, setMessage] = useState('');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && onSendMessage) {
      onSendMessage(message);
      setMessage('');
    }
  };
  
  return (
    <div className="chat-footer mt-3">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Type a message..."
          className="flex-1 px-4 py-3 text-sm bg-white dark:bg-gray-800 border-0 rounded-xl shadow-md placeholder:text-gray-400 focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all duration-200 ease-in-out dark:text-white hover:shadow-lg"
        />
        <button 
          type="submit"
          disabled={!message.trim()}
          className="bg-blue-500 hover:bg-blue-600 text-white rounded-lg px-4 py-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default ChatFooter; 