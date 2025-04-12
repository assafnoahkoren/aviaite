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

interface ChatProps {}

const Chat: React.FC<ChatProps> = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<string>('');
  
  const handleSendMessage = async (message: string) => {
    // Add user message
    setMessages(prev => [...prev, { text: message, isSent: true }]);
    setIsLoading(true);
    setCurrentStreamingMessage('');

    try {
      // Add initial bot message with empty text
      setMessages(prev => [...prev, { 
        text: '', 
        isSent: false 
      }]);

      // Start streaming search
      await SemanticSearchService.stream_search(
        message,
        (chunk) => {
          console.log(chunk);
          
          setCurrentStreamingMessage(prev => prev + chunk);
          // Update the last message (bot's message) with the accumulated text
          setMessages(prev => {
            const newMessages = [...prev];
            const lastMessage = newMessages[newMessages.length - 1];
            if (lastMessage && !lastMessage.isSent) {
              lastMessage.text = currentStreamingMessage + chunk;
            }
            return newMessages;
          });
        }
      );
    } catch (error) {
      // Add error message
      setMessages(prev => [...prev, { 
        text: "Sorry, I encountered an error while searching. Please try again.", 
        isSent: false 
      }]);
      console.error('Error in semantic search:', error);
    } finally {
      setIsLoading(false);
      setCurrentStreamingMessage('');
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