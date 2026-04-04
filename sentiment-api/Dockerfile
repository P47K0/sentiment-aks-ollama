# sentiment-api/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY sentiment-api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY sentiment-api/app.py .

EXPOSE 5000

CMD ["python", "app.py"]