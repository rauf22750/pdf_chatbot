#!/bin/bash
#!/bin/bash
echo "Installing dependencies..."
python3.9 -m pip install --upgrade pip
python3.9 -m pip install -r requirements.txt
echo "Collecting static files..."
python3.9 manage.py collectstatic --noinput
echo "Build completed."
!/bin/bash
Build the project
