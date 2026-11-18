# Deployment Guide

## Prerequisites
- Docker and Docker Compose
- Domain name
- Stripe account (test mode for dev, live for production)

## Quick Start (Production)

### 1. Configure environment
```bash
cp .env.production.example .env.production
# Edit .env.production with your values
```

### 2. Generate secrets
```bash
openssl rand -hex 32  # for SECRET_KEY and JWT_SECRET_KEY
```

### 3. Start
```bash
docker compose -f docker-compose.prod.yml up -d
```

### 4. Run migrations
```bash
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 5. Set up domain + SSL
```bash
docker compose -f docker-compose.prod.yml exec nginx nginx -t
```

## Backups
Daily encrypted backups stored in the `backup` volume.
```bash
docker compose -f docker-compose.prod.yml exec backup ls /backup/
```

## Monitoring
- Health: `curl https://your-domain.com/health`
- Logs: `docker compose -f docker-compose.prod.yml logs -f`
- Database: managed by PostgreSQL, connection pooling configured

## Secrets Management
- All secrets in `.env.production` — never commit this file
- Database password, SECRET_KEY, JWT_SECRET_KEY must be >= 32 random hex chars
- Stripe keys from your Stripe Dashboard
