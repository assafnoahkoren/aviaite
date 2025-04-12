import React from 'react';
import type { SemanticSearchResponse } from '../types/semanticSearch';

interface BotMessageProps {
  text: string;
  searchResults?: SemanticSearchResponse;
}

const BotMessage: React.FC<BotMessageProps> = ({ text, searchResults }) => {
  return (
    <div className="flex flex-col gap-2 p-4">
      <div className="bg-blue-100 dark:bg-blue-900 px-3 rounded-lg max-w-[90%] self-start">
        <p className="text-left text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{text}</p>
      </div>
    
    </div>
  );
};

export default BotMessage; 