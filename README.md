# LangChain + Gemini + Chroma PDF Knowledge Base

## Overview

Welcome to the **LangChain + Gemini + Chroma PDF Knowledge Base**! This application is a powerful tool that uses the **LangChain** framework, **Google Gemini AI models**, and **Chroma** for building a sophisticated knowledge base from PDF documents. It allows you to upload PDFs, extract their content, store it as embeddings, and then query that stored content for insightful, AI-generated answers.

Whether you're building a knowledge base, enhancing your document management system, or just curious about AI-powered querying, this app provides a seamless solution by combining advanced PDF processing, language models, and efficient vector storage with Chroma.

### Key Features

- **PDF Text Extraction**: Easily upload and extract textual content from PDF files.
- **AI-Enhanced Querying**: Use Google’s Gemini AI to process and generate embeddings for better search and retrieval.
- **Fast, Scalable Backend**: Powered by **FastAPI**, providing an efficient API for interacting with your knowledge base.
- **Automatic Embedding Storage**: Chunks of extracted text are stored as embeddings in **Chroma**, a vector database, making searches and queries fast and effective.
- **Dynamic Question Answering**: Ask any question about the content, and the app will fetch relevant answers from the knowledge base using a retrieval-based model.

## Technologies

This application integrates several cutting-edge technologies:

- **FastAPI**: A modern web framework for building APIs that’s easy to use and fast in performance.
- **Google Generative AI**: Leverages Google's AI models for generating text embeddings and producing responses.
- **Chroma**: A vector database for storing and retrieving embeddings, optimizing query performance.
- **LangChain**: A library that integrates language models and chains for powerful AI workflows.
- **PyPDF2**: Used for extracting text from PDF files in the application.
- **Uvicorn**: An ASGI server that runs the FastAPI application efficiently.

## Prerequisites

Before running this application, you need to set up the following:

1. **Environment Variables**: Create a `.env` file in your project root and add the following keys:
   - `GOOGLE_API_KEY`: Your API key for Google's services (for embeddings and text generation).
   - `CHROMA_API_KEY`: Your API key for Chroma (the vector database).
   - `CHROMA_TENANT`: Your Chroma tenant ID.
   - `CHROMA_DATABASE`: The name of the Chroma database you're using.
   - `EMBEDDING_MODEL`: (Optional) The model for embeddings (default: `gemini-embedding-001`).
   - `GENERATION_MODEL`: (Optional) The model used for generating responses (default: `gemini-2.5-flash`).

2. **Dependencies**: Install the required libraries by running:
   ```bash
   pip install -r requirements.txt
###You’ll need the following dependencies:

1. fastapi
2. uvicorn
3. langchain
4. langchain-google-genai
5. chromadb
6. PyPDF2
7. python-dotenv

##Installation
Follow these steps to get the application up and running:

Clone the Repository:

bash
Copy code
git clone https://github.com/yourusername/langchain-gemini-chroma-pdf-knowledge-base.git
cd langchain-gemini-chroma-pdf-knowledge-base
Install Dependencies:

bash
Copy code
pip install -r requirements.txt
Set up Environment Variables:
Create a .env file in the project root and fill in the required Google and Chroma API keys and configurations.
In th environment need to add:
1. GOOGLE_API_KEY
2. CHROMA_API_KEY
3. CHROMA_TENANT
4. CHROMA_DATABASE
5. EMBEDDING_MODEL
6. GENERATION_MODEL

Running the Application
Once you’ve configured the environment variables and installed the dependencies, you can run the app with:

bash
Copy code
uvicorn main:app --reload  
This will start the FastAPI application on your local machine at http://127.0.0.1:8000.

Endpoints
The application provides two main API endpoints:

###1. Upload PDF - /upload_pdf
Method: POST

Parameters:

file: The PDF file you want to upload.

Description: Upload a PDF document, extract its text, chunk it into smaller parts, and store the chunks as embeddings in Chroma. Previous embeddings will be cleared, and new embeddings will be created.

Example:

bash
Copy code
curl -X 'POST' \
  'http://127.0.0.1:8000/upload_pdf' \
  -F 'file=@yourfile.pdf'
Response:

json
Copy code
{
  "status": "success",
  "message": "PDF 'yourfile.pdf' uploaded and stored.",
  "doc_count": 10,
  "deletion_report": {"deleted_previous_collection": true}
}
###2. Query Knowledge Base - /query
Method: POST

Parameters:

question: The question you want to ask about the uploaded documents.

top_k: (Optional) The number of relevant documents to return (default is 3).

Description: Submit a question, and the system will search the stored embeddings to find the most relevant chunks of text, and return an AI-generated response.

Example:

bash
Copy code
curl -X 'POST' \
  'http://127.0.0.1:8000/query' \
  -F 'question=What is the main topic of the document?' \
  -F 'top_k=3'
Response:

json
Copy code
{
  "status": "success",
  "query": "What is the main topic of the document?",
  "answer": "The main topic is related to AI models and natural language processing.",
  "sources": [
    {"filename": "yourfile.pdf", "chunk_index": 2}
  ]
}
###3. Frontend Interface - /
Method: GET

Description: The homepage serves an HTML interface for users to upload PDFs and submit queries. This is a simple frontend for interacting with the backend API.

Files and Directory Structure
Here’s a quick rundown of the project structure:

main.py: The core FastAPI app file that defines the logic for uploading PDFs, querying the knowledge base, and interacting with Chroma and Google APIs.

index.html: A simple HTML file served by FastAPI for user interaction.

.env: Your environment configuration file, where API keys and settings are stored.

requirements.txt: A list of dependencies needed to run the project.

Troubleshooting
Missing index.html: If the app can’t find the index.html file, ensure it's present in the root directory.

API Errors: If there are issues with uploading PDFs or querying the knowledge base, check your environment variables to ensure all API keys are correctly set.

Contributing
Contributions are always welcome! If you have ideas for improvements or find bugs, feel free to fork the repository, create an issue, or submit a pull request.

License
This project is licensed under the MIT License. See the LICENSE file for more information.

