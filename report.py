from fpdf import FPDF
import sqlite3 
import pandas as pd

WIDTH = 210
HEIGHT = 297

sql = """ select * from recap

"""

with sqlite3.Connection('plitech_database.db') as conn:
    cur = conn.cursor()
    df = pd.read_sql_query(sql,conn)
    
df['date_arrivé'] = pd.to_datetime(df.date_arrivé)    
date_debut = df.date_arrivé.min()
date_fin = df.date_arrivé.max()
t_tole_plie = df.qty_tole.sum()

pdf = FPDF()
pdf.add_page()
pdf.set_font('Helvetica', 'B', 24)
pdf.cell(105, 10, '',ln=True)
pdf.cell(0, 15, f'Rapport plitech service',ln=1,align='C')
pdf.cell(0,15,f'{date_debut.strftime("%d-%m-%Y")} au {date_fin.strftime("%d-%m-%Y")}',align='C',ln=1)
pdf.set_font('Helvetica', '', 12)
pdf.cell(0,10,f"Total Tôle plié: {t_tole_plie:.0f}")

pdf.output('tuto1.pdf', 'F')
