import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import translators as ts
from gtts import gTTS
from sqlalchemy import create_engine
import mplcursors
import os

# Database AW connection details from secrets
host = st.secrets.database.host
port = st.secrets.database.port
database = st.secrets.database.database
username = st.secrets.database.username
password = st.secrets.database.password

# Connect to the database
connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string)

# Load the data
data = pd.read_csv("dataset/imdbscrap.csv", sep=";")

# Comparison
def comparisonaw(engine):
    query = """
        SELECT sm.name AS shipping_method,
        COUNT(sf.shippingMethod_key) AS usage_count
        FROM sales_fact sf
        JOIN shipping_method sm ON sf.shippingMethod_key = sm.id
        GROUP BY sm.name
    """
    df = pd.read_sql(query, engine)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(df['shipping_method'], df['usage_count'], color='gold', zorder=2)
    ax.set_xlabel('Shipping Method', color='white', fontweight='bold', labelpad=20)
    ax.set_ylabel('Usage Count', color='white', fontweight='bold', labelpad=20)
    plt.xticks(color='white', fontweight='bold')
    plt.yticks(color='white', fontweight='bold')

    # Set the color of lines around the plot area to white
    ax.spines['top'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')

    # Set the color of grid lines to white
    ax.yaxis.grid(True, color='white', alpha=0.5)
    ax.xaxis.grid(True, color='white', alpha=0.5)

    # Set the background frame to be transparent
    ax.set_facecolor('none')
    fig.patch.set_facecolor('none')

    st.pyplot(fig)

# Relationship
def relationshipaw(engine):
    # Query the data from the database
    query = """
        SELECT OrderQty, LineTotal
        FROM sales_fact;
    """
    df = pd.read_sql(query, engine)

    # Create a scatter plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['OrderQty'], df['LineTotal'], color='gold', alpha=0.25, zorder=2)
    ax.set_xlabel('Order Quantity', color='white', fontweight='bold', labelpad=20)
    ax.set_ylabel('Line Total', color='white', fontweight='bold', labelpad=20)
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontweight('bold')

    # Set the color of grid lines to white
    ax.grid(True, color='white', alpha=0.5)

    # Set the color of lines around the plot area to white
    ax.spines['top'].set_color('white')
    ax.spines['bottom'].set_color('white')
    ax.spines['left'].set_color('white')
    ax.spines['right'].set_color('white')

    # Set the background frame to be transparent
    ax.set_facecolor('none')
    fig.patch.set_facecolor('none')
    
    st.pyplot(fig)

# Composition
def compositionaw(engine):
    # Query the data from the database
    query = """
        SELECT 
            c.territory,
            COUNT(sf.customer_key) AS jumlah_pembelian,
            CONCAT(FORMAT(COUNT(sf.customer_key)/ total_pembelian.total * 100, 2), '%%') AS persentase_pembelian
        FROM 
            sales_fact sf
        JOIN 
            customer c ON sf.customer_key = c.id
        CROSS JOIN 
            (SELECT COUNT(*) AS total FROM sales_fact) AS total_pembelian
        GROUP BY 
            c.territory;
    """
    df = pd.read_sql(query, engine)

    # Set palette colors
    colors = ['#ffd404', '#ffd718', '#ffdb2b', '#ffde3f', '#ffe152', '#ffe566', '#ffe87a', '#ffec8d', '#ffefa1', '#fff2b5']

    # Plotting the donut chart
    fig, ax = plt.subplots(figsize=(8, 8))
    pie = ax.pie(df['jumlah_pembelian'], labels=df['territory'], autopct='%1.1f%%', startangle=90, pctdistance=0.85, colors=colors, textprops={'fontweight': 'bold'})
    
    # Draw a circle at the center of pie to make it a donut chart
    centre_circle = plt.Circle((0, 0), 0.5, fc='#101414')
    fig.gca().add_artist(centre_circle)
    
    # Set text color
    for text in pie[1]:
        text.set_color('#101414' if centre_circle.contains_point(text.get_position()) else 'white')
    
    # Equal aspect ratio ensures that pie is drawn as a circle
    ax.axis('equal')

    # Set the background frame to be transparent
    ax.set_facecolor('none')
    fig.patch.set_facecolor('none')

    st.pyplot(fig)

# Distribution
def distributionaw(engine):
    # Query the data from the database
    query = """
        SELECT
            FLOOR(StockedQty / 100) * 100 AS bin_start,
            FLOOR(StockedQty / 100) * 100 + 100 AS bin_end,
            SUM(StockedQty) AS bin_sum
        FROM
            production_fact
        GROUP BY
            FLOOR(StockedQty / 100)
        ORDER BY
            bin_start;
    """
    df = pd.read_sql(query, engine)

    # Create interval labels
    df['interval'] = df.apply(lambda row: f"{int(row['bin_start'])}-{int(row['bin_end'])}", axis=1)
    
    # Plot the histogram using Plotly
    fig = go.Figure(data=[go.Bar(
        x=df['interval'], 
        y=df['bin_sum'],
        marker_color='gold'
    )])
    
    fig.update_layout(
        xaxis_title='Stocked Quantity Interval',
        yaxis_title='Total Quantity',
        xaxis=dict(
            rangeslider=dict(
                visible=True
            ),
            tickangle=-45
        ),
        plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
        paper_bgcolor='rgba(0,0,0,0)'  # Transparent background
    )
    
    st.plotly_chart(fig)


# Comparison
# Relationship
# Composition
# Distribution


# Function to perform text-to-speech and translation
# def perform_tts_and_translation(text, target_language):
#     st.write("Terjemahan dalam bahasa target:")
#     hasil = ts.translate_text(text, to_language=target_language, translator='google')
#     st.write(hasil)
    
#     tts_translated = gTTS(text=hasil, lang=target_language)
#     tts_translated.save("translated.mp3")
#     st.audio("translated.mp3", format="audio/mp3")

# Main Streamlit app
def main():
    st.write("Adventure Works Dataset & IMDB Data Scrapping Visualization")
    st.write("By Fariz - 21082010156")
    st.write("Adventure Works Dataset")

    st.title('Usage Count of Shipping Methods')
    st.write('Comparison - Column Chart Visualization')
    comparisonaw(engine)

    st.title('Scatter Plot of Order Quantity and Line Total')
    st.write('Relationship - Scatter Plot Visualization')
    relationshipaw(engine)

    st.title('Purchase Proportions by Region')
    st.write('Composition - Donut Chart Visualization')
    compositionaw(engine)

    st.title('Stocked Quantity Distribution')
    st.write('Distribution - Column Histogram Visualization')
    distributionaw(engine)

    st.write("IMDB Top 250 Movies By Popularity")

    
    # text = st.text_area("Masukkan teks yang ingin diucapkan dan diterjemahkan", 
    #                     "This company was founded in 2010 by the infamous movie star, Graeme Alexander. Currently, the company worths USD 1 billion according to Forbes report in 2023. What an achievement in just 13 years.")
    
    # target_language = st.selectbox("Pilih bahasa target untuk menerjemahkan", 
    #                                ["id", "fr", "es", "zh-CN"])
    
    # if st.button("Proses"):
    #     perform_tts_and_translation(text, target_language)

# Run the app
if __name__ == "__main__":
    main()
