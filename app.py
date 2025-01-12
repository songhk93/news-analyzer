from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import logging
from logging.handlers import RotatingFileHandler

# Flask 앱 초기화
app = Flask(__name__)

# 기본 설정
app.config.update(
    SQLALCHEMY_DATABASE_URI='sqlite:///newsletter.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SECRET_KEY='your-secret-key-here'
)

# 데이터베이스 초기화
db = SQLAlchemy(app)

# 로깅 설정
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = RotatingFileHandler('logs/news_analyzer.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('News Analyzer startup')

# 데이터베이스 모델
class Newsletter(db.Model):
    seq = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    keywords = db.Column(db.String(200))
    url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'seq': self.seq,
            'title': self.title,
            'content': self.content,
            'keywords': self.keywords,
            'url': self.url,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# 데이터베이스 생성
with app.app_context():
    try:
        db.create_all()
        app.logger.info('Database tables created successfully')
    except Exception as e:
        app.logger.error(f'Error creating database tables: {str(e)}')

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f'Error in index route: {str(e)}')
        return str(e), 500

@app.route('/articles')
def articles():
    try:
        return render_template('articles.html')
    except Exception as e:
        app.logger.error(f'Error in articles route: {str(e)}')
        return str(e), 500

@app.route('/api/articles', methods=['GET'])
def get_articles():
    try:
        articles = Newsletter.query.order_by(Newsletter.created_at.desc()).all()
        return jsonify([article.to_dict() for article in articles])
    except Exception as e:
        app.logger.error(f'Error in get_articles: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)
