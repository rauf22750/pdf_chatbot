#!/bin/bash
set -e  # Exit on any error

echo "Ensuring pip is installed..."
python -m ensurepip --upgrade  # Use python instead of python3.9
if [ $? -ne 0 ]; then
  echo "Failed to install pip!"
  exit 1
fi

echo "Upgrading pip..."
python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
  echo "Failed to upgrade pip!"
  exit 1
fi

echo "Installing dependencies..."
python -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
  echo "Failed to install dependencies!"
  exit 1
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
  echo "Failed to collect static files!"
  exit 1
fi

echo "Build completed."

