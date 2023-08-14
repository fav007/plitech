import streamlit as st
import pandas as pd
import sqlite3 
import constants
from helpers import *
from PIL import Image
im = Image.open(constants.LOGO_LINK)

st.set_page_config(page_title="Plitech Service",page_icon= im,layout="wide") 

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

       
conn = constants.conn


df = pd.read_sql_query("select * from recap",conn)
st.image(im,width=150)
st.title("Logiciel de gestion d'entreprise")

df