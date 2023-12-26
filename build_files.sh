#!/bin/bash
echo "BUILD START"
python -m pip install -r requirements.txt
python manage.py migrate

# Collect static files
python3 manage.py collectstatic --noinput

# Start the Django development server
python manage.py runserver 0.0.0.0:$PORT
echo "BUILD END"