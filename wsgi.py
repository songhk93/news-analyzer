import sys
path = '/home/songhk/news-analyzer'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
