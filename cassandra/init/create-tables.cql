-- Cassandra schema initialization
-- This will be executed when Cassandra container starts

CREATE KEYSPACE IF NOT EXISTS parking_system
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE parking_system;

CREATE TABLE IF NOT EXISTS parking_history (
    timestamp TIMESTAMP,
    license_plate TEXT,
    location TEXT,
    status_code TEXT,
    parking_duration_minutes DECIMAL,
    parking_fee DECIMAL,
    PRIMARY KEY ((license_plate), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_location ON parking_history (location);
