import React, { useState } from 'react';
import ChatBody from './ChatBody';
import ChatFooter from './ChatFooter';
import ChatHeader from './ChatHeader';
import { SemanticSearchService } from '../services/semanticSearchService';
import type { SemanticSearchResponse } from '../types/semanticSearch';

interface Message {
  text: string;
  isSent: boolean;
  searchResults?: SemanticSearchResponse;
}

interface ChatProps {
  // Add props here as needed
}

const Chat: React.FC<ChatProps> = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const handleSendMessage = async (message: string) => {
    // Add user message
    setMessages(prev => [...prev, { text: message, isSent: true }]);
    setIsLoading(true);

    try {
      // Get semantic search results
      const searchResults = await SemanticSearchService.search(message);
      
      // Add bot response with search results
      setMessages(prev => [...prev, { 
        text: searchResults.analysis.answer || "I couldn't find a specific answer to your question.", 
        isSent: false,
        searchResults
      }]);
    } catch (error) {
      // Add error message
      setMessages(prev => [...prev, { 
        text: "Sorry, I encountered an error while searching. Please try again.", 
        isSent: false 
      }]);
      console.error('Error in semantic search:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="flex flex-col w-full h-dvh">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow flex flex-col h-full">
        <ChatHeader />
        <div className="flex-1 overflow-hidden">
          <ChatBody messages={messages} />
        </div>
        <ChatFooter onSendMessage={handleSendMessage} isLoading={isLoading} />
      </div>
    </div>
  );
};

export default Chat; 