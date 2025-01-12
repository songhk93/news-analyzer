#!/bin/bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -c "from app import db; db.create_all()"
gunicorn wsgi:application --bind 0.0.0.0:$PORT
