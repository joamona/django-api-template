import psycopg
from myLib import p1Settings
def connect():
    conn= psycopg.connect(
        dbname=p1Settings.POSTGRES_DB,
        user=p1Settings.POSTGRES_USER,
        password=p1Settings.POSTGRES_PASSWORD,
        host=p1Settings.POSTGRES_HOST,
        port=p1Settings.POSTGRES_PORT
        )
    print("Connected")
    return conn

def insert():
    conn=connect()
    cur=conn.cursor()
    cons="""
        INSERT INTO d.buildings 
            (description, area)
        VALUES
            (%s,%s)
        """
    cur.execute(cons,['My first building', 100])
    conn.commit()
    cur.close()
    conn.close()
    print("Inserted")


