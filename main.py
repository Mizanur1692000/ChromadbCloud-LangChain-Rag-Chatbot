import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from PyPDF2 import PdfReader
import uvicorn
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
from langchain.chains import RetrievalQA
import chromadb

# --- Load environment variables ---
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY")
CHROMA_TENANT = os.getenv("CHROMA_TENANT")
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "gemini-embedding-001")
GENERATION_MODEL = os.getenv("GENERATION_MODEL", "gemini-2.5-flash")

if not all([GOOGLE_API_KEY, CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE]):
    raise RuntimeError("Please set all required variables in your .env file.")

# --- Initialize embeddings and generator ---
embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, api_key=GOOGLE_API_KEY)
generator = GoogleGenerativeAI(model=GENERATION_MODEL, api_key=GOOGLE_API_KEY)

# --- FastAPI app ---
app = FastAPI(title="LangChain + Gemini + Chroma PDF Knowledge Base")

# --- PDF Helpers ---
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.strip()

def chunk_text(text: str, max_chars: int = 2000):
    if len(text) <= max_chars:
        yield text
        return
    start = 0
    while start < len(text):
        end = start + max_chars
        yield text[start:end]
        start = end

# --- Initialize Chroma Cloud client ---
client = chromadb.CloudClient(
    tenant=CHROMA_TENANT,
    database=CHROMA_DATABASE,
    api_key=CHROMA_API_KEY
)

COLLECTION_NAME = "Rag_Chatbot_Collection"

# --- Serve Frontend ---
@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: index.html not found</h1>", status_code=404)

# --- Upload PDF Endpoint ---
@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    temp_file_path = f"temp_{uuid.uuid4().hex}.pdf"
    deletion_report = {}
    
    try:
        # Save PDF temporarily
        with open(temp_file_path, "wb") as f:
            f.write(await file.read())
        
        text_content = extract_text_from_pdf(temp_file_path)
        
        if not text_content:
            return {"status": "error", "message": "No extractable text found in PDF."}
        
        # Chunk text
        docs = [Document(page_content=chunk, metadata={"filename": file.filename, "chunk_index": i})
                for i, chunk in enumerate(chunk_text(text_content))]
        
        # --- Delete previous embeddings by deleting the collection ---
        try:
            client.delete_collection(name=COLLECTION_NAME)
            deletion_report["deleted_previous_collection"] = True
        except Exception as e_del:
            deletion_report["deleted_previous_collection"] = False
            deletion_report["error"] = str(e_del)
        
        # --- Recreate collection with new documents ---
        vectorstore = Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            client=client
        )
        
        return {
            "status": "success",
            "message": f"PDF '{file.filename}' uploaded and stored. Previous embeddings cleared.",
            "doc_count": len(docs),
            "deletion_report": deletion_report
        }
    
    except Exception as e:
        return {"status": "error", "message": str(e), "deletion_report": deletion_report}
    
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# --- Query Endpoint ---
@app.post("/query")
async def query_collection(question: str = Form(...), top_k: int = Form(3)):
    try:
        vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            client=client
        )
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=generator,
            retriever=vectorstore.as_retriever(search_kwargs={"k": top_k}),
            return_source_documents=True
        )
        
        # Call the chain and get dictionary output
        result_dict = qa_chain({"query": question})
        answer = result_dict.get("result", "")
        sources_docs = result_dict.get("source_documents", [])
        sources = [doc.metadata for doc in sources_docs]
        
        return {"status": "success", "query": question, "answer": answer, "sources": sources}
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- Run app ---
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
    