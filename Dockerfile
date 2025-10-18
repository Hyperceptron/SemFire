# SemFire CLI container
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

WORKDIR /app

# Optional: install from requirements.txt (disabled by default)
ARG INSTALL_REQS=false
COPY requirements.txt ./requirements.txt

# Install minimal runtime deps for CLI usage and config menu
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN if [ "$INSTALL_REQS" = "true" ]; then pip install --no-cache-dir -r requirements.txt; fi

# Copy source code (library + CLI) and supporting modules used by CLI
COPY src/ ./src/
COPY spotlighting/ ./spotlighting/
COPY injection_defense/ ./injection_defense/
COPY sitecustomize.py ./sitecustomize.py

# Default to printing help if no args are supplied
ENTRYPOINT ["python", "-m", "src.cli"]
CMD ["analyze", "--help"]
