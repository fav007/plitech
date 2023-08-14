import constants
import sqlite3
import streamlit as st

def connector(database_link):
    return sqlite3.connect(database_link,check_same_thread=False)

def ajout_tole():
    
    st.write("## Ajout de tôle")
    
    qty = st.number_input("Quantité",1,step=1)
    is_plein = st.radio("Chute",("Non","Oui"),horizontal=True)
    if is_plein == "Oui":
        longueur = st.number_input("Longueur",1,value=constants.SHEET_METAL_LENGTH,step=1)
        largeur = st.number_input("Largeur",1,value=constants.SHEET_METAL_WIDTH,step=1)
        if largeur > longueur:
            longueur,largeur = largeur,longueur
    else:
        longueur = 2000
        largeur = 1000
        
    is_item_sold = st.radio("Vendu",["Non","Plitech","Tojo","Hanitra"],horizontal=True)
        
    item_type = st.selectbox("type",["TPN","TPG","TPI","TPP"])
    
    if item_type == 'TPP':
        thickness_choice = ["25/100","30/100","35/100","40/100","45/100","50/100","55/100","60/100","65/100"]
    else :
        thickness_choice = ["7/10",'8/10','9/10','10/10','11/10','12/10','15/10','2mm','3mm','4mm']
        
    epaiseur = st.selectbox("Epaisseur",thickness_choice,1)
    col = st.columns(2)
    with col[0]:
        if st.button("Ajouter"):
            st.session_state["items"].append((qty,is_plein,longueur,largeur,item_type, epaiseur,is_item_sold))
    with col[1]:
        if st.button("Effacer"):
            st.session_state["items"].clear()
