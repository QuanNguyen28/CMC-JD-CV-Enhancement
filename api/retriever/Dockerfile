# retriever/Dockerfile

# 1. Base image
FROM python:3.12-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy application code
COPY . .

# 5. Expose port
EXPOSE 8000

# 6. Default command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
