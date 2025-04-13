import React, { useState } from 'react';
import { IconSend, IconLoader2 } from '@tabler/icons-react';
import './ChatFooter.scss';

interface ChatFooterProps {
  onSendMessage?: (message: string) => void;
  isLoading?: boolean;
}

const ChatFooter: React.FC<ChatFooterProps> = ({ onSendMessage, isLoading = false }) => {
  const [message, setMessage] = useState('');
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && onSendMessage && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };
  
  return (
    <div className="chat-footer">
      <form onSubmit={handleSubmit} className="message-form">
        <input
          type="text"
          id="message-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask anything..."
          className="message-input"
          disabled={isLoading}
        />
        <button 
          type="submit"
          className="send-button"
          disabled={isLoading}
        >
          {isLoading ? (
            <IconLoader2 size={20} className="animate-spin" />
          ) : (
            <IconSend size={20} />
          )}
        </button>
      </form>
    </div>
  );
};

export default ChatFooter; 