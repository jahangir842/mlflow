# Use the official MLflow image as the base
FROM ghcr.io/mlflow/mlflow:v2.20.3

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && pip install psycopg2-binary==2.9.9 \
    && apt-get remove -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Set the default command (optional, can be overridden in Kubernetes)
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]
