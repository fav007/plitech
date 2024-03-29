import sqlite3


def add_columns(column_name):
    with sqlite3.connect('plitech_database.db') as conn:
        cursor = conn.cursor()
        alter_query = f"ALTER TABLE recap ADD COLUMN {column_name}"
        cursor.execute(alter_query)
        conn.commit()
    
def delete_row(num):
    conn = sqlite3.connect('plitech_database.db')
    cursor = conn.cursor()

    delete_query = "DELETE FROM recap WHERE num_facture = ?"
    cursor.execute(delete_query, (f"{num}",))

    conn.commit()
    conn.close()

def update_row():
    with sqlite3.connect('plitech_database.db') as conn:
        cur = conn.cursor()
        sql = "UPDATE recap SET nom_client = 'TINA' WHERE num_facture = 57"
        cur.execute(sql)
        conn.commit()

add_columns("is_item_sold")
