# Inventory Reconciliation SaaS

A full-stack SaaS application for inventory reconciliation with discrepancy detection, reporting, and automated alerts.

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy (async), PostgreSQL, Celery, Redis
- **Frontend**: React + TypeScript + Vite
- **Deployment**: Docker Compose

## Local Setup

```bash
# Start infrastructure
docker compose up -d db redis

# Install backend dependencies
pip install -e backend/

# Install frontend dependencies
cd frontend && npm install && cd ..

# Run migrations
cd backend && alembic upgrade head

# Start development servers
docker compose up
```

## Dev Server Commands

- Backend: `cd backend && uvicorn app.main:app --reload --port 8000`
- Frontend: `cd frontend && npm run dev`
