FROM python:3.11-slim

WORKDIR /app

# System deps (git needed for repo cloning)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# SQLite data volume mount point
RUN mkdir -p /data
ENV DATABASE_URL=sqlite:////data/codeviz.db

EXPOSE 8000

CMD ["python", "main.py"]
