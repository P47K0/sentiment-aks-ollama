# llm-adapter/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY llm-adapter/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY llm-adapter/app.py .

EXPOSE 5000

CMD ["python", "app.py"]