import os
import logging
from pathlib import Path
import PyPDF2
import nltk
from nltk.tokenize import sent_tokenize
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings  # Updated import
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_groq import ChatGroq

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

def process_pdf(pdf_document):
    pdf_path = pdf_document.file.path  # Correct file path
    
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

    # Use updated HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = FAISS.from_texts(chunks, embeddings)

    logger.info("Created FAISS vector store")

    # Save FAISS index
    index_path = FAISS_INDEX_DIR / f"faiss_index_{pdf_document.id}"
    vector_store.save_local(str(index_path))

    logger.info(f"Saved FAISS index to {index_path}")

def generate_response(user_input, user):
    vector_stores = []
    
    for pdf in user.pdfdocument_set.all():
        faiss_index_path = FAISS_INDEX_DIR / f"faiss_index_{pdf.id}"

        if faiss_index_path.exists():
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            vector_store = FAISS.load_local(str(faiss_index_path), embeddings, allow_dangerous_deserialization=True)
            vector_stores.append(vector_store)
        else:
            logger.warning(f"FAISS index file not found for PDF {pdf.id}")

    if not vector_stores:
        raise ValueError("No vector stores found!")

    main_vector_store = vector_stores[0]
    for vs in vector_stores[1:]:
        main_vector_store.merge_from(vs)

    # Set up memory for conversational chain
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

    # Initialize Groq client for the language model
    llm = ChatGroq(
        groq_api_key=os.environ.get("GROQ_API_KEY"),
        model_name="llama3-70b-8192",
        temperature=0.7,
        max_tokens=1000,
    )

    # Create conversational retrieval chain
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
