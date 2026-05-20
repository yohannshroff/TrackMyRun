import uuid
from database import get_connection
from auth import hash_password

conn = get_connection()
cursor = conn.cursor()

hashed = hash_password("y")

cursor.execute("""
INSERT INTO users(userid, name, password)
VALUES(%s,%s,%s)
ON CONFLICT DO NOTHING
""", (
    "y",
    "y",
    hashed
))

cursor.execute("""
INSERT INTO lifetime_stats(userid)
VALUES(%s)
ON CONFLICT DO NOTHING
""", ("y",))

conn.commit()

print("Seed completed.")

cursor.close()
conn.close()