import os
import logging
from pathlib import Path
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from accounts.models import PDFDocument

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download necessary NLTK data
nltk.download('punkt', quiet=True)

# Define paths
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"
PDF_DIR = MEDIA_DIR / "pdfs"
FAISS_INDEX_DIR = MEDIA_DIR / "faiss_indexes"

# Ensure directories exist
PDF_DIR.mkdir(parents=True, exist_ok=True)
FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)

# Global vector store
global_vector_store = None

def process_pdf(pdf_document):
    global global_vector_store
    pdf_path = pdf_document.file.path

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    logger.info(f"Processing PDF: {pdf_path}")
    
    pdf_reader = PyPDF2.PdfReader(pdf_path)
    text = "".join(page.extract_text() or "" for page in pdf_reader.pages)

    if not text.strip():
        raise ValueError("Failed to extract text from the PDF.")

    logger.info(f"Extracted {len(text)} characters from the PDF")

    sentences = sent_tokenize(text)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(" ".join(sentences))

    if not chunks:
        raise ValueError("No text chunks generated for FAISS index.")

    logger.info(f"Split text into {len(chunks)} chunks")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    if global_vector_store is None:
        global_vector_store = FAISS.from_texts(chunks, embeddings)
    else:
        global_vector_store.add_texts(chunks)

    logger.info("Updated global FAISS vector store")

def generate_response(user_input, user):
    global global_vector_store
    try:
        if global_vector_store is None:
            # Initialize the global vector store if it doesn't exist
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            all_pdfs = PDFDocument.objects.all()
            all_chunks = []
            for pdf in all_pdfs:
                pdf_reader = PyPDF2.PdfReader(pdf.file.path)
                text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
                sentences = sent_tokenize(text)
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                chunks = text_splitter.split_text(" ".join(sentences))
                all_chunks.extend(chunks)
            
            if not all_chunks:
                raise ValueError("No text chunks found in any PDF.")
            
            global_vector_store = FAISS.from_texts(all_chunks, embeddings)
            logger.info("Initialized global FAISS vector store")

        # Set up memory and LLM model
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        # Initialize the language model using Groq API
        llm = ChatGroq(
            groq_api_key=os.environ.get("GROQ_API_KEY"),
            model_name="llama3-70b-8192",
            temperature=0.7,
            max_tokens=1000,
        )

        # Create the conversational chain
        qa = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=global_vector_store.as_retriever(search_kwargs={"k": 5}),
            memory=memory
        )

        response = qa({"question": user_input})
        return response['answer']

    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return "Sorry, I couldn't process your request at the moment."

