import React, { useState } from 'react';
import ChatBody from './ChatBody';
import ChatFooter from './ChatFooter';
import ChatHeader from './ChatHeader';

interface Message {
  text: string;
  isSent: boolean;
}

interface ChatProps {
  // Add props here as needed
}

const Chat: React.FC<ChatProps> = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  
  const handleSendMessage = (message: string) => {
    setMessages([...messages, { text: message, isSent: true }]);
    // Here you would typically also send the message to your backend
    
    // Simulate a response after 1 second
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        text: `You said: "${message}"`, 
        isSent: false 
      }]);
    }, 1000);
  };
  
  return (
    <div className="flex flex-col w-full h-dvh">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow flex flex-col h-full">
        <ChatHeader />
        <div className="flex-1 overflow-hidden">
          <ChatBody messages={messages} />
        </div>
        <ChatFooter onSendMessage={handleSendMessage} />
      </div>
    </div>
  );
};

export default Chat; 