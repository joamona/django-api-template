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
            (description, area,geom)
        VALUES
            (%s,%s,
            st_geometryFromText(%s,25830))
        RETURNING id
        """
    cur.execute(cons,
                ['My first building',
                 100,
                 'POLYGON((0 0, 100 0, 100 100, 0 100, 0 0))'
                 ])
    conn.commit()
    cur.close()
    conn.close()
    print("Inserted")


