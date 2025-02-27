import os
import logging
from pathlib import Path
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq
from accounts.models import PDFDocument

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

#  Set custom NLTK data directory
BASE_DIR = Path(__file__).resolve().parent.parent
NLTK_DATA_DIR = BASE_DIR / "nltk_data"

# Ensure the directory exists
os.makedirs(NLTK_DATA_DIR, exist_ok=True)

# Add to nltk data path
nltk.data.path.append(str(NLTK_DATA_DIR))

# Download 'punkt' if not available
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    logger.info("Downloading NLTK 'punkt' tokenizer...")
    nltk.download("punkt", download_dir=str(NLTK_DATA_DIR))

#  Define paths
MEDIA_DIR = BASE_DIR / "media"
PDF_DIR = MEDIA_DIR / "pdfs"
FAISS_INDEX_DIR = MEDIA_DIR / "faiss_indexes"

# Ensure necessary directories exist
PDF_DIR.mkdir(parents=True, exist_ok=True)
FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)

def process_pdf(pdf_document):
    """Extracts text from a PDF file, splits it into chunks, and stores embeddings in FAISS."""
    pdf_path = pdf_document.file.path  # Correct file path
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    logger.info(f"Processing PDF: {pdf_path}")
    
    #  Read PDF text
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_path)
        text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
    except Exception as e:
        raise RuntimeError(f"Error reading PDF: {str(e)}")

    if not text.strip():
        raise ValueError("Failed to extract text from the PDF.")

    logger.info(f"Extracted {len(text)} characters from the PDF")
    
    #  Split text into chunks
    sentences = sent_tokenize(text)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(" ".join(sentences))

    if not chunks:
        raise ValueError("No text chunks generated for FAISS index.")

    logger.info(f"Split text into {len(chunks)} chunks")

    #  Generate embeddings and store in FAISS
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embeddings)
    
    logger.info("Created FAISS vector store")
    
    #  Save FAISS index
    index_path = FAISS_INDEX_DIR / f"faiss_index_{pdf_document.id}"
    vector_store.save_local(str(index_path))
    
    logger.info(f"Saved FAISS index to {index_path}")

def generate_response(user_input, context=None):
    """Generates a response using FAISS and Groq's Llama-3 model."""
    vector_stores = []
    
    for pdf in PDFDocument.objects.all():
        faiss_index_path = FAISS_INDEX_DIR / f"faiss_index_{pdf.id}"
        
        if faiss_index_path.exists():
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            try:
                vector_store = FAISS.load_local(str(faiss_index_path), embeddings, allow_dangerous_deserialization=True)
                vector_stores.append(vector_store)
            except Exception as e:
                logger.error(f"Error loading FAISS index for PDF {pdf.id}: {str(e)}")
        else:
            logger.warning(f"FAISS index file not found for PDF {pdf.id}")

    if not vector_stores:
        raise ValueError("No vector stores found!")

    #  Merge all FAISS vector stores
    main_vector_store = vector_stores[0]
    for vs in vector_stores[1:]:
        main_vector_store.merge_from(vs)

    #  Set up memory for conversational chain
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    
    #  Ensure API key is available
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")

    #  Initialize Groq client for the language model
    llm = ChatGroq(
        groq_api_key=groq_api_key,
        model_name="llama3-70b-8192",
        temperature=0.7,
        max_tokens=1000,
    )

    #  Create conversational retrieval chain
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=main_vector_store.as_retriever(search_kwargs={"k": 5}),
        memory=memory
    )

    try:
        response = qa({"question": user_input})
        return response['answer']
    except Exception as e:
        logger.error(f"Error during response generation: {str(e)}")
        return "Sorry, I couldn't process your request at the moment."
