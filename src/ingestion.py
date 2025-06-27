import os
from typing import List, Dict
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import TextLoader, PDFMinerLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.utils import is_supported_file

class DocumentProcessor:
    def __init__(self, docs_dir: str = 'docs', data_dir: str = 'data'):
        self.docs_dir = docs_dir
        self.data_dir = data_dir
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        self.index = None
        self.documents = []
        self.document_sources = []
        
        os.makedirs(self.data_dir, exist_ok=True)
        
    def load_documents(self) -> List[str]:
        documents = []
        sources = []
        
        for filename in os.listdir(self.docs_dir):
            if not is_supported_file(filename):
                continue
                
            filepath = os.path.join(self.docs_dir, filename)
            try:
                if filename.endswith('.txt'):
                    loader = TextLoader(filepath)
                elif filename.endswith('.pdf'):
                    loader = PDFMinerLoader(filepath)
                else:
                    continue
                    
                docs = loader.load()
                for doc in docs:
                    if hasattr(doc, 'page_content'):
                        documents.append(doc)
                        sources.append(filename)
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
                
        self.document_sources = sources
        return documents
    
    def process_documents(self):
        documents = self.load_documents()
        if not documents:
            return
            
        chunks = []
        chunk_sources = []
        for doc, source in zip(documents, self.document_sources):
            if hasattr(doc, 'page_content'):
                doc_chunks = self.text_splitter.split_text(doc.page_content)
                chunks.extend(doc_chunks)
                chunk_sources.extend([source] * len(doc_chunks))
        
        self.documents = chunks
        self.document_sources = chunk_sources
        
        embeddings = self.model.encode(chunks, convert_to_numpy=True)
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        self.save_processed_data()
        
    def save_processed_data(self):
        if self.index is not None:
            faiss.write_index(self.index, os.path.join(self.data_dir, 'document_index.faiss'))
            
        if self.documents:
            with open(os.path.join(self.data_dir, 'documents.txt'), 'w', encoding='utf-8') as f:
                for doc, source in zip(self.documents, self.document_sources):
                    f.write(f"SOURCE: {source}\n")
                    f.write(doc + '\n')
                    f.write("===\n")
                    
    def load_processed_data(self) -> bool:
        index_path = os.path.join(self.data_dir, 'document_index.faiss')
        docs_path = os.path.join(self.data_dir, 'documents.txt')
        
        if not (os.path.exists(index_path) and os.path.exists(docs_path)):
            return False
            
        try:
            self.index = faiss.read_index(index_path)
            
            self.documents = []
            self.document_sources = []
            current_doc = []
            current_source = None
            
            with open(docs_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith("SOURCE: "):
                        current_source = line[8:].strip()
                    elif line.strip() == "===":
                        if current_doc and current_source:
                            self.documents.append(''.join(current_doc))
                            self.document_sources.append(current_source)
                            current_doc = []
                    else:
                        current_doc.append(line)
                        
            if current_doc and current_source:
                self.documents.append(''.join(current_doc))
                self.document_sources.append(current_source)
                
            return True
        except Exception as e:
            print(f"Error loading processed data: {str(e)}")
            return False
            
    def get_relevant_chunks(self, query: str, k: int = 3) -> List[Dict[str, str]]:
        if self.index is None:
            return []
            
        query_embedding = self.model.encode([query], convert_to_numpy=True)[0].reshape(1, -1)
        D, I = self.index.search(query_embedding.astype('float32'), k)
        
        results = []
        for idx in I[0]:
            results.append({
                'content': self.documents[idx],
                'source': self.document_sources[idx]
            })
            
        return results 