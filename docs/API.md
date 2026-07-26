# API Reference (Planned)

## Overview

Bowling HQ API provides RESTful endpoints for all platform operations. This is a planned API reference for the implementation phase.

## Authentication

All API requests require authentication using JWT tokens.

```bash
Authorization: Bearer <token>
```

## Base URL

```
https://api.bowling-hq.com/v1
```

## Response Format

All responses are JSON:

```json
{
  "success": true,
  "data": { },
  "error": null
}
```

## Core Endpoints (Planned)

### Authentication

```
POST   /auth/register       - Create account
POST   /auth/login          - Get access token
POST   /auth/refresh        - Refresh token
POST   /auth/logout         - Logout
```

### Sessions

```
GET    /sessions            - List user sessions
GET    /sessions/{id}       - Get session details
POST   /sessions            - Create new session
PUT    /sessions/{id}       - Update session
DELETE /sessions/{id}       - Delete session
```

### Video

```
POST   /videos              - Upload video
GET    /videos/{id}         - Get video details
GET    /videos/{id}/analysis - Get analysis results
DELETE /videos/{id}         - Delete video
```

### Analysis

```
GET    /analysis/{type}     - Get analysis by type
GET    /analysis/form       - Get form analysis
GET    /analysis/equipment  - Get equipment analysis
GET    /analysis/patterns   - Get pattern analysis
```

### Commander AI

```
POST   /ai/commander        - Get real-time recommendation
GET    /ai/suggestion       - Get current suggestion
```

### Ghost Bowler

```
GET    /ghost-bowler        - Get baseline stats
GET    /ghost-bowler/compare - Compare to baseline
```

### Arsenal

```
GET    /arsenal             - List equipment
GET    /arsenal/{id}        - Get equipment details
POST   /arsenal             - Add equipment
PUT    /arsenal/{id}        - Update equipment
DELETE /arsenal/{id}        - Delete equipment
```

### Digital Twin

```
POST   /twin/simulate       - Run simulation
GET    /twin/prediction     - Get prediction
```

## Example Requests

### Create Session

```bash
POST /sessions
{
  "date": "2026-07-08",
  "type": "league",
  "venue_id": "123",
  "games": [
    {
      "frames": [10, 9, 0, 10, ...],
      "score": 185,
      "equipment": "ball_id_1"
    }
  ]
}
```

### Upload Video

```bash
POST /videos
Content-Type: multipart/form-data

{
  "file": <video_file>,
  "session_id": "session_123",
  "description": "League night game 1"
}
```

### Get Recommendation

```bash
POST /ai/commander
{
  "current_score": 120,
  "frames_played": 5,
  "lane_condition": "fresh",
  "equipment_in_use": "ball_id_1"
}
```

## Error Responses

```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Description of error",
    "details": { }
  }
}
```

### Error Codes

- `UNAUTHORIZED` - Missing or invalid authentication
- `FORBIDDEN` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `INVALID_REQUEST` - Invalid parameters
- `CONFLICT` - Resource already exists
- `RATE_LIMITED` - Too many requests
- `INTERNAL_ERROR` - Server error

## Rate Limiting

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1625747200
```

Default: 100 requests per hour per user

## Pagination

```bash
GET /sessions?page=1&limit=20&sort=date&order=desc
```

Response:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "pages": 8
  }
}
```

## Filtering

```bash
GET /sessions?date_from=2026-01-01&date_to=2026-12-31&venue_id=123&type=league
```

## WebSocket (Real-time)

For real-time coaching during play:

```bash
ws://api.bowling-hq.com/live/session/{session_id}
```

Messages:
```json
{
  "type": "score_update",
  "frame": 3,
  "pins": 10,
  "recommendation": {...}
}
```

## SDKs

Planned SDKs:
- Python
- JavaScript/TypeScript
- React
- Mobile (iOS/Android)

## Documentation

Full API documentation will be available at:
- Swagger/OpenAPI: `/api/docs`
- Postman Collection: Coming soon

---

**This is a planned API reference. Implementation details will be refined during development.**
