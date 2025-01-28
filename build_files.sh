#!/bin/bash
set -e  # Exit on any error

echo "Ensuring pip is installed..."
Python -m ensurepip --upgrade
if [ $? -ne 0 ]; then
  echo "Failed to install pip!"
  exit 1
fi

echo "Upgrading pip..."
Python -m pip install --upgrade pip
if [ $? -ne 0 ]; then
  echo "Failed to upgrade pip!"
  exit 1
fi

echo "Installing dependencies..."
Python -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
  echo "Failed to install dependencies!"
  exit 1
fi

echo "Collecting static files..."
Python manage.py collectstatic --noinput
if [ $? -ne 0 ]; then
  echo "Failed to collect static files!"
  exit 1
fi

echo "Build completed."
