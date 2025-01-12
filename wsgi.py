import sys
import os

# Add your project directory to Python path
project_home = os.path.expanduser('~/news-analyzer')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application

# This is the PythonAnywhere WSGI configuration
if __name__ == '__main__':
    application.run()
