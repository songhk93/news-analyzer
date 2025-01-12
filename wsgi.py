import sys
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 프로젝트 디렉토리 설정
project_dir = '/home/new1/news-analyzer'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# 환경 변수 설정
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'production'

from app import app as application