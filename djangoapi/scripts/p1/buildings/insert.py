import psycopg
from myLib import p1Settings
def connect():
    conn= psycopg.connect(
        database=p1Settings.POSTGRES_DB,
        user=p1Settings.POSTGRES_USER,
        password=p1Settings.POSTGRES_PASSWORD,
        host=p1Settings.POSTGRES_HOST,
        port=p1Settings.POSTGRES_PORT
        )
    conn.close()
    print("Done")

