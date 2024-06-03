import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.express as px
import translators as ts
from gtts import gTTS
from sqlalchemy import create_engine
import os

st.write("Adventure Works Dataset & IMDB Data Scrapping Visualization")
st.write("By Fariz - 21082010156")

# Database AW connection details from secrets
# dialect = st.secrets["connections.mydb"]["dialect"]
# driver = st.secrets["connections.mydb"]["driver"]
host = st.secrets["connections.mydb"]["host"]
port = st.secrets["connections.mydb"]["port"]
database = st.secrets["connections.mydb"]["database"]
username = st.secrets["connections.mydb"]["username"]
password = st.secrets["connections.mydb"]["password"]

# Connect to the database
connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
# connection_string = f"{dialect}+{driver}://{username}:{password}@{host}:{port}/{database}"
engine = create_engine(connection_string)

# Query the database
st.write("Data from Database")
try:
    df = pd.read_sql('SELECT EnglishPromotionName, StartDate, EndDate, MaxQty FROM dimpromotion LIMIT 10;', engine)
    st.table(df)
except Exception as e:
    st.write(f"Error connecting to the database: {e}")

# Load the data
data = pd.read_csv("dataset/imdbscrap.csv")

st.write("Adventure Works Dataset")
#Comparison
def create_column_chart_from_database(engine):
    query = """
        SELECT sm.name AS shipping_method,
        COUNT(sf.shippingMethod_key) AS usage_count
        FROM sales_fact sf
        JOIN shipping_method sm ON sf.shippingMethod_key = sm.id
        GROUP BY sm.name
    """
    df = pd.read_sql(query, engine)

    plt.figure(figsize=(10, 6))
    plt.bar(df['shipping_method'], df['usage_count'], color='skyblue')
    plt.xlabel('Shipping Method')
    plt.ylabel('Usage Count')
    plt.title('Usage Count of Shipping Methods')
    plt.xticks(rotation=45)
    st.pyplot()
#Relationship
#Composition
#Distribution

st.write("IMDB Top 250 Movies By Popularity")
#Comparison
#Relationship
#Composition
#Distribution


# Function to perform text-to-speech and translation
def perform_tts_and_translation(text, target_language):
    # Translation
    st.write("Terjemahan dalam bahasa target:")
    hasil = ts.translate_text(text, to_language=target_language, translator='google')
    st.write(hasil)
    
    # Text-to-speech for translated text
    tts_translated = gTTS(text=hasil, lang=target_language)
    tts_translated.save("translated.mp3")
    st.audio("translated.mp3", format="audio/mp3")

# Main Streamlit app
def main():
    st.title("Text-to-Speech and Translation App")
    
    # Input text
    text = st.text_area("Masukkan teks yang ingin diucapkan dan diterjemahkan", 
                        "This company was founded in 2010 by the infamous movie star, Graeme Alexander. Currently, the company worths USD 1 billion according to Forbes report in 2023. What an achievement in just 13 years.")
    
    # Target language selection
    target_language = st.selectbox("Pilih bahasa target untuk menerjemahkan", 
                                   ["id", "fr", "es", "zh-CN"])
    
    # Button to perform TTS and translation
    if st.button("Proses"):
        perform_tts_and_translation(text, target_language)

# Run the app
if __name__ == "__main__":
    main()