import React from 'react';
import type { SemanticSearchResponse } from '../types/semanticSearch';
import Markdown from 'react-markdown'
import { IconBook, IconBook2, IconFileText } from '@tabler/icons-react';

interface Source {
  page: number;
  quote: string;
}

interface BotMessageProps {
  text: string;
  searchResults?: SemanticSearchResponse;
}

const parseMessage = (text: string | undefined): { answer: string; sources: Source[] } => {
  if (!text) {
    return {
      answer: '',
      sources: []
    };
  }
  
  const [answer, sourcesText] = text.split(/SOURCES:?/);
  
  const sources: Source[] = [];
  if (sourcesText) {
    const sourceLines = sourcesText.split('\n').filter(line => line.trim().startsWith('-'));
    sources.push(...sourceLines.map(line => {
      const match = line.match(/Page (\d+): "(.*?)"/);
      if (match) {
        return {
          page: parseInt(match[1]),
          quote: match[2]
        };
      }
      return null;
    }).filter((source): source is Source => source !== null));
  }

  return {
    answer: answer.trim(),
    sources
  };
};

const BotMessage: React.FC<BotMessageProps> = ({ text, searchResults }) => {
  const { answer, sources } = parseMessage(text);
  
  return (
    <div className="flex flex-col p-4">
      <div className="bg-blue-200 dark:bg-blue-900 px-3 rounded-t-lg max-w-[90%] self-start">
        <p className="text-left text-gray-800 dark:text-gray-200">
          <Markdown>{answer}</Markdown>
        </p>
      </div>
      {sources.length > 0 && (
        <div className="bg-blue-100 dark:bg-gray-800 px-3 rounded-b-lg max-w-[90%] self-start">
          <div className="flex items-center gap-4 my-2 mt-4">
            <div className="h-px flex-1 bg-blue-300 dark:bg-gray-600"></div>
            <p className="text-center text-gray-600 dark:text-gray-300 text-sm flex items-center gap-1 m-0">
              <IconBook2 size={16} />
              Sources
            </p>
            <div className="h-px flex-1 bg-blue-300 dark:bg-gray-600"></div>
          </div>
          {sources.map((source, index) => (
            <div key={index} className="mt-1">
              <p className="text-left text-gray-600 dark:text-gray-300 text-sm">
                <IconFileText size={14} className="inline-block mr-1 relative top-0.5" /><b>{source.page}</b>: "{source.quote}"
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default BotMessage; 