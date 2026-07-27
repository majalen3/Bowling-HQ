# Migrations

Apply migrations in lexical order after the base schema.

- `001_session_progress_indexes.sql` adds indexes used by session progress
  workflows.
- `003_vertical_slice_tables.sql` adds Ghost Bowler, Pattern Intelligence,
  and Simulator persistence tables.
