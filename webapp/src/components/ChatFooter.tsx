import React, { useState } from 'react';
import { IconSend } from '@tabler/icons-react';

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
    <div className="chat-footer py-3 px-2">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask anything..."
          className="flex-1 px-4 py-3 text-sm bg-gray-1 dark:bg-gray-900 border-0 rounded-full placeholder:text-gray-400 focus:outline-none transition-all duration-200 ease-in-out dark:text-white"
        />
        <button 
          type="submit"
          className="bg-blue-500 hover:bg-blue-600 text-white rounded-full w-10 h-10 flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 border-none"
        >
          <IconSend size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatFooter; 