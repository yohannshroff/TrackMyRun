from datetime import date
import uuid

from fastapi import Depends, FastAPI, Form, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt
from pydantic import BaseModel

from auth import ALGORITHM, SECRET_KEY, create_access_token, verify_password
from database import get_connection
from utils import calculate_pace, get_random_quote


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# =========================================================
# MODELS
# =========================================================

class GoalPayload(BaseModel):
    goalDistance: float | None = None
    goalDuration: float | None = None


class LogPayload(BaseModel):
    duration: float
    distance: float
    place: str
    date: str


# =========================================================
# AUTH HELPERS
# =========================================================

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


def get_current_user(authorization: str | None = Header(default=None)):
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header"
        )

    payload = verify_token(token)

    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    return payload["sub"]


def resolve_userid(userid: str, current_user: str):
    if userid == "me":
        return current_user

    if userid != current_user:
        raise HTTPException(
            status_code=403,
            detail="You can only access your own data"
        )

    return userid


def validate_log_date(log_date_string: str):
    try:
        log_date = date.fromisoformat(log_date_string)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use YYYY-MM-DD."
        )

    if log_date > date.today():
        raise HTTPException(
            status_code=400,
            detail="You cannot create or update logs for future dates."
        )

    return log_date_string


# =========================================================
# FRONTEND ROUTES
# =========================================================

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html"
    )


# =========================================================
# LOGIN / LOGOUT
# =========================================================

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE userid=%s",
        (username,)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if not user or not verify_password(password, user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": username})

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@app.get("/logout")
def logout():
    return RedirectResponse("/")


# =========================================================
# QUOTES
# =========================================================

@app.get("/quotes/random")
def random_quote(current_user: str = Depends(get_current_user)):
    return {
        "quote": get_random_quote()
    }


# =========================================================
# STATS
# =========================================================

@app.get("/users/{userid}/stats")
def get_stats(
    userid: str,
    current_user: str = Depends(get_current_user)
):
    userid = resolve_userid(userid, current_user)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM lifetime_stats WHERE userid=%s",
        (userid,)
    )

    stats = cursor.fetchone()

    cursor.close()
    conn.close()

    return stats or {}


def recalculate_stats(userid: str, conn):
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM workout_logs
        WHERE userid=%s
        """,
        (userid,)
    )

    logs = cursor.fetchall()

    if not logs:
        cursor.execute(
            """
            UPDATE lifetime_stats
            SET total_runs=0,
                total_distance=0,
                total_duration=0,
                avg_pace=0,
                start_date=NULL,
                end_date=NULL,
                consistency=0,
                max_pace=0,
                max_distance=0,
                max_duration=0
            WHERE userid=%s
            """,
            (userid,)
        )

        cursor.close()
        return

    total_runs = len(logs)
    total_distance = sum(log["distance"] for log in logs)
    total_duration = sum(log["duration"] for log in logs)

    avg_pace = round(total_distance / total_duration, 2) if total_duration else 0

    max_pace = max(log["pace"] for log in logs)
    max_distance = max(log["distance"] for log in logs)
    max_duration = max(log["duration"] for log in logs)

    dates = [log["date"] for log in logs]

    start_date = min(dates)
    end_date = max(dates)

    total_days = (end_date - start_date).days + 1
    unique_run_days = len(set(dates))

    consistency = round((unique_run_days / total_days) * 100, 2)
    consistency = min(consistency, 100)

    cursor.execute(
        """
        UPDATE lifetime_stats
        SET total_runs=%s,
            total_distance=%s,
            total_duration=%s,
            avg_pace=%s,
            start_date=%s,
            end_date=%s,
            consistency=%s,
            max_pace=%s,
            max_distance=%s,
            max_duration=%s
        WHERE userid=%s
        """,
        (
            total_runs,
            total_distance,
            total_duration,
            avg_pace,
            start_date,
            end_date,
            consistency,
            max_pace,
            max_distance,
            max_duration,
            userid
        )
    )

    cursor.close()


# =========================================================
# GOALS
# =========================================================

@app.get("/users/{userid}/goal")
def get_goal(
    userid: str,
    current_user: str = Depends(get_current_user)
):
    userid = resolve_userid(userid, current_user)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM goals
        WHERE userid=%s AND status='active'
        """,
        (userid,)
    )

    goal = cursor.fetchone()

    cursor.close()
    conn.close()

    if not goal:
        return {
            "active": False,
            "goal_distance": None,
            "goal_duration": None,
            "goal_pace": None
        }

    return {
        "active": True,
        "goal_distance": goal["goal_distance"],
        "goal_duration": goal["goal_duration"],
        "goal_pace": goal["goal_pace"]
    }


