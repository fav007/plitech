import streamlit as st
import pandas as pd
import sqlite3
import datetime
import time
import matplotlib.pyplot as plt
import numpy as np
from millify import millify

st.set_page_config(page_title="Plitech Service",page_icon= "✈") 
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)


conn = sqlite3.connect("plitech_database.db")
cursor = conn.cursor()

aggregations = {
        'total_vente_tole': 'mean',
        'total_frais_pliage': 'mean',
        'total_remise': 'mean',
        'qty_tole': 'sum',
        'total_chute':'sum',
        }

if "items" not in st.session_state:
    st.session_state.items = []


# Establish a connection to the SQLite database

# cursor.execute("""CREATE TABLE IF NOT EXISTS recap (
# 	qty integer NOT NULL,
#    	is_plain TEXT NOT NULL,
# 	longueur INTEGER ,
#     largeur INTEGER ,
#     type TEXT,
#     epaisseur TEXT,
#     nom_client TEXT,
#     date_arrivé TEXT,
#     heure_arrivé TEXT,
#     total_vente_tole INTEGER,
#     total_frais_pliage INTEGER,
#     total_remise INTEGER,
#     total_chute FLOAT ) ;""")


cond = [2000,1000]
longueur,largeur = 2000 , 1000
thickness_choice = ["25/100","30/100","35/100","40/100","45/100","50/100","55/100","60/100","65/100","7/10",'8/10','9/10','10/10','11/10','12/10','15/10','2mm','3mm','4mm']
    
placeholder_entre_tole = st.empty()

def delete_row(num):
    conn = sqlite3.connect('plitech_database.db')
    cursor = conn.cursor()

    delete_query = "DELETE FROM recap WHERE num_facture = ?"
    cursor.execute(delete_query, (f"{num}",))

    conn.commit()
    st.warning(f"facture numéro {num} supprimée",icon="⚠️")
    time.sleep(0.5)
    conn.close()
    st.experimental_rerun()
    

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
    col = st.columns(2)
    with col[0]:
        if st.button("Ajouter"):
            st.session_state["items"].append((qty,is_plein,longueur,largeur,item_type, epaiseur))
    with col[1]:
        if st.button("Effacer"):
            st.session_state["items"].clear()


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
    ax.set_title('Répartition en Tôle Plane')

    # Display the histogram in Streamlit
    st.pyplot(fig)


