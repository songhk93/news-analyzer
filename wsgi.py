import os
import sys

# 프로젝트 디렉토리 경로 설정
path = '/home/songhk/news-analyzer'
if path not in sys.path:
    sys.path.append(path)

# 가상환경 경로 설정
virtualenv_path = '/home/songhk/news-analyzer/venv/lib/python3.9/site-packages'
if virtualenv_path not in sys.path:
    sys.path.append(virtualenv_path)

from app import app as application

# This is the PythonAnywhere WSGI configuration
if __name__ == '__main__':
    application.run()
