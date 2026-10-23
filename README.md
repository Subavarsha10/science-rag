
# 📘 Science RAG Tutor

An AI-powered Class 10 Science learning assistant that uses
Retrieval-Augmented Generation (RAG) to answer questions from NCERT
textbooks and CBSE previous-year question papers.

The application also generates practice questions, searches YouTube
for educational videos, and answers questions about uploaded PDFs.

## Features

### 1. NCERT Question Answering
- Retrieves relevant passages from Class 10 Science textbooks.
- Generates student-friendly explanations using an LLM.
- Displays source references where available.

### 2. Previous-Year Questions
- Extracts text from CBSE Science question papers using OCR.
- Stores question chunks in a ChromaDB vector database.
- Retrieves relevant past-paper material.

### 3. Practice Question Generator
- Generates original Science practice questions.
- Supports easy, medium, hard, and mixed difficulty levels.
- Includes answers and explanations.

### 4. YouTube Learning
- Searches educational videos using YouTube Data API v3.
- Displays video titles, channel names, thumbnails, and links.

### 5. PDF Question Answering
- Accepts text-based PDF uploads.
- Retrieves relevant document passages for individual questions.
- Supports batch processing to answer questions across a PDF.
- Provides page references for retrieved passages.

### 6. Evaluation
- Tests NCERT and PYQ retrieval.
- Checks source-type handling and answer generation.
- Records test results in CSV format.

## Technology Stack

- Python
- Streamlit
- Retrieval-Augmented Generation (RAG)
- ChromaDB
- Sentence Transformers
- all-MiniLM-L6-v2 embeddings
- Groq API for language-model responses
- PyMuPDF for PDF text extraction
- Tesseract OCR for scanned question papers
- YouTube Data API v3

## Project Structure

```text
science-rag/
├── app.py
├── src/
│   ├── rag.py
│   ├── retrieve.py
│   ├── llm.py
│   ├── chunk_text.py
│   ├── create_vectorstore.py
│   ├── practice.py
│   ├── youtube_search.py
│   ├── pdf_qa.py
│   ├── add_pyq_to_vectorstore.py
│   └── evaluate_rag.py
├── data/
│   ├── raw/
│   │   ├── ncert/
│   │   └── pyq/
│   ├── processed/
│   └── chunks/
├── vectorstore/
├── evaluation/
├── .env
├── .gitignore
└── README.md
```

*This structure describes the intended organization; update it if your
actual project files differ.*

## Requirements

- Python 3.12 or a compatible Python version
- Internet access for Groq and YouTube API requests
- A Groq API key
- A YouTube Data API v3 key

## Installation

Clone the repository or open the project folder.

Create and activate a virtual environment if one does not already exist.

Install the required packages:

```bash
python -m pip install streamlit chromadb sentence-transformers groq python-dotenv PyMuPDF google-api-python-client
```

If OCR is required, install Tesseract OCR separately and ensure it is
available to your Python environment.

## Environment Variables

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_groq_api_key
YOUTUBE_API_KEY=your_youtube_api_key
```

Use the exact variable names expected by your `src/llm.py` and
`src/youtube_search.py` implementations.

**Never upload your real API keys to a public repository.**

## Run the Application

From the project root:

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually:

```text
http://localhost:8501
```

## Run Evaluation

Run the evaluation script:

```bash
python -m src.evaluate_rag
```

Detailed results are written to:

```text
evaluation/rag_evaluation_results.csv
```

Review retrieval quality, answer relevance, source correctness, and
errors manually before reporting performance metrics.

## How RAG Works

1. Source PDFs are converted into text.
2. Text is divided into manageable chunks.
3. Sentence Transformers converts chunks into embeddings.
4. Embeddings are stored in ChromaDB.
5. A user's question is embedded and matched against stored chunks.
6. Retrieved context is sent to the language model.
7. The generated answer and available source references are displayed.

## Limitations

- OCR can introduce errors in scanned question papers.
- Retrieval quality depends on chunking, embeddings, and query wording.
- Generated answers may contain errors and require verification.
- PDF batch processing can take time and use API quota.
- Uploaded PDFs are processed in memory and are not automatically added
  to the permanent ChromaDB collection.
- YouTube results depend on the availability and quota of the API.

## Future Improvements

- Improve retrieval ranking and evaluation.
- Add OCR support for uploaded scanned PDFs.
- Cache PDF extraction and embeddings for faster repeated questions.
- Add user feedback and answer-quality assessment.
- Deploy the application to a suitable hosting platform.

## Academic Use

This project is intended as an educational assistant. Students should
verify generated answers against their textbook, teacher guidance, and
official examination materials.
