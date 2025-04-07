import React, { useState } from 'react';
import { IconSend } from '@tabler/icons-react';
import './ChatFooter.scss';

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
    <div className="chat-footer">
      <form onSubmit={handleSubmit} className="message-form">
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask anything..."
          className="message-input"
        />
        <button 
          type="submit"
          className="send-button"
        >
          <IconSend size={20} />
        </button>
      </form>
    </div>
  );
};

export default ChatFooter; 