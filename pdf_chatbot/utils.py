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

def generate_response(user_input,context=None):
    vector_stores = []
    
    for pdf in PDFDocument.objects.all():
        faiss_index_path = FAISS_INDEX_DIR / f"faiss_index_{pdf.id}"  # Corrected path

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

    # Ensure API key is available
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set.")

    # Initialize Groq client for the language model
    llm = ChatGroq(
        groq_api_key=groq_api_key,
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



# import os
# import logging
# from pathlib import Path
# import PyPDF2
# import nltk
# from nltk.tokenize import sent_tokenize
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain.vectorstores import FAISS
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory
# from accounts.models import PDFDocument

# # Logging setup
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # Download necessary NLTK data
# nltk.download('punkt', quiet=True)

# # Define paths
# BASE_DIR = Path(__file__).resolve().parent.parent
# MEDIA_DIR = BASE_DIR / "media"
# PDF_DIR = MEDIA_DIR / "pdfs"
# FAISS_INDEX_DIR = MEDIA_DIR / "faiss_indexes"

# # Ensure directories exist
# PDF_DIR.mkdir(parents=True, exist_ok=True)
# FAISS_INDEX_DIR.mkdir(parents=True, exist_ok=True)

# # Global vector store
# global_vector_store = None

# def process_pdf(pdf_document):
#     global global_vector_store
#     pdf_path = pdf_document.file.path

#     if not os.path.exists(pdf_path):
#         raise FileNotFoundError(f"PDF file not found: {pdf_path}")

#     logger.info(f"Processing PDF: {pdf_path}")
    
#     pdf_reader = PyPDF2.PdfReader(pdf_path)
#     text = "".join(page.extract_text() or "" for page in pdf_reader.pages)

#     if not text.strip():
#         raise ValueError("Failed to extract text from the PDF.")

#     logger.info(f"Extracted {len(text)} characters from the PDF")

#     sentences = sent_tokenize(text)
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     chunks = text_splitter.split_text(" ".join(sentences))

#     if not chunks:
#         raise ValueError("No text chunks generated for FAISS index.")

#     logger.info(f"Split text into {len(chunks)} chunks")

#     embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
#     if global_vector_store is None:
#         global_vector_store = FAISS.from_texts(chunks, embeddings)
#     else:
#         global_vector_store.add_texts(chunks)

#     logger.info("Updated global FAISS vector store")

# def generate_response(user_input, user):
#     global global_vector_store
#     try:
#         if global_vector_store is None:
#             # Initialize the global vector store if it doesn't exist
#             embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
#             all_pdfs = PDFDocument.objects.all()
#             all_chunks = []
#             for pdf in all_pdfs:
#                 pdf_reader = PyPDF2.PdfReader(pdf.file.path)
#                 text = "".join(page.extract_text() or "" for page in pdf_reader.pages)
#                 sentences = sent_tokenize(text)
#                 text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#                 chunks = text_splitter.split_text(" ".join(sentences))
#                 all_chunks.extend(chunks)
            
#             if not all_chunks:
#                 raise ValueError("No text chunks found in any PDF.")
            
#             global_vector_store = FAISS.from_texts(all_chunks, embeddings)
#             logger.info("Initialized global FAISS vector store")

#         # Set up memory for the conversational chain
#         memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

#         # Create the conversational chain using FAISS as retriever
#         qa = ConversationalRetrievalChain.from_llm(
#             retriever=global_vector_store.as_retriever(search_kwargs={"k": 5}),
#             memory=memory
#         )

#         # Generate a response based on the user's input
#         response = qa({"question": user_input})
#         return response['answer']

#     except Exception as e:
#         logger.error(f"Error generating response: {str(e)}")
#         return "Sorry, I couldn't process your request at the moment."