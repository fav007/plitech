import streamlit as st
import pandas as pd
import sqlite3
import datetime
import time
import matplotlib.pyplot as plt
import numpy as np
from millify import millify
import plotly.express as px
from plotly_calplot import calplot
from PIL import Image
import locale
from helpers import table_to_df
ma_locale = locale.setlocale(locale.LC_ALL, '')

# total sales
# total orders
# average order value
# returning customer rate
im = Image.open("bending.png")
st.set_page_config(page_title="Plitech Service",page_icon= im) 
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

#image_client = Image.open("C:\Users\USER\code\fav007\DGD\plitech\client.png")

conn = sqlite3.connect("plitech_database.db")
cursor = conn.cursor()

aggregations = {
        'total_vente_tole': 'mean',
        'total_frais_pliage': 'mean',
        'total_remise': 'mean',
        'qty_tole': 'sum',
        'total_chute':'sum',
        'num_facture':'mean'
        }

cond = [2000,1000]
longueur,largeur = 2000 , 1000
thickness_choice = ["25/100","30/100","35/100","40/100","45/100","50/100","55/100","60/100","65/100","7/10",'8/10','9/10','10/10','11/10','12/10','15/10','2mm','3mm','4mm']

if "items" not in st.session_state:
    st.session_state.items = []




    
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
    



def generate_invoice():
    
    total_tole = 0
    st.write('## Entrée Tôle')
    st.write('-' * 30)
    for qty,is_plein,longueur,largeur,item_type, epaiseur,is_item_sold in st.session_state["items"]:
        owner = is_item_sold
        chute = {"Oui":'[chute]',"Non":''}
        if is_item_sold == 'Non':
            owner = 'Client'
        
        st.write(f'{qty} \t {item_type} {epaiseur} \t\t {longueur} x {largeur} {chute[is_plein]} [{owner}]')
        total_tole += qty*longueur*largeur/2_000_000
    st.write('-' * 30)
    st.write(f'Total Tôles :\t\t{total_tole:.2f}')
    st.session_state['total_tole'] = total_tole
    
def ajout_tole():
    
    st.write("## Ajout de tôle")
    
    qty = st.number_input("Quantité",1,step=1)
    is_plein = st.radio("Chute",("Non","Oui"),horizontal=True)
    if is_plein == "Oui":
        longueur = st.number_input("Longueur",1,value=cond[0],step=1)
        largeur = st.number_input("Largeur",1,value=cond[1],step=1)
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


def affiche_table(df):
    st.write(df)
    
