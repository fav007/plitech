import sqlite3 as sq

conn = sq.connect("plitech_database.db")
cur = conn.cursor()
query = """
create table billetage (
    date text,
    b20_000 int,
    b10_000 int,
    b5_000 int,
    b2_000 int,
    b1_000 int,
    b_500 int,
    b_200 int,
    b_100 int
    )
"""
cur.execute(query)
conn.commit()
cur.close()
conn.close()