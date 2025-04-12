import { SemanticSearchResponse } from '../types/semanticSearch';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class SemanticSearchService {
  static async search(query: string): Promise<SemanticSearchResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data as SemanticSearchResponse;
    } catch (error) {
      console.error('Error performing semantic search:', error);
      throw error;
    }
  }

  static async stream_search(
    query: string,
    onChunk: (chunk: string) => void,
    temperature: number = 0.7,
    language: string = "ENGLISH",
    length: string = "SHORT"
  ): Promise<void> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          temperature,
          language,
          length
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }

        const chunk = decoder.decode(value);
        onChunk(chunk);
      }
    } catch (error) {
      console.error('Error performing streaming search:', error);
      throw error;
    }
  }
} 