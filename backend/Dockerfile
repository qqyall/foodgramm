FROM python:3.9
WORKDIR /app

COPY requirements.txt .
RUN pip install -U -r requirements.txt --no-cache-dir
COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "foodgram.wsgi"]
