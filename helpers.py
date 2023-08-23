import sqlite3 as sq
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt


database_name = "plitech_database.db"




def connect(database_name):
    return sq.connect(database_name,check_same_thread=False)


conn = connect(database_name)
def table_to_df(table_name):
    query = f"""select * from {table_name}"""
    df = pd.read_sql_query(query, conn)
    return df

def data_preprocessing(df:pd.DataFrame) ->pd.DataFrame:
    
    df['qty_tole'] = df["qty"] * df['longueur'] * df['largeur']/2_000_000
    df['ca'] = df['total_vente_tole'] + df['total_frais_pliage']
    
    return df

def plot_by_month(result,name="total_frais_pliage"):
    result.reset_index(inplace = True)
    result['date_arrivé'] = pd.to_datetime(result['date_arrivé'])

    # Step 2: Extract the month and year from 'date_arrivé'
    result['month_year'] = result['date_arrivé'].dt.to_period('M')

    # Step 3: Group the data by month and year, and calculate the sum of 'total_frais_pliage'
    grouped_data = result.groupby('month_year')[name].sum()

    # Create a Streamlit app
    st.title(f'{name}')
    st.write(f'This app displays the {name} by month and year.')

    # Show the data table (optional)

    # Plot the data using matplotlib and display it in Streamlit
    plt.figure(figsize=(10, 6))
    plt.bar(grouped_data.index.astype(str), grouped_data.values)
    plt.xlabel('Month-Year')
    plt.ylabel(f'{name}')
    plt.title(f'{name} by Month-Year')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    # Show the plot using Streamlit
    st.pyplot(plt)
