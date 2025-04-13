import React, { useRef, useEffect } from 'react';
import UserMessage from './UserMessage';
import BotMessage from './BotMessage';
import WelcomePage from './WelcomePage';
import './ChatBody.scss';

interface Message {
  text: string;
  isSent: boolean;
}

interface ChatBodyProps {
  messages?: Message[];
}

const ChatBody: React.FC<ChatBodyProps> = ({ messages = [] }) => {
  const chatBodyRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="chat-container">
      <div className="chat-body hide-scrollbar" ref={chatBodyRef}>
        {messages.length === 0 ? (
          <WelcomePage />
        ) : (
          <>
            {messages.map((message, index) => (
              message.isSent ? 
                <UserMessage key={index} text={message.text} /> : 
                message.text ? <BotMessage key={index} text={message.text} /> : null
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