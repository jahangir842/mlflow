# MLflow Docker Compose Setup

Quick setup for MLflow using Docker Compose.

## Prerequisites
- Docker
- Docker Compose

## Quick Start

1. Build the custom image:
```bash
docker build -t mlflow-with-psycopg2:v2.20.3 .
```

2. Start services:
```bash
docker-compose up -d
```

3. Access MLflow UI:
- URL: http://localhost:5000

## Configuration
- PostgreSQL:
  - User: admin
  - Password: pakistan
  - Database: mlflowdb
  - Port: 5432

- MLflow:
  - Port: 5000
  - Artifacts: stored in Docker volume

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Stop and remove everything (including volumes)
docker-compose down -v
```

## Troubleshooting

1. If PostgreSQL port 5432 is already in use:
   - Change the port mapping in docker-compose.yml from "5432:5432" to "5433:5432"

2. If MLflow container fails to start:
   ```bash
   # Check MLflow logs
   docker-compose logs mlflow
   ```

3. If PostgreSQL connection fails:
   ```bash
   # Check PostgreSQL logs
   docker-compose logs postgres
   ```

## Data Persistence

- PostgreSQL data is stored in the `postgres_data` volume
- MLflow artifacts are stored in the `mlflow_artifacts` volume

These volumes persist even after containers are stopped. To remove them, use:
```bash
docker-compose down -v
```

## Security Note

The default credentials in this setup are for demonstration purposes. For production:
1. Change the default passwords
2. Use environment variables or Docker secrets
3. Enable SSL/TLS
4. Configure proper network security

## Additional Resources

- [MLflow Documentation](https://www.mlflow.org/docs/latest/index.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)
