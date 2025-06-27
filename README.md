# Policy & SOP Discovery AI Assistant

An AI-powered assistant that helps employees find information from internal policy documents and SOPs using natural language queries.

## Features

- Document ingestion from local folders
- Natural language querying
- Context-aware responses
- Chat history logging
- Support for multiple document types
- Clean web interface using Streamlit
- Offline-capable using local embeddings

## Setup Instructions

1. Clone the repository
```bash
git clone <your-repo-url>
cd megatron
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Place your documents in the `docs` folder

5. Run the application
```bash
streamlit run app.py
```

## Usage

1. Upload your policy documents through the web interface
2. Ask questions in natural language, such as:
   - "What is the leave policy?"
   - "How many vacation days do I get per year?"
   - "Is there a policy for remote work reimbursement?"

## Technical Details

- Uses Mistral AI for text processing
- Implements FAISS for efficient vector similarity search
- Sentence transformers for document embeddings
- Streamlit for the web interface

## Project Structure

```
megatron/
├── app.py              # Main Streamlit application
├── src/
│   ├── ingestion.py    # Document ingestion logic
│   ├── querying.py     # Query processing
│   └── utils.py        # Helper functions
├── docs/              # Sample documents folder
├── data/              # Processed data and embeddings
└── requirements.txt   # Project dependencies
```

## Contributing

Feel free to submit issues and enhancement requests! 