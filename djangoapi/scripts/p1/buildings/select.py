from myLib.connect import connect
from psycopg.rows import dict_row

def select():
    conn=connect()
    cur=conn.cursor(row_factory=dict_row)
    cons="""
        SELECT 
            description, area,st_astext(geom)
        FROM 
            d.buildings 
        WHERE
            id>%s
        """
    cur.execute(cons, [0])
    l=cur.fetchall()
    print(l)
    print('First row:')
    print(l[0])
    conn.commit()
    cur.close()
    conn.close()
    print("Selected")


