import os
import streamlit as st
from src.ingestion import DocumentProcessor
from src.querying import QueryProcessor
from src.utils import load_chat_history

# Page config
st.set_page_config(
    page_title="Policy Assistant",
    page_icon="📚",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        padding: 1rem;
        margin: 1rem 0;
    }
    .source-tag {
        background-color: #f0f2f6;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        margin-right: 0.5rem;
        color: black;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'doc_processor' not in st.session_state:
    st.session_state.doc_processor = DocumentProcessor()
if 'query_processor' not in st.session_state:
    api_key = os.getenv('MISTRAL_API_KEY')
    st.session_state.query_processor = QueryProcessor(api_key)

# Sidebar
with st.sidebar:
    st.title("📚 Document Management")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload Policy Documents",
        accept_multiple_files=True,
        type=['txt', 'md', 'pdf', 'doc', 'docx']
    )
    
    if uploaded_files:
        with st.spinner("Processing documents..."):
            # Save uploaded files
            for uploaded_file in uploaded_files:
                with open(os.path.join('docs', uploaded_file.name), 'wb') as f:
                    f.write(uploaded_file.getbuffer())
            
            # Process documents
            st.session_state.doc_processor.process_documents()
            st.success("Documents processed successfully!")
    
    # Process existing documents
    if st.button("Process Existing Documents"):
        with st.spinner("Processing documents..."):
            st.session_state.doc_processor.process_documents()
            st.success("Documents processed successfully!")
            
    # Show document statistics
    st.write("### Document Statistics")
    if hasattr(st.session_state.doc_processor, 'document_sources'):
        unique_docs = len(set(st.session_state.doc_processor.document_sources))
        st.write(f"📄 Processed Documents: {unique_docs}")

# Main content
st.title("Policy Assistant")
st.write("Ask questions about company policies and SOPs in natural language.")

# Query input
query = st.text_input("Ask a question:")

if query:
    with st.spinner("Searching for answer..."):
        # Get relevant document chunks
        chunks = st.session_state.doc_processor.get_relevant_chunks(query)
        
        # Process query
        result = st.session_state.query_processor.process_query(query, chunks)
        
        # Display answer in a card-like container
        st.write("### Answer")
        with st.container():
            st.markdown(result["answer"])
        
        # Display sources in a more attractive way
        if result["sources"]:
            st.write("### Sources")
            source_html = "<div style='display: flex; flex-wrap: wrap; gap: 8px;'>"
            for source in result["sources"]:
                source_html += f"<span class='source-tag'>📄 {source}</span>"
            source_html += "</div>"
            st.markdown(source_html, unsafe_allow_html=True)

# Chat history with improved display
st.write("### Chat History")
chat_history = load_chat_history()

if chat_history:
    for log in reversed(chat_history):
        with st.expander(f"❓ {log['question']}", expanded=False):
            st.markdown("#### Answer")
            st.markdown(log['answer'])
            st.markdown(f"*Asked on: {log['timestamp']}*") 
