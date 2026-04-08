# Docker Setup Guide

This project is now fully dockerized with support for backend, frontend, and PostgreSQL database services.

## Files Created

- **Dockerfile.backend** - FastAPI backend container (Python 3.11)
- **Dockerfile.frontend** - React/Vite frontend container (Node 20)
- **docker-compose.yml** - Orchestrates all services (backend, frontend, PostgreSQL)
- **.dockerignore** - Excludes unnecessary files from Docker builds
- **.env.example** - Template for environment variables
- **server/.dockerignore** - Backend-specific Docker ignore file
- **frontend/.dockerignore** - Frontend-specific Docker ignore file

## Prerequisites

- [Docker](https://www.docker.com/products/docker-desktop) (version 20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (version 1.29+)

## Quick Start

### 1. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and update these critical values:
```env
GEMINI_API_KEY=your_actual_gemini_api_key
DB_PASSWORD=your_secure_password  # Change from default "admin"
SECRET_KEY=your_secure_secret_key
```

### 2. Build and Start Services

```bash
docker-compose up -d
```

This will:
- Build the backend container
- Build the frontend container
- Start PostgreSQL with initial database schema
- Start FastAPI backend on `http://localhost:8000`
- Start React frontend on `http://localhost:3000`

### 3. Verify Services

```bash
# Check all containers are running
docker-compose ps

# View logs
docker-compose logs -f backend    # Backend logs
docker-compose logs -f frontend   # Frontend logs
docker-compose logs -f db         # Database logs
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Common Commands

### Stop Services
```bash
docker-compose down
```

### Stop Services & Remove Volumes (Remove Database)
```bash
docker-compose down -v
```

### Rebuild Containers
```bash
docker-compose up -d --build
```

### Rebuild Specific Service
```bash
docker-compose up -d --build backend
docker-compose up -d --build frontend
```

### View Service Logs
```bash
docker-compose logs -f          # All services
docker-compose logs -f backend  # Backend only
docker-compose logs -f frontend # Frontend only
docker-compose logs -f db       # Database only
```

### Execute Commands in Containers
```bash
# Run Python script in backend
docker-compose exec backend python script.py

# Run npm command in frontend
docker-compose exec frontend npm run build

# Connect to PostgreSQL
docker-compose exec db psql -U postgres -d smart_db
```

## Environment Variables Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_USER` | postgres | PostgreSQL username |
| `DB_PASSWORD` | admin | PostgreSQL password |
| `DB_HOST` | db | PostgreSQL host (use 'db' in Docker) |
| `DB_PORT` | 5432 | PostgreSQL port |
| `DB_NAME` | smart_db | Database name |
| `GEMINI_API_KEY` | - | Your Google Gemini API key (required) |
| `SECRET_KEY` | - | JWT secret key (change in production) |
| `REACT_APP_API_URL` | http://localhost:8000 | Backend API URL for frontend |
| `BACKEND_PORT` | 8000 | Backend service port |
| `FRONTEND_PORT` | 3000 | Frontend service port |

## Database Initialization

The database automatically initializes on first run with:
- `products_table.sql` - Product schema
- `custommer.sql` - Customer schema
- `insertion.sql` - Sample data
- `others.sql` - Additional tables

To reinitialize the database:
```bash
docker-compose down -v
docker-compose up -d
```

## Port Mapping

| Service | Container Port | Host Port |
|---------|-----------------|-----------|
| Frontend | 3000 | 3000 |
| Backend | 8000 | 8000 |
| PostgreSQL | 5432 | 5432 |

To use different ports, update the port mappings in `docker-compose.yml` or override via environment variables.

## Production Deployment Notes

For production deployment:

1. **Update SECRET_KEY**: Change from default value
2. **Update DB_PASSWORD**: Use a strong password
3. **Configure GEMINI_API_KEY**: Ensure API key is securely set
4. **Set REACT_APP_API_URL**: Use your production backend URL
5. **Enable HTTPS**: Use a reverse proxy (nginx/traefik)
6. **Resource Limits**: Add memory/CPU limits in docker-compose.yml
7. **Volume Persistence**: Ensure PostgreSQL data volume is backed up
8. **Restart Policy**: Services are set to `restart: unless-stopped`

## Troubleshooting

### Containers Won't Start
```bash
# Check logs
docker-compose logs

# Rebuild and start
docker-compose down
docker-compose up -d --build
```

### Database Connection Errors
```bash
# Ensure database is healthy
docker-compose exec db pg_isready

# Wait for database to be ready
docker-compose up -d db
sleep 10
docker-compose up -d backend
```

### Port Already in Use
Update port mappings in `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Use 8001 instead of 8000
```

### Frontend Can't Connect to Backend
Ensure `REACT_APP_API_URL` is correctly set to match your backend service location.

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI in Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [React in Docker](https://create-react-app.dev/docs/deployment/)
