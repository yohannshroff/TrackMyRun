DROP TABLE IF EXISTS goals;
DROP TABLE IF EXISTS workout_logs;
DROP TABLE IF EXISTS lifetime_stats;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    userid VARCHAR PRIMARY KEY,
    name VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    unit_preference VARCHAR DEFAULT 'km',
    created_at DATE DEFAULT CURRENT_DATE
);

CREATE TABLE workout_logs (
    logid VARCHAR PRIMARY KEY,
    userid VARCHAR REFERENCES users(userid),
    duration FLOAT NOT NULL,
    distance FLOAT NOT NULL,
    place VARCHAR,
    date DATE,
    pace FLOAT
);

CREATE TABLE goals (
    goalid VARCHAR PRIMARY KEY,
    userid VARCHAR UNIQUE REFERENCES users(userid),
    goal_distance FLOAT,
    goal_duration FLOAT,
    goal_pace FLOAT,
    status VARCHAR
);

CREATE TABLE lifetime_stats (
    userid VARCHAR PRIMARY KEY REFERENCES users(userid),
    total_runs INT DEFAULT 0,
    total_distance FLOAT DEFAULT 0,
    total_duration FLOAT DEFAULT 0,
    avg_pace FLOAT DEFAULT 0,
    start_date DATE,
    end_date DATE,
    consistency FLOAT DEFAULT 0,
    max_pace FLOAT DEFAULT 0,
    max_distance FLOAT DEFAULT 0,
    max_duration FLOAT DEFAULT 0
);