# Django PDF Chatbot Project

This repository contains a Django-based project for creating a chatbot capable of extracting and analyzing data from PDF files. The chatbot uses natural language processing (NLP) techniques to provide intelligent responses based on the uploaded PDFs.

## Features
- User authentication and registration.
- Upload and process multiple PDFs.
- Tokenize and extract data from PDFs using NLP.
- Provide intelligent answers to user queries based on PDF content.

---

## Requirements
Groq API

### Prerequisites
- Python 3.8 or later
- pip (Python package manager)

### Installation
Ensure you have the required Python version installed on your system. To install the project dependencies, follow the steps below.

---

## Installation and Setup

### 1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_name>
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv env
source env/bin/activate  # For Linux/macOS
env\Scripts\activate   # For Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download NLTK Data (First Time Setup)
```python
import nltk
nltk.download('stopwords')
nltk.download('punkt')
```

### 5. Migrate the Database
```bash
python manage.py migrate
```

### 6. Create a Superuser
```bash
python manage.py createsuperuser
```
Follow the prompts to set up an admin user.

### 7. Run the Server
```bash
python manage.py runserver
```
Access the application at `http://127.0.0.1:2222/`

## Usage
- **Upload PDFs**: Use the web interface to upload PDF files.
- **Query PDFs**: Interact with the chatbot to ask questions based on uploaded PDF content.

### Acknowledgements
- Django Framework
- PyPDF2 for PDF parsing
- NLTK for natural language processing

