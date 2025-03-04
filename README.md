# MLflow Deployment Guide

This repository contains comprehensive guides for deploying MLflow in different environments.

## Available Installation Methods

1. [Docker Compose Installation](docker_compose_installation/README.md)
   - Single command setup with `docker-compose up`
   - Includes PostgreSQL and MLflow
   - Perfect for development and testing
   - [Quick Start Guide](docker_compose_installation/README.md#quick-start)

2. [Linux Direct Installation](linux_installation/complete_installation_guide.md)
   - Complete step-by-step installation
   - Systemd service setup
   - Production-ready configuration
   - [Comprehensive Guide](linux_installation/complete_installation_guide.md)

3. [Kubernetes Installation](kubernetes_installation/README.md)
   - Production-grade deployment
   - High availability setup
   - Scalable architecture

## Quick Start Commands

### Docker Compose
```bash
git clone <this-repo>
cd mlflow/docker_compose_installation
docker-compose up -d
```
Access MLflow at: http://localhost:5000

### Linux Direct Installation
```bash
# Follow comprehensive guide
cd mlflow/linux_installation
source .mlflow/bin/activate
sudo systemctl start mlflow-server
```
Access MLflow at: http://localhost:5000

### Kubernetes
```bash
kubectl apply -f kubernetes_installation/manifests/
```
Access MLflow at: http://cluster-ip:30500

## Directory Structure
```
mlflow/
├── docker_compose_installation/   # Docker-based setup
│   ├── README.md                 # Docker setup guide
│   ├── docker-compose.yml        # Service definitions
│   └── Dockerfile               # Custom MLflow image
├── linux_installation/           # Direct Linux setup
│   ├── complete_installation_guide.md  # Full guide
│   └── systemd_setup.md         # Service automation
└── kubernetes_installation/      # K8s deployment
    ├── README.md                # K8s setup guide
    └── manifests/               # K8s configurations
```

## Common Configurations

All installation methods use these default settings:
- PostgreSQL Database:
  - User: admin
  - Database: mlflowdb
  - Port: 5432
- MLflow Server:
  - Port: 5000
  - Artifact Storage: Local filesystem
  - Backend: PostgreSQL

## Choosing the Right Method

1. **Docker Compose**: Choose if you:
   - Want quick local setup
   - Need isolated environment
   - Are developing/testing

2. **Linux Direct**: Choose if you:
   - Need full control
   - Have existing Linux server
   - Want system integration

3. **Kubernetes**: Choose if you:
   - Need high availability
   - Want automated scaling
   - Have K8s infrastructure

## Documentation
- [MLflow Documentation](https://www.mlflow.org/docs/latest/index.html)
- [Setup Troubleshooting](linux_installation/complete_installation_guide.md#troubleshooting)
- [Security Considerations](docker_compose_installation/README.md#security-note)