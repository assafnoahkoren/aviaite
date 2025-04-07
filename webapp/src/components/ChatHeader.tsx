import React from 'react';

interface ChatHeaderProps {
}

const ChatHeader: React.FC<ChatHeaderProps> = (props: ChatHeaderProps) => {
  return (
    <div className="flex items-center px-4 py-3 border-b border-gray-200 bg-gray-1">
      <h1 className="text-xl font-400 text-blue-500 m-0 ">
	  	avi<span className="font-bold text-blue-600">ai</span>te
      </h1>
    </div>
  );
};

export default ChatHeader; 