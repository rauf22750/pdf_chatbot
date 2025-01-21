#!/bin/bash
# build_files.sh

# Activate the Python environment provided by Vercel
source /vercel/.venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput


