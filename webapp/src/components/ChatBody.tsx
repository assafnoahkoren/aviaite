import React from 'react';

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
          <div className="message-received bg-gray-100 dark:bg-gray-700 rounded-lg p-3 max-w-[80%] self-start">
            <p className="text-sm text-gray-800 dark:text-gray-200">Hello! How can I help you today?</p>
          </div>
          
          <div className="message-sent bg-blue-500 dark:bg-blue-600 rounded-lg p-3 max-w-[80%] self-end text-white">
            <p className="text-sm">I'm just checking out this new chat component!</p>
          </div>
        </>
      ) : (
        <>
          {messages.map((message, index) => (
            <div 
              key={index} 
              className={`${
                message.isSent 
                  ? "message-sent bg-blue-500 dark:bg-blue-600 text-white self-end" 
                  : "message-received bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 self-start"
              } rounded-lg p-3 max-w-[80%]`}
            >
              <p className="text-sm">{message.text}</p>
            </div>
          ))}
        </>
      )}
    </div>
  );
};

export default ChatBody; 