def generate_customers():
    with st.form('customers'):
        st.write("## Information client")
        customers_name = st.text_input("Nom client").upper()
        date_sheet_metal_entry = st.date_input("Date d'entrée")
        time_sheet_metal_entry = st.time_input("Time")
        num_facture = st.number_input('Numéro Facture',0,step=1)
        total_sales_sheet_metal = st.number_input('Total vente tôle en Ar',0,step=100,format="%d")
        total_sales_service = st.number_input('Total frais de pliage en Ar',0,step=100)
        total_discount = st.number_input('Total remise en Ar',0,step=100)
        total_customers_fall_sheet_metal = st.number_input("Chute")
        grand_total = total_sales_service + total_sales_sheet_metal
        
        if st.form_submit_button():
            u = [w + (customers_name,date_sheet_metal_entry.strftime("%Y-%m-%d"),time_sheet_metal_entry.strftime("%H:%M:%S"),total_sales_sheet_metal,total_sales_service,total_discount,total_customers_fall_sheet_metal,num_facture) for w in st.session_state['items']]
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
                                                    total_chute,
                                                    num_facture)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)""",x)
            conn.commit()
            st.success(f"Facture numéro:{num_facture} au nom de {customers_name} a bien été ajoutée")
            st.session_state["items"].clear()
            st.success("ok")
            st.experimental_rerun()
            
def delete_all():
    cursor.execute("delete from recap")
    conn.commit()
    st.success("Supprimé avec success")
    conn.close()
    st.experimental_rerun()
            
def plot_client(result):
    grouped_data = result.groupby('nom_client')

    # Step 2: Calculate the sum of 'qty_tole' and 'total_frais_pliage' for each 'nom_client'
    sum_qty_tole = grouped_data['qty_tole'].sum()
    sum_total_frais_pliage = grouped_data['total_frais_pliage'].sum()

    # Step 3: Combine the sums into a new DataFrame
    sum_df = pd.DataFrame({
        'sum_qty_tole': sum_qty_tole,
        'sum_total_frais_pliage': sum_total_frais_pliage
    })

    # Step 4: Sort the data based on the calculated sums in descending order
    sum_df = sum_df.sort_values(by=['sum_qty_tole', 'sum_total_frais_pliage'], ascending=False)

    # Step 5: Extract the top 10 'nom_client' based on the sums
    top_12_clients = sum_df.head(12)

    # Step 6: Plot the results
    fig = plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.bar(top_12_clients.index, top_12_clients['sum_qty_tole'])
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Nom Client')
    plt.ylabel('Sum of qty_tole')
    plt.title('Top 12 Nom Clients by Sum of qty_tole')

    plt.subplot(1, 2, 2)
    plt.bar(top_12_clients.index, top_12_clients['sum_total_frais_pliage'])
    plt.xticks(rotation=45, ha='right')
    plt.xlabel('Nom Client')
    plt.ylabel('Sum of total_frais_pliage')
    plt.title('Top 12 Nom Clients by Sum of total_frais_pliage')

    plt.tight_layout()
    st.pyplot(fig)
    
    
def main():
    
    st.title("Logiciel de gestion d'entreprise")
    tabs_title = ["💁 Input","Dashboard","Graph","administration"]
    tabs = st.tabs(tabs_title)
    
    df = table_to_df("recap")
    result = df.groupby(['nom_client', 'date_arrivé', 'heure_arrivé']).agg(aggregations)
    ca = result['total_frais_pliage'].sum() + result['total_vente_tole'].sum()
    t_vente_tole = result['total_vente_tole'].sum()
    t_vente_pliage = result['total_frais_pliage'].sum()
    t_remise = result['total_remise'].sum()
    t_tole_entree = result['qty_tole'].sum()
    t_tole_plie = result['qty_tole'].sum()-result['total_chute'].sum()
    t_chute = result.total_chute.sum()
    #c_top_tole = result.groupby('nom_client')["qty_tole"].sum().sort_values(ascending=False)[0]
    
    with tabs[0]:
        
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
        

    # Perform the aggregation
        result = df.groupby(['nom_client', 'date_arrivé', 'heure_arrivé']).agg(aggregations)
        st.write(result)
        
    with tabs[1]:
        st.title("Dashboard")
        
        
        
        st.write("## Cumul Général")
        st.write("### Finances")
        col = st.columns(5)
        with col[0]:
            st.metric("Chiffre d'affaire",f"{millify(ca, precision=1)}")
        with col[1]:
            st.metric("Tot. recette tôles",f"{millify(t_vente_tole,precision=1)}")
        with col[2]:
            st.metric("Tot. recette pliage",f"{millify(t_vente_pliage,precision=1)}")
        with col[3]:
            st.metric("Tot. remise",f"{millify(t_remise)}")
        
        
        st.write("### Statistique tôle")
        
        col = st.columns(5)
        with col[0]:
            st.metric("Tot. tôle entrée",f"{millify(t_tole_entree)}")
        with col[1]:
            st.metric("Tot. tôle pliés",f"{millify(t_tole_plie)}")
        with col[2]:
            st.metric("Tot. tôle vendus",f"{millify(1)}")
        with col[3]:
            st.metric("Tot. chute tole",f"{millify(t_chute,1)}")
        with col[4]:
            st.metric("Tot. tole perdu",f"{0}")
        
        st.write("### Clients")
        col = st.columns(5)
        with col[0]:
            st.metric("Tot. Clients",f"{df.nom_client.nunique()}")
        # with col[1]:
        #     st.metric("Top chiffre d'affaire",f"{millify(0)}")
        # with col[2]:
        #     st.metric("Top recette tole",f"{millify(0)}")
        # with col[3]:
        #     st.metric("Top nb. tôle",f"{0}")
        # with col[4]:
        #     st.metric("Top remise",f"{0}")
        
    with tabs[2]:
        st.write('## Graphique')
        plot_graph(df)   
        plot_client(result)  
        
    
    
    with tabs[3]:
        st.title("Administration")
        
        
        st.write("## SUpprimé par facture")
        with st.form("administration"):
            num_facture = st.number_input("Numéro Facture",0,step=1)
            if st.form_submit_button("delete"):
                delete_row(num_facture)
                
        st.write("## Tout supprimé")
        if st.button(":red[Tout supprimé]"):
            delete_all()
                

    conn.close()
                
if __name__ == '__main__':
    main()


