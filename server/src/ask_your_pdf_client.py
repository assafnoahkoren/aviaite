import os
import requests
from typing import List, Dict, Any, Generator
from dotenv import load_dotenv

class AskYourPdfClient:
    def __init__(self):
        self.api_key = os.getenv('ASK_YOUR_PDF_API_KEY')
        self.knowledge_base_id = os.getenv('ASK_YOUR_PDF_KNOWLEDGE_BASE_ID')
        self.base_url = 'https://api.askyourpdf.com/v1/api'
        
        if not self.api_key:
            raise ValueError("ASK_YOUR_PDF_API_KEY environment variable is not set")
        if not self.knowledge_base_id:
            raise ValueError("ASK_YOUR_PDF_KNOWLEDGE_BASE_ID environment variable is not set")
            
        self.headers = {
            'x-api-key': self.api_key,
            'Content-Type': 'application/json'
        }

    def ask_knowledge_base(self, query: str, stream: bool = True, temperature: float = 0.7, 
                          language: str = "ENGLISH", length: str = "SHORT") -> Generator[str, None, None]:
        url = f"{self.base_url}/knowledge_base_chat"
        
        payload = {
            "documents": ["f64ec15d-8420-4245-a463-297ca89b44cf"],
            "messages": [
                {
                    "sender": "user",
                    "message": query
                }
            ]
        }
        
        params = {
            "stream": stream,
            "temperature": temperature,
            "language": language,
            "length": length
        }
        
        with requests.post(url, headers=self.headers, json=payload, params=params, stream=True) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if line:
                    yield line.decode('utf-8')


def main():
    # Load environment variables from .env file
    load_dotenv()
    
    try:
        # Initialize the client
        client = AskYourPdfClient()
        
        # Test knowledge base query
        print("Testing knowledge base query:")
        query = "When should I send the RCL message?"
        print(f"Query: {query}")
        
        print("\nResponse (streaming):")
        for chunk in client.ask_knowledge_base(query):
            print(chunk, end='', flush=True)
        print()  # New line after streaming
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 