import requests
import json
import os
from config.logger import logger

class OllamaService:
    def __init__(self):
        # Ollama typically runs on host machine
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://host.docker.internal:11434')
        self.default_model = os.getenv('OLLAMA_MODEL', 'llama3')
    
    def generate_response(self, prompt: str, model: str = None) -> str:
        """Generate a response using Ollama."""
        try:
            model = model or self.default_model
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response generated')
            else:
                logger(f"Ollama API error: {response.status_code} - {response.text}", 'ERROR')
                return "Sorry, I couldn't generate a response. Please try again."
                
        except requests.exceptions.RequestException as e:
            logger(f"Error connecting to Ollama: {e}", 'ERROR')
            return "Sorry, I'm having trouble connecting to the AI service. Please try again."
        except Exception as e:
            logger(f"Unexpected error in Ollama service: {e}", 'ERROR')
            return "Sorry, something went wrong. Please try again."
    
    def list_models(self) -> list:
        """List available Ollama models."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            logger(f"Error getting Ollama models: {e}", 'ERROR')
            return []
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

# Global instance
ollama_service = OllamaService()
