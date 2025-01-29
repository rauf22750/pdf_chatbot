#!/bin/bash

echo "Ensuring pip is installed..."
python -m ensurepip --default-pip
python -m pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate

echo "Collecting static files..."
mkdir -p staticfiles  # Ensure the folder exists
python manage.py collectstatic --noinput

echo "Checking collected files..."
ls -la staticfiles
