import sqlite3 as sq
import pandas as pd
import streamlit as st


database_name = "plitech_database.db"




def connect(database_name):
    return sq.connect(database_name,check_same_thread=False)


conn = connect(database_name)
def table_to_df(table_name):
    query = f"""select * from {table_name}"""
    df = pd.read_sql_query(query, conn)
    df['qty_tole'] = df["qty"]*df['longueur']*df['largeur']/2_000_000
    return df
