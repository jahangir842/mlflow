# MLflow Linux Installation Guide

Complete guide for installing MLflow on Linux servers with PostgreSQL backend and systemd service.

## Quick Installation

```bash
# Install dependencies
sudo apt update && sudo apt install python3 python3-pip libpq-dev postgresql -y

# Create virtual environment
python3 -m venv .mlflow && source .mlflow/bin/activate

# Install MLflow
pip install mlflow psycopg2-binary

# Setup PostgreSQL and start service
sudo -u postgres psql -c "CREATE DATABASE mlflowdb;"
sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'pakistan';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE mlflowdb TO admin;"

# Create artifacts directory
sudo mkdir -p /mlflow/artifacts && sudo chown -R $USER:$USER /mlflow
```

## Detailed Documentation

See [Complete Installation Guide](complete_installation_guide.md) for:
- Detailed system setup
- PostgreSQL configuration
- MLflow server setup
- Systemd service configuration
- Troubleshooting steps

## Common Commands

```bash
# Start MLflow server
mlflow server \
  --backend-store-uri postgresql://admin:pakistan@localhost/mlflowdb \
  --default-artifact-root file:///mlflow/artifacts \
  --host 0.0.0.0 \
  --port 5000

# Using systemd service
sudo systemctl start mlflow-server
sudo systemctl status mlflow-server
```

## Directory Structure
```
linux_installation/
├── complete_installation_guide.md  # Full setup instructions
├── README.md                      # This file
└── systemd_setup.md              # Service configuration
```

For production deployment, please follow the [Complete Installation Guide](complete_installation_guide.md).
