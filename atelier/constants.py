import streamlit as st
from helpers import *



DATABSE_LINK = r"C:\Users\USER\code\fav007\DGD\plitech\plitech_database.db"
LOGO_LINK = r"C:\Users\USER\code\fav007\DGD\plitech\bending.png"

SHEET_METAL_WIDTH = 1000
SHEET_METAL_LENGTH = 2000

conn = connector(DATABSE_LINK)

