# Database Directory

This directory contains database schemas, migrations, and seed data for Bowling-HQ.

## Structure

```
database/
├── schemas/               → Database schema definitions
│   ├── postgres.sql      → PostgreSQL table definitions
│   ├── mongodb.js        → MongoDB collection initialization
│   └── redis.conf        → Redis configuration (if needed)
├── seeds/                 → Initial data
│   ├── ghost_bowler_level1.json  → Thomas's initial profile
│   ├── arsenal.json              → All bowling balls
│   ├── patterns.json             → Bowling patterns
│   ├── centers.json              → Bowling centers
│   └── thomas_sessions.json      → Sample session data
├── migrations/            → Future: Database migrations
│   └── README.md
└── README.md             → This file
```

## PostgreSQL Tables

- `users` - User profiles
- `bowling_sessions` - Session records (league/tournament/practice)
- `games` - Individual games within sessions
- `frames` - Individual frames within games
- `bowling_centers` - Center information
- `patterns` - Lane pattern definitions
- `recommendations` - Historical recommendations

## MongoDB Collections

- `ghost_bowler_profiles` - Thomas's digital twin models
- `arsenal_database` - Ball records and metadata
- `commander_recommendations` - Historical recommendations
- `session_analytics` - Computed analytics

## Redis Keys

- `user:{id}:ghost_bowler` - Cached Ghost Bowler profile
- `user:{id}:recommendations:cache` - Cached recommendations
- `pattern:{id}:trending` - Live pattern trend data

## Getting Started

```bash
# Load PostgreSQL schema
psql -U postgres -d bowling_hq -f schemas/postgres.sql

# Load MongoDB collections
mongosh bowling_hq < schemas/mongodb.js

# Load seed data
python load_seeds.py
```

## Seed Data

See individual JSON files in `seeds/` for initial data structure.

## Development

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development guidelines.