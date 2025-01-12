#!/bin/bash
python -m pip install --upgrade pip
pip install -r requirements.txt
python -c "from app import db; db.create_all()"
gunicorn --config gunicorn_config.py wsgi:application
