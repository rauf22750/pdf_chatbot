#!/bin/bash
set -e  # Exit on error

echo "Installing dependencies..."
python3.9 -m pip install --upgrade pip
if [ $? -ne 0 ]; then
  echo "Failed to upgrade pip!"
  exit 1
fi

python3.9 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
  echo "Failed to install dependencies from requirements.txt!"
  exit 1
fi

echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
  echo "Failed to collect static files!"
  exit 1
fi

echo "Build completed."
