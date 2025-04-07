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
        <p className="text-left text-gray-800 dark:text-gray-200">{text}</p>
      </div>
      
      {searchResults && searchResults.results.length > 0 && (
        <div className="bg-gray-50 dark:bg-gray-700 px-3 rounded-lg max-w-[90%] self-start mt-2">
          <p className="text-sm text-gray-600 dark:text-gray-300 font-medium mb-2">
            Found {searchResults.total_results} relevant results:
          </p>
          <div className="space-y-2">
            {searchResults.results.map((result, index) => (
              <div key={result.chunk_id} className="text-sm">
                <p className=" text-gray-800 dark:text-gray-200">
                  {index + 1}. {result.chunk_text}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Similarity: {(result.similarity * 100).toFixed(1)}%
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default BotMessage; 