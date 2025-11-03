-- ============================================
-- CASSANDRA SCHEMA FOR PARKING SYSTEM
-- ============================================

-- Create keyspace
CREATE KEYSPACE IF NOT EXISTS parking_system
WITH REPLICATION = {
    'class': 'SimpleStrategy',
    'replication_factor': 1
};

USE parking_system;

-- Table: Lịch sử đỗ xe
CREATE TABLE IF NOT EXISTS parking_history (
    timestamp TIMESTAMP,
    license_plate TEXT,
    location TEXT,
    status_code TEXT,
    parking_duration_minutes DECIMAL,
    parking_fee DECIMAL,
    PRIMARY KEY ((license_plate), timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);

-- Table: Trạng thái hiện tại (để query nhanh)
CREATE TABLE IF NOT EXISTS current_parking_status (
    location TEXT PRIMARY KEY,
    license_plate TEXT,
    status_code TEXT,
    start_time TIMESTAMP,
    parking_duration_minutes DECIMAL,
    parking_fee DECIMAL
);

-- Index để query theo location
CREATE INDEX IF NOT EXISTS idx_location ON parking_history (location);

