import React from 'react';
import UserMessage from './UserMessage';
import BotMessage from './BotMessage';

interface Message {
  text: string;
  isSent: boolean;
}

interface ChatBodyProps {
  messages?: Message[];
}

const ChatBody: React.FC<ChatBodyProps> = ({ messages = [] }) => {
  return (
    <div className="chat-body flex flex-col flex-1 gap-3 h-96 overflow-y-auto p-2">
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
  );
};

export default ChatBody; 