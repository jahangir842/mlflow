FROM ghcr.io/mlflow/mlflow:v3.14.0

# Install system + Python dependencies:
#   - psycopg2-binary : PostgreSQL backend store driver
#   - boto3           : S3/MinIO artifact store driver (needed for --serve-artifacts)
#   - mlflow[auth]    : basic-auth extras (Flask-WTF etc.) for --app-name basic-auth
#   - curl            : used by the container healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        gcc \
        curl \
    && pip install --no-cache-dir \
        psycopg2-binary==2.9.9 \
        boto3==1.35.99 \
        'mlflow[auth]==3.14.0' \
    && apt-get remove -y gcc \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 5000

# Default command (overridden by docker-compose / k8s to add store URIs and auth)
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]
