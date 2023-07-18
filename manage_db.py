import sqlite3


def add_columns(column_name):
    conn = sqlite3.connect('plitech_database.db')
    cursor = conn.cursor()
    alter_query = f"ALTER TABLE recap ADD COLUMN {column_name}"
    cursor.execute(alter_query)
    conn.commit()
    conn.close()
    
def delete_row(num):
    conn = sqlite3.connect('plitech_database.db')
    cursor = conn.cursor()

    delete_query = "DELETE FROM recap WHERE num_facture = ?"
    cursor.execute(delete_query, (f"{num}",))

    conn.commit()
    conn.close()

delete_row(None)

