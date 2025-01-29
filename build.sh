#!/bin/bash
# Exit on error
set -e
python -m pip install --upgrade pip
# Install Python dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"