# Performance Optimization Guide

## Frontend Performance

### Code Splitting

```javascript
// Lazy load components
const Sessions = React.lazy(() => import('./components/Sessions'));
const VideoCoach = React.lazy(() => import('./components/VideoCoach'));

// With Suspense
<Suspense fallback={<Spinner />}>
  <Sessions />
</Suspense>
```

### Bundle Analysis

```bash
# Analyze bundle size
npm install --save-dev source-map-explorer
npm run build
npx source-map-explorer 'build/static/js/*.js'
```

### Image Optimization

```javascript
// Use responsive images
<picture>
  <source srcSet="image.webp" type="image/webp" />
  <img src="image.jpg" loading="lazy" alt="description" />
</picture>
```

### Caching Strategy

```javascript
// Service Worker caching
const CACHE_NAME = 'bowling-hq-v1';
const URLS_TO_CACHE = [
  '/',
  '/styles.css',
  '/app.js',
  '/favicon.ico'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(URLS_TO_CACHE))
  );
});
```

### Database Query Optimization

```python
# N+1 Query Problem - BAD
for session in sessions:
    print(session.user.name)  # Query per session

# GOOD - Use eager loading
sessions = Session.query.options(joinedload(Session.user)).all()
```

### Indexing Strategy

```sql
-- Add indexes for common queries
CREATE INDEX idx_sessions_user_date ON sessions(user_id, date);
CREATE INDEX idx_sessions_date ON sessions(date DESC);
CREATE INDEX idx_videos_session ON videos(session_id);
```

### Caching Layers

```python
# Redis caching
import redis
from functools import wraps

redis_client = redis.Redis()

def cache_result(ttl=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            result = redis_client.get(key)
            if result:
                return json.loads(result)
            
            result = func(*args, **kwargs)
            redis_client.setex(key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

@cache_result(ttl=3600)
def get_user_stats(user_id):
    return User.query.get(user_id).calculate_stats()
```

## Backend Performance

### API Response Optimization

```python
# Pagination
@app.get("/api/sessions")
def get_sessions(page: int = 1, limit: int = 20):
    skip = (page - 1) * limit
    sessions = db.query(Session).skip(skip).limit(limit).all()
    return {"data": sessions, "total": count, "pages": count // limit}
```

### Async Processing

```python
# Use background tasks for heavy operations
from celery import shared_task

@shared_task
def analyze_video(video_id):
    video = Video.query.get(video_id)
    analysis = run_video_analysis(video.path)
    video.analysis = analysis
    db.session.commit()

# Queue task
analyze_video.delay(video_id)
```

### Connection Pooling

```python
# PostgreSQL connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=40,
    pool_recycle=3600
)
```

## Monitoring Performance

### Application Performance Monitoring (APM)

```python
# Sentry integration
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://key@sentry.io/project",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1
)
```

### Database Query Monitoring

```python
# Log slow queries
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, params, context, executemany):
    total_time = time.time() - conn.info['query_start_time'].pop(-1)
    if total_time > 1:  # Log queries slower than 1 second
        logger.warning(f"Slow query ({total_time:.2f}s): {statement}")
```

### Load Testing

```bash
# K6 load testing
k6 run --vus 100 --duration 30s tests/load/api.js
```

## Performance Benchmarks

### Frontend Targets
- **First Contentful Paint (FCP)**: < 1.5s
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Cumulative Layout Shift (CLS)**: < 0.1
- **Time to Interactive (TTI)**: < 3.5s
- **Bundle Size**: < 200KB (gzipped)

### Backend Targets
- **API Response Time**: < 200ms (p95)
- **Database Query Time**: < 100ms (p95)
- **Throughput**: > 1000 req/s
- **Error Rate**: < 0.1%

## Optimization Checklist

- [ ] Code splitting implemented
- [ ] Lazy loading for images
- [ ] Caching strategy in place
- [ ] Database indexes optimized
- [ ] Connection pooling configured
- [ ] CDN enabled
- [ ] Gzip compression enabled
- [ ] Monitoring configured
- [ ] Load tests passing
- [ ] Benchmarks met

---

**This is a comprehensive performance guide for implementation phase.**
