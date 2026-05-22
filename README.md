# TrackMyRun

TrackMyRun is a full-stack running tracker web application built with FastAPI, PostgreSQL, HTML, CSS, JavaScript, and JWT authentication.

Users can log workouts, set running goals, track lifetime statistics, view workout history, monitor pace and consistency, and stay motivated with random quotes.

---

## Features

### Authentication

- JWT-based login system
- Secure password hashing using bcrypt
- Protected API routes
- User-specific data access
- Logout support

### Workout Logging

Users can:

- Log running workouts
- Store distance, duration, place, and date
- Automatically calculate pace
- Edit existing workouts
- Delete workouts
- Prevent future-date workout logs

### Goal Tracking

Users can set goals for:

- Distance
- Duration

Goal behavior:

- Active goals are displayed on the dashboard
- Goals persist until completed
- Goals are automatically cleared once achieved
- Users can replace an existing active goal anytime

### Lifetime Statistics

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

### Motivational Quotes

A random motivational quote is displayed every time the dashboard loads.

---

## Tech Stack

### Backend

- Python
- FastAPI
- PostgreSQL
- psycopg2
- python-jose
- passlib
- bcrypt
- Jinja2

### Frontend

- HTML
- CSS
- Vanilla JavaScript

### Database

- PostgreSQL
- Docker PostgreSQL setup supported

---

## Project Structure

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
│   │   └── login.js
│   │
│   └── templates/
│       ├── login.html
│       └── dashboard.html
│
├── docker-compose.yml
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Database Schema

The project uses PostgreSQL with the following tables:

- `users`
- `workout_logs`
- `goals`
- `lifetime_stats`

---

## Dummy Login Credentials

Use this account after seeding the database:

```text
Username: y
Password: y
```

---

## Setup Instructions

### 1. Clone The Repository

```bash
git clone https://github.com/yohannshroff/TrackMyRun.git
cd TrackMyRun
```

---

### 2. Create A Virtual Environment

```bash
python -m venv venv
```

Activate it:

#### macOS / Linux

```bash
source venv/bin/activate
```

#### Windows

```bash
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is missing, create one with:

```text
fastapi
uvicorn
jinja2
python-multipart
psycopg2-binary
python-jose
passlib[bcrypt]
bcrypt==4.0.1
```

Then run:

```bash
pip install -r requirements.txt
```

---

## PostgreSQL Setup With Docker

This project is configured to work with Docker PostgreSQL.

### 1. Start PostgreSQL

From the project root:

```bash
docker compose up -d
```

This starts PostgreSQL using the settings from `docker-compose.yml`.

Default database settings:

```text
Database: trackmyrun
User: postgres
Password: postgres
Port: 5433
```

---

### 2. Run The Schema

From the project root:

```bash
docker exec -i trackmyrun_db psql -U postgres -d trackmyrun < app/schema.sql
```

If your container name is different, check it with:

```bash
docker ps
```

Then replace `trackmyrun_db` with the correct container name.

---

### 3. Seed The Demo User

Go into the app folder:

```bash
cd app
```

Run:

```bash
python seed.py
```

You should see:

```text
Seed completed.
```

This creates the demo user:

```text
Username: y
Password: y
```

---

## Database Configuration

The app connects to PostgreSQL using `app/database.py`.

For Docker PostgreSQL, it should look like this:

```python
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
```

---

## Run The Application

Make sure you are inside the `app` folder:

```bash
cd app
```

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

The app will run at:

```text
http://127.0.0.1:8000
```

Open that URL in your browser.

---

## First-Time Run Commands

From the project root:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
docker compose up -d
docker exec -i trackmyrun_db psql -U postgres -d trackmyrun < app/schema.sql
cd app
python seed.py
uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

Login with:

```text
Username: y
Password: y
```

---

## Normal Run Commands

After the first setup, use:

```bash
source venv/bin/activate
docker compose up -d
cd app
uvicorn main:app --reload
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/login` | Login user and return JWT token |
| GET | `/logout` | Logout route |

---

### Quotes

| Method | Endpoint | Description |
|---|---|---|
| GET | `/quotes/random` | Fetch a random motivational quote |

---

### Goals

| Method | Endpoint | Description |
|---|---|---|
| GET | `/users/{userid}/goal` | Fetch active goal |
| POST | `/users/{userid}/goal` | Set or replace active goal |

---

### Workout Logs

| Method | Endpoint | Description |
|---|---|---|
| GET | `/users/{userid}/logs` | Fetch workout history |
| POST | `/users/{userid}/logs` | Create workout log |
| PATCH | `/users/{userid}/logs/{logid}` | Edit workout log |
| DELETE | `/users/{userid}/logs/{logid}` | Delete workout log |

---

### Statistics

| Method | Endpoint | Description |
|---|---|---|
| GET | `/users/{userid}/stats` | Fetch lifetime statistics |

---

## JWT Authentication

TrackMyRun uses JWT tokens for authentication.

After login:

- A JWT token is generated by the backend
- The token is stored in browser `localStorage`
- The token is sent with protected API requests using the `Authorization` header

Example:

```text
Authorization: Bearer <token>
```

Note: JWT is stored in `localStorage` for simplicity in this educational project. In production, HTTP-only secure cookies are usually safer.

---

## Date Handling

Workout dates are stored internally in `YYYY-MM-DD` format because that is the standard format used by HTML date inputs and PostgreSQL.

On the dashboard, dates are displayed as:

```text
DD-MM-YYYY
```

The app prevents users from creating or editing workout logs for future dates.

---

## Example Features Demonstrated

- JWT authentication
- Password hashing with bcrypt
- Protected API routes
- CRUD operations
- PostgreSQL database integration
- Goal management
- Lifetime statistics aggregation
- Dynamic frontend updates
- Docker PostgreSQL setup
- Date validation
- Responsive dashboard UI

---

## Running Tests

If tests are added, they can be run with:

```bash
pytest
```

Recommended test categories:

```bash
pytest tests/unit
pytest tests/integration
pytest tests/e2e
```

---

## Future Improvements

Potential future enhancements:

- Add charts and analytics
- Add weekly and monthly reports
- Move dashboard JavaScript into a separate `dashboard.js` file
- Add a polished edit modal instead of browser prompts
- Add user registration
- Add email/password reset
- Add route mapping with GPS
- Add dark/light theme toggle
- Add CI/CD pipeline
- Deploy the app online

---

## Author

Built by Yohann Shroff.