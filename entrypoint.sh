#!/bin/bash

# Run migrations (uncomment when db is added)
# python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Start the Django server
exec python manage.py runserver 0.0.0.0:8000