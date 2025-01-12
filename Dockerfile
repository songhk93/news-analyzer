FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:application"]
