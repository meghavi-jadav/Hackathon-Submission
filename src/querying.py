from typing import List, Dict, Optional, Union, Any
from mistralai.client import MistralClient
from src.utils import create_chat_log, save_chat_history

class QueryProcessor:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the query processor with optional API key."""
        self.client = MistralClient(api_key=api_key) if api_key else None
        self.chat_history: List[Dict[str, Any]] = []
        
    def process_query(self, query: str, context_chunks: List[Dict[str, str]]) -> Dict[str, Union[str, List[str]]]:
        """Process a query using either Mistral API or local processing."""
        if not context_chunks:
            return {
                "answer": "I couldn't find any relevant information in the documents.",
                "sources": []
            }
            
        # Combine context chunks and track sources
        context = "\n\n".join([chunk['content'] for chunk in context_chunks])
        sources = list(set(chunk['source'] for chunk in context_chunks))
        
        if self.client:
            # Use Mistral API with improved prompt
            system_prompt = """You are a helpful AI assistant that answers questions about company policies and SOPs.
            Base your answers ONLY on the provided context. If you cannot find the answer in the context, say so.
            
            Follow these guidelines for your response:
            1. Provide a clear, well-structured answer
            2. Use bullet points or numbered lists where appropriate
            3. Break down complex information into sections
            4. Summarize key points at the end if the answer is long
            5. Be concise but comprehensive
            6. Use professional language
            7. If dates, numbers, or specific procedures are mentioned, highlight them
            
            Context: {context}"""
            
            messages = [
                {"role": "system", "content": system_prompt.format(context=context)},
                {"role": "user", "content": f"Please provide a well-structured answer to: {query}"}
            ]
            
            response = self.client.create_chat_completion(
                model="mistral-tiny",
                messages=messages
            )
            
            answer = response.choices[0].message.content
        else:
            # Local processing with basic structure
            answer = "Here's a summary of the relevant information:\n\n"
            for chunk in context_chunks:
                answer += f"From {chunk['source']}:\n"
                answer += f"• {chunk['content'].strip()}\n\n"
            
        # Log the interaction
        log_entry = create_chat_log(query, f"{answer}\n\nSources: {', '.join(sources)}")
        self.chat_history.append(log_entry)
        save_chat_history(self.chat_history)
        
        return {
            "answer": answer,
            "sources": sources
        } 