import requests
import json

def get_model(prompt):
    """
    Connects to the local Ollama server running Llama 3.2.
    """
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    }
    
    try:
        # This sends the prompt to the Ollama app running on your PC
        response = requests.post(url, json=payload, timeout=90)
        
        if response.status_code == 200:
            return response.json().get('response', "Error: AI response was empty.")
        else:
            return f"Ollama Error: Status {response.status_code}. Ensure Ollama is running."
            
    except Exception as e:
        return "⚠️ CONNECTION ERROR: Is the Ollama app open in your system tray?"