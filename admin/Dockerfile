FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files (not .venv, .git, __pycache__, etc.)
COPY app.py run.py wsgi.py ./
COPY templates/ ./templates/
COPY static/ ./static/ 2>/dev/null || true

# Create non-root user for security
RUN useradd -m -u 1000 flaskuser
USER flaskuser

# Environment defaults
ENV DATABASE_PATH=/data/oc_frenchquran.sqlite
ENV ADMIN_PASSWORD=admin123
ENV FLASK_SECRET_KEY=change-me-in-production
ENV FLASK_DEBUG=0

# Expose the correct port (run.py uses 5001 by default)
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import sqlite3; sqlite3.connect('$DATABASE_PATH')" || exit 1

CMD ["python", "run.py"]
