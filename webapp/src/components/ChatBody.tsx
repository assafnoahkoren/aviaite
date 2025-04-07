import React from 'react';
import UserMessage from './UserMessage';
import BotMessage from './BotMessage';
import './ChatBody.scss';

interface Message {
  text: string;
  isSent: boolean;
}

interface ChatBodyProps {
  messages?: Message[];
}

const ChatBody: React.FC<ChatBodyProps> = ({ messages = [] }) => {
  return (
    <div className="chat-container">
      <div className="chat-body hide-scrollbar">
        {messages.length === 0 ? (
          <>
            {/* Placeholder message examples */}
            <BotMessage text="Hello! How can I help you today?" />
            <UserMessage text="I'm just checking out this new chat component!" />
          </>
        ) : (
          <>
            {messages.map((message, index) => (
              message.isSent ? 
                <UserMessage key={index} text={message.text} /> : 
                <BotMessage key={index} text={message.text} />
            ))}
          </>
        )}
      </div>
      {/* Gradient overlay for seamless scrolling effect */}
      <div className="gradient-overlay"></div>
    </div>
  );
};

export default ChatBody; 