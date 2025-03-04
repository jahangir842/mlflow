# Complete MLflow Installation Guide for Linux

## Table of Contents
1. [Basic Installation](#basic-installation)
2. [PostgreSQL Setup](#postgresql-setup)
3. [Server Configuration](#server-configuration)
4. [Systemd Service Setup](#systemd-service-setup)

## Basic Installation

### System Requirements
- Python 3.7+
- pip
- virtualenv or venv

### Steps
```bash
# Update system and install dependencies
sudo apt update
sudo apt install python3 python3-pip libpq-dev -y

# Create and activate virtual environment
cd /home/jahangir/projects/mlflow
python3 -m venv .mlflow
source .mlflow/bin/activate

# Install MLflow
pip install mlflow psycopg2-binary
```

## PostgreSQL Setup

### Installation
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Database Configuration
```bash
# Create database and user
sudo -u postgres psql <<EOF
CREATE DATABASE mlflowdb;
CREATE USER admin WITH PASSWORD 'pakistan';
ALTER ROLE admin SET client_encoding TO 'utf8';
ALTER ROLE admin SET default_transaction_isolation TO 'read committed';
ALTER ROLE admin SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE mlflowdb TO admin;
\q
EOF
```

## Server Configuration

### Artifact Storage Setup
```bash
# Create artifact directory
sudo mkdir -p /mlflow/artifacts
sudo chown -R $USER:$USER /mlflow
```

### Firewall Configuration
```bash
# Ubuntu/Debian
sudo ufw allow 5000/tcp

# RHEL/CentOS
sudo firewall-cmd --permanent --add-port=5000/tcp
sudo firewall-cmd --reload
```

### Environment Setup
```bash
# Set MLflow environment variable
echo 'export MLFLOW_TRACKING_URI="http://localhost:5000"' >> ~/.bashrc
source ~/.bashrc
```

## Systemd Service Setup

### Create Service File
```bash
sudo tee /etc/systemd/system/mlflow-server.service << EOF
[Unit]
Description=MLflow Server
After=network.target postgresql.service

[Service]
User=$USER
Group=$USER
WorkingDirectory=/home/jahangir/projects/mlflow
ExecStart=/bin/bash -c "source .mlflow/bin/activate && \
          mlflow server \
          --backend-store-uri postgresql://admin:pakistan@localhost/mlflowdb \
          --default-artifact-root file:///mlflow/artifacts \
          --host 0.0.0.0 \
          --port 5000"
Restart=always
Environment=PATH=/usr/local/bin:$PATH

[Install]
WantedBy=multi-user.target
EOF
```

### Enable and Start Service
```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable mlflow-server

# Start service
sudo systemctl start mlflow-server

# Check status
sudo systemctl status mlflow-server
```

## Verification

1. Check MLflow Server Status
```bash
sudo systemctl status mlflow-server
```

2. View Logs
```bash
sudo journalctl -u mlflow-server -f
```

3. Test Access
- Open browser: http://localhost:5000
- Or use curl: `curl http://localhost:5000`

## Common Operations

### Service Management
```bash
# Stop service
sudo systemctl stop mlflow-server

# Restart service
sudo systemctl restart mlflow-server

# Disable autostart
sudo systemctl disable mlflow-server
```

### Database Operations
```bash
# Connect to database
psql -h localhost -U admin -d mlflowdb

# Backup database
pg_dump -U admin -d mlflowdb > mlflow_backup.sql

# Restore database
psql -U admin -d mlflowdb < mlflow_backup.sql
```

## Troubleshooting

1. If MLflow fails to start:
   - Check logs: `sudo journalctl -u mlflow-server -f`
   - Verify PostgreSQL connection: `psql -h localhost -U admin -d mlflowdb`
   - Check artifact directory permissions: `ls -la /mlflow/artifacts`

2. If PostgreSQL is inaccessible:
   ```bash
   sudo systemctl status postgresql
   sudo tail -f /var/log/postgresql/postgresql-14-main.log
   ```

3. If port 5000 is already in use:
   ```bash
   sudo netstat -tulpn | grep 5000
   sudo lsof -i :5000
   ```
