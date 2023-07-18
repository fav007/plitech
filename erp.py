import streamlit as st
import pandas as pd
import sqlite3
import datetime
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Plitech Service",page_icon= "✈"   ) 
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)



# Establish a connection to the SQLite database
conn = sqlite3.connect("plitech_database.db")
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS recap (
	qty integer NOT NULL,
   	is_plain TEXT NOT NULL,
	longueur INTEGER ,
    largeur INTEGER ,
    type TEXT,
    epaisseur TEXT,
    nom_client TEXT,
    date_arrivé TEXT,
    heure_arrivé TEXT,
    total_vente_tole INTEGER,
    total_frais_pliage INTEGER,
    total_remise INTEGER,
    total_chute FLOAT ) ;""")


cond = [2000,1000]
longueur,largeur = 2000 , 1000
thickness_choice = ["25/100","30/100","35/100","40/100","45/100","50/100","55/100","60/100","65/100","7/10",'8/10','9/10','10/10','11/10','12/10','15/10','2mm','3mm','4mm']
    
placeholder_entre_tole = st.empty()

def table_to_df(table):
    query = f"""select * from {table}"""
    df = pd.read_sql_query(query, conn)
    df['qty_tole'] = df["qty"]*df['longueur']*df['largeur']/2000000
    
    return df

def generate_invoice():
    total_tole = 0
    st.write('## Entrée Tôle')
    #st.write('Item\t\tPrice')
    st.write('-' * 30)
    for qty,is_plein,longueur,largeur,item_type, epaiseur in st.session_state["items"]:
        chute = {"Oui":'[chute]',"Non":''}
        st.write(f'{qty} \t {item_type} {epaiseur} \t\t {longueur} x {largeur} {chute[is_plein]}')
        #st.write(f'{qty*longueur*largeur/2_000_000}\t\t {item_type} {epaiseur}')
        total_tole += qty*longueur*largeur/2_000_000
    st.write('-' * 30)
    st.write(f'Total Tôles :\t\t{total_tole:.2f}')
    st.session_state['total_tole'] = total_tole
    
def ajout_tole():
    
    st.write("## Ajout de tôle")
    
    qty = st.number_input("Quantité",1,step=1)
    is_plein = st.radio("Chute",("Non","Oui"))
    if is_plein == "Oui":
        longueur = st.number_input("Longueur",1,value=cond[0],step=1)
        largeur = st.number_input("Largeur",1,value=cond[1],step=1)
    else:
        longueur = 2000
        largeur = 1000
        
    item_type = st.selectbox("type",["TPN","TPG","TPI","TPP"])
    if item_type == 'TPP':
        thickness_choice = ["25/100","30/100","35/100","40/100","45/100","50/100","55/100","60/100","65/100"]
    else :
        thickness_choice = ["7/10",'8/10','9/10','10/10','11/10','12/10','15/10','2mm','3mm','4mm']
        
    epaiseur = st.selectbox("Epaisseur",thickness_choice,1)
    if st.button("Ajouter"):
        st.session_state["items"].append((qty,is_plein,longueur,largeur,item_type, epaiseur))
    if st.button("Effacer"):
        st.session_state["items"].clear()
    if st.button("finaliser"):
        st.success("Toles ajoutés")  


def affiche_table(df):
    st.write(df)
    
def plot_graph(df):
    
    custom_order = ["7/10", "8/10", "9/10", "10/10", "11/10", "12/10", "15/10", "2mm", "3mm", "4mm"]

    # Create a mapping of the custom order to numerical values
    order_mapping = {value: i for i, value in enumerate(custom_order)}

    # Convert 'epaisseur' to numerical values based on the custom order
    df['epaisseur_order'] = df['epaisseur'].map(order_mapping)

    # Sort the DataFrame based on the numerical order
    df.sort_values('epaisseur_order', inplace=True)

    # Create the histogram
    fig, ax = plt.subplots()
    ax.hist(df['epaisseur_order'], weights=df['qty'], bins=np.arange(len(custom_order) + 1))

    # Set the tick labels on the x-axis
    ax.set_xticks(np.arange(len(custom_order)))
    ax.set_xticklabels(custom_order, rotation=45)

    # Set the labels and title
    ax.set_xlabel('Epaisseur')
    ax.set_ylabel('Quantité')
    ax.set_title('Histogram of Epaisseur vs Quantity')

    # Display the histogram in Streamlit
    st.pyplot(fig)

  

    

if "items" not in st.session_state:
    st.session_state.items = []
    
def generate_customers():
    with st.form('customers'):
        st.write("## Information client")
        customers_name = st.text_input("Nom client").upper()
        date_sheet_metal_entry = st.date_input("Date d'entrée")
        time_sheet_metal_entry = st.time_input("Time")
        total_sales_sheet_metal = st.number_input('Total vente tôle en Ar',0,step=100,format="%d")
        total_sales_service = st.number_input('Total frais de pliage en Ar',0,step=100)
        total_discount = st.number_input('Total remise en Ar',0,step=100)
        total_customers_fall_sheet_metal = st.number_input("Chute")
        grand_total = total_sales_service + total_sales_sheet_metal
        if st.form_submit_button():
            u = [w + (customers_name,date_sheet_metal_entry.strftime("%Y-%m-%d"),time_sheet_metal_entry.strftime("%H:%M:%S"),total_sales_sheet_metal,total_sales_service,total_discount,total_customers_fall_sheet_metal) for w in st.session_state['items']]
            st.write(f"Le Client {customers_name} plie {st.session_state['total_tole']} tôles pour un total de : {grand_total:,} Ar le {date_sheet_metal_entry} {time_sheet_metal_entry}")
            for x in u:
                cursor.execute("""INSERT INTO recap(qty,
                                                    is_plain,
                                                    longueur,
                                                    largeur,
                                                    type,
                                                    epaisseur,
                                                    nom_client,
                                                    date_arrivé,
                                                    heure_arrivé,
                                                    total_vente_tole,
                                                    total_frais_pliage,
                                                    total_remise,
                                                    total_chute)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",x)
            conn.commit()
            st.experimental_rerun()
            st.success("ok")


    

def main():
    
    st.title("Logiciel de gestion d'entreprise")
    tabs_title = ["💁 Input","Dashboard"]
    tabs = st.tabs(tabs_title)
    
    with tabs[0]:
        
        df = table_to_df("recap")
        ajout_tole()
        generate_invoice()
        generate_customers()
        affiche_table(df)
        plot_graph(df)
        if st.button("supprimer donnée",disabled=True):
            conn.execute("DELETE FROM recap;")
            conn.commit()
            st.experimental_rerun()
        df.to_csv("a.csv")
        aggregations = {
        'total_vente_tole': 'mean',
        'total_frais_pliage': 'mean',
        'total_remise': 'mean',
        'qty_tole': 'sum',
        'total_chute':sum,
        }

    # Perform the aggregation
        result = df.groupby(['nom_client', 'date_arrivé', 'heure_arrivé']).agg(aggregations)
        ca = result[['total_vente_tole','total_frais_pliage']].sum()

        st.write(result)
        
    with tabs[1]:
        st.title("Dashboard")
        ca = 0
        st.metric("Chiffre d'affaire",f"{ca} ar")
    conn.close()
if __name__ == '__main__':
    main()


