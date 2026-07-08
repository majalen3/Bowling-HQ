db = db.getSiblingDB(process.env.MONGO_DB || 'bowling_hq');

db.createCollection('ghost_bowler_profiles');
db.createCollection('arsenal_database');
db.createCollection('session_analytics');

db.ghost_bowler_profiles.createIndex({ userId: 1 }, { unique: true });
db.arsenal_database.createIndex({ ownerId: 1, name: 1 }, { unique: true });
db.session_analytics.createIndex({ sessionId: 1 }, { unique: true });
