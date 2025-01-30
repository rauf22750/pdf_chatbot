import os
import logging
from PyPDF2 import PdfReader
from groq import Groq
from django.conf import settings
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.probability import FreqDist

# Download necessary NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        extracted_text = ""
        for page in pdf_reader.pages:
            extracted_text += page.extract_text()
    return extracted_text

def summarize_text(text, max_sentences=3):
    sentences = sent_tokenize(text)
    words = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    words = [word for word in words if word not in stop_words]

    freq_dist = FreqDist(words)
    sentence_scores = {}
    for sentence in sentences:
        for word in word_tokenize(sentence.lower()):
            if word in freq_dist:
                if sentence not in sentence_scores:
                    sentence_scores[sentence] = freq_dist[word]
                else:
                    sentence_scores[sentence] += freq_dist[word]

    summary_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:max_sentences]
    summary = ' '.join(summary_sentences)
    return summary

def process_multiple_pdfs(pdf_data, question, context):
    summaries = []
    for pdf in pdf_data:
        extracted_text = extract_text_from_pdf(pdf['path'])
        summary = summarize_text(extracted_text)
        summaries.append(f"PDF: {os.path.basename(pdf['path'])}\nSummary: {summary}")
    
    return send_text_to_model(summaries, question, context)

def send_text_to_model(pdf_summaries, question, context):
    try:
        api_key = settings.GROQ_API_KEY
        if not api_key:
            logger.error("API key is missing in settings")
            return "Error: API key is missing."

        client = Groq(api_key=api_key)
        model_name = "llama3-8b-8192"

        # Combine summaries, context, and question, respecting token limit
        combined_input = "Summarized content of PDFs:\n\n"
        for summary in pdf_summaries:
            combined_input += f"{summary}\n\n"
        
        if context:
            combined_input += f"Previous interaction:\n{context}\n\n"
        
        combined_input += f"Current question: {question}\n\n"
        combined_input += "Based on the summarized PDF content and the current question, please provide a concise and relevant answer. Focus only on answering the current question without repeating previous information."

        # Ensure we're within token limit (assuming 4 characters per token as a rough estimate)
        max_tokens = 7000  # Leave some room for the model's response
        if len(combined_input) > max_tokens * 4:
            combined_input = combined_input[:max_tokens * 4]
        
        logger.info(f"Sending request to model with input length: {len(combined_input)}")
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": combined_input}],
            model=model_name,
            max_tokens=1000  # Limit the response length
        )
        
        response = chat_completion.choices[0].message.content
        logger.info(f"Received response from model with length: {len(response)}")
        return response

    except Exception as e:
        logger.error(f"Error while interacting with the model: {str(e)}")
        return f"Error while interacting with the model: {str(e)}"