import os
from typing import List, Dict
from datetime import datetime

def get_file_extension(filename: str) -> str:
    """Get the file extension from a filename."""
    return os.path.splitext(filename)[1].lower()

def is_supported_file(filename: str) -> bool:
    """Check if the file type is supported."""
    supported_extensions = {'.txt', '.md', '.pdf', '.doc', '.docx'}
    return get_file_extension(filename) in supported_extensions

def create_chat_log(question: str, answer: str) -> Dict:
    """Create a chat log entry."""
    return {
        'timestamp': datetime.now().isoformat(),
        'question': question,
        'answer': answer
    }

def save_chat_history(chat_history: List[Dict], filepath: str = 'data/chat_history.jsonl'):
    """Save chat history to a file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'a') as f:
        f.write(f"{str(chat_history[-1])}\n")

def load_chat_history(filepath: str = 'data/chat_history.jsonl') -> List[Dict]:
    """Load chat history from file."""
    if not os.path.exists(filepath):
        return []
    
    chat_history = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.strip():
                chat_history.append(eval(line.strip()))
    return chat_history 