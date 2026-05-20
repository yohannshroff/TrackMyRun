from psycopg2.extras import RealDictCursor
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "database": "trackmyrun",
    "user": "postgres",
    "password": "postgres",
    "port": 5433
}

def get_connection():
    return psycopg2.connect(
        cursor_factory=RealDictCursor,
        **DB_CONFIG
    )