@app.post("/users/{userid}/goal")
def set_goal(
    userid: str,
    goal: GoalPayload,
    current_user: str = Depends(get_current_user)
):
    userid = resolve_userid(userid, current_user)

    goal_pace = None

    if goal.goalDistance and goal.goalDuration:
        goal_pace = calculate_pace(
            goal.goalDistance,
            goal.goalDuration
        )

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO goals(
                goalid,
                userid,
                goal_distance,
                goal_duration,
                goal_pace,
                status
            )
            VALUES(%s,%s,%s,%s,%s,'active')
            ON CONFLICT(userid)
            DO UPDATE SET
                goal_distance=EXCLUDED.goal_distance,
                goal_duration=EXCLUDED.goal_duration,
                goal_pace=EXCLUDED.goal_pace,
                status='active'
            """,
            (
                str(uuid.uuid4()),
                userid,
                goal.goalDistance,
                goal.goalDuration,
                goal_pace
            )
        )

        conn.commit()

        return {
            "message": "Goal saved"
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        cursor.close()
        conn.close()


def active_goal_is_hit(goal, log: LogPayload):
    if not goal:
        return False

    if goal["goal_distance"] is not None and log.distance < goal["goal_distance"]:
        return False

    if goal["goal_duration"] is not None and log.duration < goal["goal_duration"]:
        return False

    return True


def complete_goal_if_hit(userid: str, log: LogPayload, conn):
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM goals
        WHERE userid=%s AND status='active'
        """,
        (userid,)
    )

    goal = cursor.fetchone()

    if not active_goal_is_hit(goal, log):
        cursor.close()
        return False

    cursor.execute(
        """
        UPDATE goals
        SET status='completed'
        WHERE goalid=%s
        """,
        (goal["goalid"],)
    )

    cursor.close()
    return True


# =========================================================
# WORKOUT LOGS
# =========================================================

@app.get("/users/{userid}/logs")
def get_logs(
    userid: str,
    current_user: str = Depends(get_current_user)
):
    userid = resolve_userid(userid, current_user)

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM workout_logs
        WHERE userid=%s
        ORDER BY date DESC
        """,
        (userid,)
    )

    logs = cursor.fetchall()

    cursor.close()
    conn.close()

    return logs


@app.post("/users/{userid}/logs")
def create_log(
    userid: str,
    log: LogPayload,
    current_user: str = Depends(get_current_user)
):
    userid = resolve_userid(userid, current_user)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        validated_date = validate_log_date(log.date)

        pace = calculate_pace(
            log.distance,
            log.duration
        )

        cursor.execute(
            """
            SELECT *
            FROM lifetime_stats
            WHERE userid=%s
            """,
            (userid,)
        )

        previous = cursor.fetchone()

        if not previous:
            cursor.execute(
                """
                INSERT INTO lifetime_stats(userid)
                VALUES(%s)
                ON CONFLICT DO NOTHING
                """,
                (userid,)
            )

            previous = {
                "max_pace": 0,
                "max_distance": 0,
                "max_duration": 0
            }

        message = f"Your pace was {pace} km/min!"

        if pace > previous["max_pace"]:
            message += f"\nCongratulations! You beat your pace PR of {previous['max_pace']}!"

        if log.distance > previous["max_distance"]:
            message += "\nCongratulations! This is the longest run yet!"

        if log.duration > previous["max_duration"]:
            message += "\nCongratulations! This is the longest duration yet!"

        cursor.execute(
            """
            INSERT INTO workout_logs(
                logid,
                userid,
                duration,
                distance,
                place,
                date,
                pace
            )
            VALUES(%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                str(uuid.uuid4()),
                userid,
                log.duration,
                log.distance,
                log.place,
                validated_date,
                pace
            )
        )

        recalculate_stats(userid, conn)

        if complete_goal_if_hit(userid, log, conn):
            message += "\nGoal achieved! Your active goal has been cleared."

        conn.commit()

        return {
            "message": message
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        cursor.close()
        conn.close()


@app.patch("/users/{userid}/logs/{logid}")
def update_log(
    userid: str,
    logid: str,
    log: LogPayload,
    current_user: str = Depends(get_current_user)
):
    userid = resolve_userid(userid, current_user)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        validated_date = validate_log_date(log.date)

        pace = calculate_pace(
            log.distance,
            log.duration
        )

        cursor.execute(
            """
            UPDATE workout_logs
            SET duration=%s,
                distance=%s,
                place=%s,
                date=%s,
                pace=%s
            WHERE logid=%s AND userid=%s
            """,
            (
                log.duration,
                log.distance,
                log.place,
                validated_date,
                pace,
                logid,
                userid
            )
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Log not found"
            )

        recalculate_stats(userid, conn)

        conn.commit()

        return {
            "message": "Updated"
        }

    except HTTPException:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        cursor.close()
        conn.close()


@app.delete("/users/{userid}/logs/{logid}")
def delete_log(
    userid: str,
    logid: str,
    current_user: str = Depends(get_current_user)
):
    userid = resolve_userid(userid, current_user)

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            DELETE FROM workout_logs
            WHERE logid=%s AND userid=%s
            """,
            (logid, userid)
        )

        if cursor.rowcount == 0:
            raise HTTPException(
                status_code=404,
                detail="Log not found"
            )

        recalculate_stats(userid, conn)

        conn.commit()

        return {
            "message": "Deleted"
        }

    except HTTPException:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()