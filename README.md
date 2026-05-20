# TrackMyRun

A full-stack running tracker web application built with:

- Python
- FastAPI
- PostgreSQL
- HTML
- CSS
- JavaScript
- JWT Authentication

TrackMyRun allows users to:

- Log workouts
- Set fitness goals
- Track lifetime statistics
- View workout history
- Monitor pace and consistency
- Stay motivated with random quotes

---

# Features

## Authentication

- JWT-based login system
- Secure password hashing using bcrypt
- Protected API routes
- User-specific data access
- Logout support

---

## Workout Logging

Users can:

- Log running workouts
- Store:
  - distance
  - duration
  - place
  - date
- Automatically calculate pace
- Edit existing workouts
- Delete workouts

---

## Goal Tracking

Users can set goals for:

- Distance
- Duration

Goal behavior:

- Active goals are displayed on the dashboard
- Goals persist until completed
- Goals are automatically cleared once achieved
- Users can replace existing goals anytime

---

## Lifetime Statistics

Automatically calculated statistics include:

- Total runs
- Total distance
- Total duration
- Average pace
- Consistency percentage
- Pace PR
- Longest run
- Longest duration
- Start tracking date
- Latest run date

---

## Motivational Quotes

Random motivational quotes are displayed every time the dashboard loads.

---

# Tech Stack

## Backend

- FastAPI
- PostgreSQL
- psycopg2
- python-jose
- passlib
- bcrypt

## Frontend

- HTML
- CSS
- Vanilla JavaScript

---

# Project Structure

```text
trackmyrun/
│
├── app/
│   ├── main.py
│   ├── auth.py
│   ├── database.py
│   ├── utils.py
│   ├── seed.py
│   ├── schema.sql
│   │
│   ├── static/
│   │   ├── style.css
│   │   ├── login.js
│   │   └── dashboard.js
│   │
│   └── templates/
│       ├── login.html
│       └── dashboard.html
│
├── venv/
│
└── README.md
```

---

# Database Schema

The project uses PostgreSQL with the following tables:

- users
- workout_logs
- goals
- lifetime_stats

---

# Setup Instructions

## 1. Clone The Repository

```bash
git clone <your-repo-url>
cd trackmyrun
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

### macOS/Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 3. Install Dependencies

```bash
pip install fastapi uvicorn psycopg2-binary python-jose passlib bcrypt python-multipart jinja2
```

---

# PostgreSQL Setup

## 1. Start PostgreSQL

Make sure PostgreSQL is running.

---

## 2. Create Database

Open psql:

```bash
psql -U <your_postgres_username>
```

Create database:

```sql
CREATE DATABASE trackmyrun;
```

Connect to it:

```sql
\c trackmyrun
```

---

## 3. Run Schema

Inside the project folder:

```bash
psql -U <your_postgres_username> -d trackmyrun -f app/schema.sql
```

---

# Configure Database

Open:

```text
app/database.py
```

Update credentials if necessary:

```python
DB_CONFIG = {
    "host": "localhost",
    "database": "trackmyrun",
    "user": "your_username",
    "password": "your_password",
    "port": 5432
}
```

---

# Seed Dummy User

Run:

```bash
cd app
python seed.py
```

This creates a test account.

---

# Dummy Login Credentials

```text
Username: y
Password: y
```

---

# Run The Application

Inside the `app` folder:

```bash
uvicorn main:app --reload
```

Application runs at:

```text
http://127.0.0.1:8000
```

---

# API Endpoints

## Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/login` | Login user |
| GET | `/logout` | Logout user |

---

## Quotes

| Method | Endpoint |
|---|---|
| GET | `/quotes/random` |

---

## Goals

| Method | Endpoint |
|---|---|
| GET | `/users/{userid}/goal` |
| POST | `/users/{userid}/goal` |

---

## Workout Logs

| Method | Endpoint |
|---|---|
| GET | `/users/{userid}/logs` |
| POST | `/users/{userid}/logs` |
| PATCH | `/users/{userid}/logs/{logid}` |
| DELETE | `/users/{userid}/logs/{logid}` |

---

## Statistics

| Method | Endpoint |
|---|---|
| GET | `/users/{userid}/stats` |

---

# JWT Authentication

TrackMyRun uses JWT tokens for authentication.

After login:

- A JWT token is generated
- Stored in browser localStorage
- Sent in Authorization headers

Example:

```text
Authorization: Bearer <token>
```

---

# Running Tests

## Unit Tests

```bash
pytest tests/unit
```

## Integration Tests

```bash
pytest tests/integration
```

## End-To-End Tests

```bash
pytest tests/e2e
```

---

# Example Features Demonstrated

- JWT Authentication
- CRUD Operations
- REST APIs
- Protected Routes
- PostgreSQL Integration
- Goal Management
- Dynamic Frontend Updates
- Statistics Aggregation

---

# Future Improvements

Potential future enhancements:

- Charts and analytics
- Dark/light theme toggle
- Mobile app support
- Social sharing
- Weekly/monthly reports
- Route mapping with GPS
- Docker deployment
- CI/CD pipeline

---

# Author

Built by Yohann Shroff.