def plot_graph(df):
    
    custom_order = ["30/100","40/100","60/100","7/10", "8/10", "9/10", "10/10", "11/10", "12/10", "15/10", "2mm", "3mm", "4mm"]

    # Create a mapping of the custom order to numerical values
    order_mapping = {value: i for i, value in enumerate(custom_order)}

    # Convert 'epaisseur' to numerical values based on the custom order
    df['epaisseur_order'] = df['epaisseur'].map(order_mapping)

    # Sort the DataFrame based on the numerical order
    df.sort_values('epaisseur_order', inplace=True)

    # Create the histogram
    fig, ax = plt.subplots()
    ax.hist(df['epaisseur_order'], weights=df['qty_tole'], bins=np.arange(len(custom_order) + 1))

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
        time_sheet_metal_entry = st.time_input("Time",step=60)
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
                                                    is_item_sold,
                                                    nom_client,
                                                    date_arrivé,
                                                    heure_arrivé,
                                                    total_vente_tole,
                                                    total_frais_pliage,
                                                    total_remise,
                                                    total_chute,
                                                    num_facture)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)""",x)
            conn.commit()
            st.toast(f"""
                       Facture numéro:{num_facture} au nom de {customers_name} a bien été ajoutée \n
                       Frais pliage : {total_sales_service} \n
                       Vente tôle : {total_sales_sheet_metal} \n
                       """)
            st.session_state["items"].clear()
            st.success("ok")
            time.sleep(1)
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

    st.pyplot(fig)
    
def plot_by_month(result):
    result.reset_index(inplace = True)
    result['date_arrivé'] = pd.to_datetime(result['date_arrivé'])

    # Step 2: Extract the month and year from 'date_arrivé'
    result['month_year'] = result['date_arrivé'].dt.to_period('M')

    # Step 3: Group the data by month and year, and calculate the sum of 'total_frais_pliage'
    grouped_data = result.groupby('month_year')['total_frais_pliage'].sum()

    # Create a Streamlit app
    st.title('Total Frais Pliage by Month-Year')
    st.write('This app displays the total frais pliage by month and year.')

    # Show the data table (optional)

    # Plot the data using matplotlib and display it in Streamlit
    plt.figure(figsize=(10, 6))
    plt.bar(grouped_data.index.astype(str), grouped_data.values)
    plt.xlabel('Month-Year')
    plt.ylabel('Total Frais Pliage')
    plt.title('Total Frais Pliage by Month-Year')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Show the plot using Streamlit
    st.pyplot(plt)




    
    
def main():
    st.image(im,width=150)
    st.title("Logiciel de gestion d'entreprise")
    tabs_title = ["💁 Input","Dashboard","Graph","administration","Billetage"]
    tabs = st.tabs(tabs_title)
    
    df = table_to_df("recap")
    result = df.groupby(['nom_client', 'date_arrivé', 'heure_arrivé']).agg(aggregations)
    result["frais_par_tole"] = result['total_frais_pliage']/result['qty_tole']
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
        
        st.write("### Factures")
        col = st.columns(5)
        with col[0]:
            st.metric("Nbr. Factures",df.num_facture.nunique())
        with col[1]:
            st.metric("Dern. Factures",df.num_facture.max())
        with col[2]:
            st.metric("Fact. Non Enr.",2)
            
        st.write("## KPI Marketing")
        col = st.columns(3)
        with col[0]:
            st.metric("Nombre clients",df.nom_client.nunique())
        with col[1]:
            st.metric("Freq. clients",millify(result.reset_index().nom_client.value_counts().mean(),precision=2))
        with col[2]:
            st.metric("Panier moyen",millify(result.reset_index().groupby("nom_client")["total_frais_pliage"].mean().mean(),precision=2))
        
        
    with tabs[2]:
        st.write('## Graphique')
        plot_by_month(result)
        plot_graph(df)   
        plot_client(result)  
        
        plt.figure()
        result.nom_client.value_counts().head(12).plot(kind='bar')
        plt.title('Fréquence client')
        plt.xlabel("Clients")
        plt.xticks(rotation=45, ha='right')
        #plt.tight_layout()
        st.pyplot(plt)
        
        plt.figure()
        result.groupby('nom_client')['frais_par_tole'].mean().sort_values(ascending=False).head(12).plot(kind='bar')
        plt.ylabel("Moyenne pliage par tole par client")
        plt.ylim(0,50000)
        st.pyplot(plt)
        
        st.write("### Panier moyen frais pliage")
        plt.figure()
        result.groupby('nom_client')['total_frais_pliage'].mean().sort_values().plot(kind='bar')
        st.pyplot(plt)
        
        st.write("### Panier moyen vente total")
        plt.figure()
        st.pyplot(plt)
        
        st.write("### Total frais pliage")
        plt.figure()
        result.groupby('nom_client')['total_frais_pliage'].sum().sort_values(ascending=False).head(12).plot(kind='bar')
        st.pyplot(plt)
        
        st.bar_chart(df,x='epaisseur',y='qty_tole')
        
        fig = calplot(
         result.groupby('date_arrivé')["qty_tole"].sum().reset_index(),
         x="date_arrivé",
         y="qty_tole")
        st.plotly_chart(fig)
        
        fig = calplot(
         result.groupby('date_arrivé')["total_frais_pliage"].sum().reset_index(),
         x="date_arrivé",
         y="total_frais_pliage",
         colorscale='ylgn'
         )
        st.plotly_chart(fig)
        
    
    
    with tabs[3]:
        st.title("Administration")
        
        
        st.write("## Supprimé par facture")
        with st.form("administration"):
            num_facture = st.number_input("Numéro Facture",0,step=1)
            if st.form_submit_button("delete"):
                delete_row(num_facture)
                
        st.write("## Modifier données")
        df_edited = st.data_editor(df)
        if st.button("valider"):
            df_edited.to_sql('recap', conn, if_exists='replace', index=False)
            conn.close()
            st.toast("validated")
            st.success("validated")
            time.sleep(1)
            st.experimental_rerun()
        st.write("## Tout supprimé")
        if st.button(":red[Tout supprimé]"):
            delete_all()
            
    with tabs[4]:
        
        ## read data
        
        query = f"""select * from billetage"""
        df = pd.read_sql_query(query, conn)
        coef = [20_000,10_000,5_000,2_000,1_000,500,200,100]
        df["total"] = (df.iloc[:,1:]*coef).sum(axis=1)
        
        
        st.write("## Billetage")
        
        a = st.empty()
        
        col1,col2 = st.columns([0.3,0.7])
        
        with col1.form('billetage',clear_on_submit=True):
            date_billetage = st.date_input("Date de billetage")
            b20_000 = st.number_input("20 000",0,step=1)
            b10_000 = st.number_input("10 000",0,step=1)
            b5_000 = st.number_input("5 000",0,step=1)
            b2_000 = st.number_input("2 000",0,step=1)
            b1_000 = st.number_input("1 000",0,step=1)
            b500 = st.number_input("500",0,step=1)
            b200 = st.number_input("200",0,step=1)
            b100 = st.number_input("100",0,step=1)
            if st.form_submit_button():
                total_tresorerie = 20_000*b20_000 + 10_000*b10_000 + 5_000 * b5_000 + 2_000*b2_000 + 1_000 * b1_000 + 500*b500 + 200*b200 + 100 *b100
                sql = """
                               insert into billetage (date,b20_000,b10_000,b5_000,b2_000,b1_000,b_500,b_200,b_100) 
                               values(?,?,?,?,?,?,?,?,?)
                               """
                
                cursor.execute(sql,(date_billetage,b20_000,b10_000,b5_000,b2_000,b1_000,b500,b200,b100))
                conn.commit()
                a.info(f'**Référence:{cursor.lastrowid} du {date_billetage}: {total_tresorerie:,}ar**')
                st.toast(f'Référence:{cursor.lastrowid} du {date_billetage}: {total_tresorerie}ar')
        
        with col2:
            fig = px.line(df[["date",'total']].groupby('date').sum())
            st.plotly_chart(fig)
                         

    conn.close()
                
if __name__ == '__main__':
    main()


