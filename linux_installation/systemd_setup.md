# MLflow Systemd Service Setup

This guide explains how to set up MLflow as a systemd service.

## Creating the Service File

1. Create the service file:
```bash
sudo nano /etc/systemd/system/mlflow-server.service
```

2. Add this configuration:
```ini
[Unit]
Description=MLflow Server
After=network.target postgresql.service

[Service]
User=jahangir
Group=jahangir
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
```

## Managing the Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable autostart
sudo systemctl enable mlflow-server

# Start the service
sudo systemctl start mlflow-server

# Check status
sudo systemctl status mlflow-server

# View logs
sudo journalctl -u mlflow-server -f
```
