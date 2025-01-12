import sys
import os

# Add the project directory to the Python path
project_dir = '/home/songhk/news-analyzer'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

from app import app as application
