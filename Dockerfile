FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and baked-in static data
COPY app/ ./app/
COPY static/ ./static/
COPY data/flashcards.json ./data/flashcards.json
COPY data/quiz_questions.json ./data/quiz_questions.json

# Create per-user progress directory (populated at runtime, not committed)
RUN mkdir -p /app/data/progress

# Run as non-root for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
