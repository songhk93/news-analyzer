from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
from urllib.parse import urlparse
import os
from konlpy.tag import Okt
import numpy as np
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
# 데이터베이스 설정
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///newsletter.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Newsletter(db.Model):
    seq = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), unique=True, nullable=False)
    title = db.Column(db.String(200))
    date = db.Column(db.DateTime)
    content = db.Column(db.Text)
    domain = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'seq': self.seq,
            'url': self.url,
            'title': self.title,
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'content': self.content,
            'domain': self.domain,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

def create_tables():
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/articles')
def articles():
    return render_template('articles.html')

@app.route('/api/articles', methods=['GET'])
def get_articles():
    articles = Newsletter.query.order_by(Newsletter.date.desc()).all()
    return jsonify([article.to_dict() for article in articles])

@app.route('/api/submit_url', methods=['POST'])
def submit_url():
    url = request.json.get('url')
    
    if not url:
        return jsonify({'error': '유효하지 않은 URL입니다.'}), 400

    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.title.string if soup.title else None
        content = ' '.join([p.text for p in soup.find_all('p')])
        
        if not title or not content:
            return jsonify({'error': '기사 내용을 파싱할 수 없습니다.'}), 400

        domain = urlparse(url).netloc
        
        existing_article = Newsletter.query.filter_by(url=url).first()
        if existing_article:
            existing_article.title = title
            existing_article.content = content
            existing_article.date = datetime.now()
            existing_article.domain = domain
        else:
            new_article = Newsletter(
                url=url,
                title=title,
                content=content,
                date=datetime.now(),
                domain=domain
            )
            db.session.add(new_article)
        
        db.session.commit()
        return jsonify({'message': '성공적으로 저장되었습니다.'})
        
    except Exception as e:
        return jsonify({'error': f'오류가 발생했습니다: {str(e)}'}), 400

@app.route('/api/keywords')
def get_keywords():
    week_ago = datetime.now() - timedelta(days=7)
    articles = Newsletter.query.filter(Newsletter.date >= week_ago).all()
    
    # 형태소 분석기 초기화
    okt = Okt()
    
    # 불용어 정의
    stopwords = {'있다', '하다', '이다', '되다', '그', '및', '제', '할', '수', '등', '들', '것', '거', '말'}
    
    # 모든 기사의 텍스트 결합
    text = ' '.join([f"{article.title} {article.content}" for article in articles])
    
    # 형태소 분석 및 명사 추출
    nouns = okt.nouns(text)
    
    # 불용어 제거 및 2글자 이상 단어만 선택
    filtered_words = [word for word in nouns if word not in stopwords and len(word) >= 2]
    
    # 단어 빈도수 계산
    word_count = Counter(filtered_words)
    
    # 상위 10개 키워드 추출
    top_keywords = word_count.most_common(10)
    
    return jsonify({
        'keywords': [{'word': word, 'count': count} for word, count in top_keywords]
    })

@app.route('/api/related_articles/<keyword>')
def get_related_articles(keyword):
    articles = Newsletter.query.filter(
        (Newsletter.title.like(f'%{keyword}%')) | 
        (Newsletter.content.like(f'%{keyword}%'))
    ).order_by(Newsletter.date.desc()).limit(5).all()
    
    return jsonify([{
        'title': article.title,
        'url': article.url,
        'date': article.date.strftime('%Y-%m-%d')
    } for article in articles])

@app.route('/api/search', methods=['GET'])
def search_articles():
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': '검색어를 입력해주세요.'}), 400
    
    # 제목과 내용에서 검색
    articles = Newsletter.query.filter(
        db.or_(
            Newsletter.title.ilike(f'%{query}%'),
            Newsletter.content.ilike(f'%{query}%')
        )
    ).order_by(Newsletter.date.desc()).all()
    
    return jsonify([article.to_dict() for article in articles])

@app.route('/api/delete_article/<int:seq>', methods=['DELETE'])
def delete_article(seq):
    article = Newsletter.query.get_or_404(seq)
    db.session.delete(article)
    db.session.commit()
    return jsonify({'message': '기사가 삭제되었습니다.'})

if __name__ == '__main__':
    create_tables()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
