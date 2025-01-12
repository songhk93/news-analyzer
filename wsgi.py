import sys
import os

# 프로젝트 디렉토리를 Python 경로에 추가
path = '/home/creativenextsoft/news-analyzer'
if path not in sys.path:
    sys.path.append(path)

# 환경 변수 설정
os.environ['FLASK_ENV'] = 'production'
os.environ['DATABASE_URL'] = 'sqlite:////home/creativenextsoft/news-analyzer/newsletter.db'

from app import app as application
application.secret_key = 'your-secret-key-here'

# 데이터베이스 테이블 생성
from app import db, create_tables
with application.app_context():
    create_tables()
