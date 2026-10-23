
# Science RAG Project Architecture

## Overview

The Science RAG application helps students learn Class 10 Science using NCERT textbook content, previous-year question papers (PYQs), practice questions, YouTube learning resources, and uploaded PDF documents.

## System Architecture

```mermaid
flowchart TD
    A[Student] --> B[Streamlit Web Application]

    B --> C[Ask Science]
    B --> D[Practice Questions]
    B --> E[YouTube Learning]
    B --> F[Upload PDF]

    C --> G[Question Processing]
    G --> H[Sentence Transformer Embeddings]
    H --> I[(ChromaDB Vector Store)]
    I --> J[Retrieve NCERT and PYQ Context]
    J --> K[Groq LLM]
    K --> L[Answer with Source References]

    D --> M[Retrieve NCERT Context]
    M --> N[Groq LLM]
    N --> O[Practice Questions]

    E --> P[YouTube Data API v3]
    P --> Q[Video Titles and Links]

    F --> R[PyMuPDF Text Extraction]
    R --> S[Chunking and Semantic Retrieval]
    S --> T[Groq LLM]
    T --> U[PDF Answers with Page References]

    V[NCERT Textbooks] --> W[Text Extraction and Chunking]
    X[CBSE Question Papers] --> Y[Tesseract OCR]
    W --> I
    Y --> I
```

## Main Components

- **Frontend:** Streamlit web application.
- **Document processing:** Text extraction from NCERT textbooks and OCR processing for scanned question papers.
- **Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`).
- **Vector database:** ChromaDB for storing and retrieving document chunks.
- **Retrieval-Augmented Generation:** Relevant context is retrieved and passed to the Groq LLM to generate answers.
- **Practice questions:** Generates topic-based questions using NCERT context.
- **YouTube integration:** Uses the YouTube Data API v3 to find relevant learning videos.
- **PDF question answering:** Extracts text from uploaded PDFs and answers questions using relevant document context.
- **Evaluation:** Tests retrieval and answer-pipeline behavior using predefined test cases.

## Evaluation Results

- Total test cases: 6
- Retrieval checks passed: 6/6 (100%)
- Answer pipeline returned text: 6/6 (100%)
- Detailed results: `evaluation/rag_evaluation_results.csv`

These results validate the current test cases; they do not by themselves establish factual answer accuracy.

## Limitations

- Scanned PDFs may require OCR before their text can be processed.
- Answer quality depends on document quality, retrieval relevance, and LLM output.
- YouTube results depend on API availability and configuration.
