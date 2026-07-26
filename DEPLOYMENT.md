# Deployment Guide

## Deployment Strategy

Bowling HQ deployment will follow a multi-phase approach as systems are completed.

## Current Phase (0): Documentation

**Status**: ✅ Complete
- Documentation deployed to repository
- Ready for Phase 1 development

## Phase 1: Backend Foundation

### Prerequisites
- PostgreSQL 13+
- Python 3.10+
- Docker & Docker Compose
- AWS/GCP/Azure account (for hosting)

### Deployment Steps

```bash
# 1. Build Docker image
docker build -t bowling-hq-backend:latest .

# 2. Run migrations
docker-compose exec web alembic upgrade head

# 3. Seed initial data
docker-compose exec web python scripts/seed_data.py

# 4. Start services
docker-compose up -d
```

## Phase 2: Frontend Deployment

### Build for Production

```bash
cd frontend
npm run build
```

### Deploy to CDN

```bash
# Upload build/ directory to S3/CloudFront
aws s3 sync build/ s3://bowling-hq-cdn/
```

## Phase 3: AI Integration

### Model Deployment

- Host models on cloud GPU instances
- Set up inference endpoints
- Configure auto-scaling

## Phase 4: Video Processing

### Pipeline Setup

```bash
# Start video processing workers
docker-compose -f docker-compose.workers.yml up -d
```

## Environment Configuration

### Production (.env.production)

```bash
# Database
DATABASE_URL=postgresql://user:password@prod-db:5432/bowling_hq

# API
API_URL=https://api.bowling-hq.com
API_PORT=8000

# Security
SECRET_KEY=<generate-strong-key>
JWT_SECRET=<generate-jwt-key>

# Services
S3_BUCKET=bowling-hq-prod
REDIS_URL=redis://prod-redis:6379

# AI
AI_MODEL_PATH=/models/production
AI_ENDPOINT=https://ai.bowling-hq.com
```

## Monitoring & Logging

### Application Monitoring

```bash
# Start monitoring stack
docker-compose -f docker-compose.monitoring.yml up -d
```

### Logging

- Application logs: CloudWatch/DataDog
- Database logs: PostgreSQL logs
- Error tracking: Sentry
- Performance: New Relic/Datadog APM

## Database Backups

### Automated Backups

```bash
# Daily backup script
0 2 * * * /scripts/backup_db.sh

# Store in S3
aws s3 cp backup.sql s3://bowling-hq-backups/daily/
```

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/`):

1. Run tests
2. Build images
3. Deploy to staging
4. Run integration tests
5. Deploy to production

## Health Checks

### API Health

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "timestamp": "2026-07-08T12:00:00Z"
}
```

## Rollback Procedure

### If Deployment Fails

```bash
# 1. Revert to previous version
git revert <commit>

# 2. Rebuild image
docker build -t bowling-hq-backend:latest .

# 3. Restart services
docker-compose restart

# 4. Monitor logs
docker-compose logs -f
```

## Performance Optimization

### Caching
- Redis for session cache
- CloudFront for static assets
- Database query caching

### Database Optimization
- Index frequently queried columns
- Connection pooling
- Query optimization

### API Performance
- Gzip compression
- Request rate limiting
- Load balancing

## Security Considerations

- SSL/TLS certificates (Let's Encrypt)
- Firewall rules
- DDoS protection
- Regular security audits
- Dependency scanning

## Disaster Recovery

### RTO/RPO Goals
- Recovery Time Objective: 1 hour
- Recovery Point Objective: 15 minutes

### Backup Storage
- Primary: AWS S3
- Secondary: Google Cloud Storage
- Retention: 30 days minimum

## Deployment Checklist

- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] Backups created
- [ ] Monitoring configured
- [ ] Health checks passing
- [ ] Performance benchmarks met
- [ ] Security audit complete

---

**This is a planned deployment guide. Details will be refined during implementation.**
