# Database Migrations

This directory holds future database migration files. As the schema evolves, add numbered migration scripts here:

```
migrations/
├── 001_add_video_analysis.sql
├── 002_add_ghost_bowler_profile.sql
└── ...
```

Use a migration tool like [Flyway](https://flywaydb.org/) or [Alembic](https://alembic.sqlalchemy.org/) for managed migrations in Phase 2+.
