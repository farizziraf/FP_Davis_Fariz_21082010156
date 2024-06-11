import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from gtts import gTTS
import mysql.connector
import os

# Database AW connection details from secrets
host = st.secrets.database.host
port = st.secrets.database.port
database = st.secrets.database.database
username = st.secrets['database']['username']
password = st.secrets.database.password

# Connect to the database
conn = mysql.connector.connect(
    host=host,
    port=port,
    database=database,
    user=username,
    password=password
)

# Load the data
data = pd.read_csv("dataset/imdbscrap.csv", sep=";")

# Comparison
def comparisonaw(conn):
    cursor = conn.cursor()
    query = """
        SELECT DepartmentName,
               COUNT(EmployeeKey) AS employee_count
        FROM dimemployee
        GROUP BY DepartmentName
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

    # Mengisi nilai yang hilang dengan 0
    df['employee_count'] = df['employee_count'].fillna(0)
    
    fig = px.bar(df, y='DepartmentName', x='employee_count', 
                 labels={'DepartmentName': 'Department Name', 'employee_count': 'Employee Count'}, 
                 color_discrete_sequence=['gold'])

    fig.update_layout(
        yaxis_title='Department Name',
        xaxis_title='Employee Count',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10),
        font=dict(color='white', size=14),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)'),
    )

    st.plotly_chart(fig)

# Relationship
def relationshipaw(conn):
    cursor = conn.cursor()
    query = """
        SELECT pc.EnglishProductCategoryName AS category, 
               fs.SalesAmount
        FROM factinternetsales fs
        JOIN dimproduct dp ON fs.ProductKey = dp.ProductKey
        JOIN dimproductsubcategory dps ON dp.ProductSubcategoryKey = dps.ProductSubcategoryKey
        JOIN dimproductcategory pc ON dps.ProductCategoryKey = pc.ProductCategoryKey;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

    # Create a scatter plot
    fig = px.scatter(df, x='category', y='SalesAmount', 
                     labels={'category': 'Product Category', 'SalesAmount': 'Sales Amount'},
                     color_discrete_sequence=['gold'],
                     opacity=0.75)

    fig.update_layout(
        xaxis_title='Product Category',
        yaxis_title='Sales Amount ($US)',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10),
        font=dict(color='white', size=14),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)', tickmode='array', tickvals=df['category'].unique()),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)'),
    )

    # Display the chart
    st.plotly_chart(fig)

# Composition
def compositionaw(conn):
    cursor = conn.cursor()
    query = """
        SELECT 
            st.SalesTerritoryRegion AS region,
            COUNT(r.ResellerKey) AS reseller_count
        FROM 
            dimreseller r
        JOIN 
            dimgeography g ON r.GeographyKey = g.GeographyKey
        JOIN 
            dimsalesterritory st ON g.SalesTerritoryKey = st.SalesTerritoryKey
        GROUP BY 
            st.SalesTerritoryRegion;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

    # Plotting the pie chart
    fig = px.pie(df, values='reseller_count', names='region',
                 hole=0.5,
                 color_discrete_sequence=['#ffd404', '#ffd718', '#ffdb2b', '#ffde3f', '#ffe152', '#ffe566', '#ffe87a', '#ffec8d', '#ffefa1', '#fff2b5'])

    fig.update_traces(textinfo='percent+label', pull=0.05)
    fig.update_layout(
        font=dict(color='white', size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    # Display the chart
    st.plotly_chart(fig)

# Distribution
def distributionaw(conn):
    cursor = conn.cursor()
    query = """
        SELECT
            dt.CalendarYear,
            dt.EnglishMonthName,
            SUM(fis.OrderQuantity) AS OrderQuantity
        FROM
            factinternetsales fis
        JOIN
            dimtime dt ON fis.OrderDateKey = dt.TimeKey
        WHERE
            dt.CalendarYear BETWEEN 2001 AND 2004
        GROUP BY
            dt.CalendarYear, dt.EnglishMonthName, dt.MonthNumberOfYear
        ORDER BY
            dt.CalendarYear, dt.MonthNumberOfYear;
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])

    # Create a new column to combine year and month
    df['YearMonth'] = df['CalendarYear'].astype(str) + ' ' + df['EnglishMonthName']

    # Plot the bar chart using Plotly
    fig = go.Figure(data=[go.Bar(
        x=df['YearMonth'], 
        y=df['OrderQuantity'],
        marker_color='gold'
    )])
    
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Order Quantity',
        xaxis=dict(
            tickangle=-45,
            tickmode='array',
            tickvals=df['YearMonth']
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10),
        font=dict(
            color='white',
            size=12,
            weight='bold'
        )
    )
    
    st.plotly_chart(fig)


# Comparison
def comparisonimdb(data):
    # Count the number of movies for each label
    count_by_label = data['label'].value_counts().reset_index()
    count_by_label.columns = ['label', 'count']

    # Set palette colors
    colors = ['#ffd404', '#ffd718', '#ffdb2b', '#ffde3f', '#ffe152', '#ffe566', '#ffe87a', '#ffec8d', '#ffefa1', '#fff2b5']

    # Create the bar chart using Plotly
    fig = px.bar(count_by_label, x='label', y='count', 
                 labels={'label': 'Label', 'count': 'Number of Movies'},
                 color='label', color_discrete_sequence=colors)

    fig.update_layout(
        xaxis=dict(title='Label', color='white', tickfont=dict(color='white')),
        yaxis=dict(title='Number of Movies', color='white', tickfont=dict(color='white')),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10),
        font=dict(color='white', size=12),
    )

    # Display the chart
    st.plotly_chart(fig)

# Relationship
def relationshipimdb(data):
    # Convert release_year to integer and rating to float
    data['release_year'] = data['release_year'].astype(int)
    data['rating'] = data['rating'] / 10.0

    # Create scatter plot
    fig = px.scatter(data, x='release_year', y='rating', 
                     labels={'release_year': 'Release Year', 'rating': 'Rating'},
                     color_discrete_sequence=['gold'],
                     opacity=0.5)

    fig.update_layout(
        xaxis_title='Release Year',
        yaxis_title='Rating',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10),
        font=dict(color='white', size=14),
        xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)'),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.2)'),
    )

    # Display the chart
    st.plotly_chart(fig)

# Composition
def compositionimdb(data):
    # Hitung total budget untuk setiap label
    total_budget_by_label = data.groupby('label')['budget'].sum()

    # Hitung total budget keseluruhan
    total_budget_all = data['budget'].sum()

    # Hitung proporsi untuk setiap label
    proportions = total_budget_by_label / total_budget_all

    # Urutkan proporsi dari yang terbesar ke yang terkecil
    proportions_sorted = proportions.sort_values(ascending=False)

    # Set palette colors
    colors = ['#ffd404', '#ffd718', '#ffdb2b', '#ffde3f', '#ffe152', '#ffe566', '#ffe87a', '#ffec8d']

    # Buat pie chart
    fig = go.Figure(data=[go.Pie(
        labels=proportions_sorted.index,
        values=proportions_sorted.values,
        hole=0.5,
        textinfo='percent+label',
        marker=dict(colors=colors),
    )])

    fig.update_layout(
        font=dict(color='white', size=12),
        margin=dict(t=10, b=10),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )

    # Tampilkan pie chart
    st.plotly_chart(fig)

# Distribution
def distributionimdb(data):
    # Hitung distribusi rating
    rating_distribution = data['rating'].value_counts().sort_index()

    # Buat line chart tanpa marker
    fig = go.Figure(data=go.Scatter(x=rating_distribution.index, y=rating_distribution.values, 
                                     mode='lines', line=dict(color='gold', width=2)))

    fig.update_layout(
        xaxis_title='Rating',
        yaxis_title='Frequency',
        xaxis=dict(color='white', gridcolor='rgba(255,255,255,0.2)', showgrid=True),
        yaxis=dict(color='white', gridcolor='rgba(255,255,255,0.2)', showgrid=True),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=10),
        font=dict(color='white', size=14),
    )

    # Tampilkan line chart
    st.plotly_chart(fig)


# Function to perform text-to-speech
def perform_tts(text, filename):
    # Periksa apakah file dengan nama yang sama sudah ada
    if os.path.exists(filename):
        os.remove(filename)  # Hapus file jika sudah ada

    # Buat ucapan dan simpan ke file
    tts = gTTS(text=text, lang='id')
    tts.save(filename)

    # Tampilkan audio
    st.audio(filename, format="audio/mp3")

# Main Streamlit app
def main():
    st.markdown("<h1 style='text-align: center; color: white;'>Adventure Works Dataset & IMDB Data Scrapping Visualization</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: white;'>By Fariz - 21082010156</h4>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: white;'>Adventure Works Dataset</h2>", unsafe_allow_html=True)

    # Add custom CSS to adjust column width
    st.markdown(
        """
        <style>
        .block-container {
            max-width: 100%;
            margin: auto;
        }
        .element-container {
            width: 100% !important;
        }
        .stColumn > div {
            padding: 1em;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # Divide the screen into 2 columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<h3>Employee Count per Department</h3>', unsafe_allow_html=True)
        st.write('Comparison - Column Chart Visualization')
        comparisonaw(conn)
        explanation1 = "Visualisasi ini menampilkan perbandingan jumlah karyawan (Employee Count) di setiap departemen. Jumlah karyawan dapat dilihat dari panjang batang pada grafik, dimana departemen dengan batang paling panjang memiliki jumlah karyawan terbanyak, sementara departemen dengan batang yang lebih pendek memiliki jumlah karyawan yang lebih sedikit. Analisis ini dapat membantu dalam memahami distribusi penyebaran tenaga kerja di berbagai departemen perusahaan."
        st.write("Penjelasan:")
        st.write(explanation1)
        if st.button("Text to Speech Comparison AW"):
            perform_tts(explanation1, "comparisonaw.mp3")

        st.markdown('<h3>Reseller Place by Region</h3>', unsafe_allow_html=True)
        st.write('Composition - Donut Chart Visualization')
        compositionaw(conn)
        explanation2 = "Visualisasi ini menampilkan proporsi jumlah reseller untuk setiap wilayah (Sales Territory Region). Setiap bagian donat menunjukkan persentase jumlah reseller dalam wilayah tersebut terhadap total jumlah reseller di seluruh wilayah. Donat yang lebih besar menunjukkan wilayah dengan lebih banyak reseller, sementara donat yang lebih kecil menandakan wilayah dengan jumlah reseller yang lebih sedikit."
        st.write("Penjelasan:")
        st.write(explanation2)
        if st.button("Text to Speech Composition AW"):
            perform_tts(explanation2, "compositionaw.mp3")

    with col2:
        st.markdown('<h3>Scatter Plot of Sales Amount by Product Category</h3>', unsafe_allow_html=True)
        st.write('Relationship - Scatter Plot Visualization')
        relationshipaw(conn)
        explanation3 = "Visualisasi ini menampilkan perbandingan jumlah penjualan (Sales Amount) untuk setiap kategori produk (Product Category). Sebaran data menunjukkan bagaimana distribusi penjualan terdistribusi di antara berbagai kategori produk, yang ditandai oleh ketebalan titik atau bulatan pada plot. Sebaran data yang lebih tebal menunjukkan jumlah penjualan yang lebih besar untuk kategori produk tersebut, sementara sebaran data yang lebih tipis menandakan jumlah penjualan yang lebih sedikit."
        st.write("Penjelasan:")
        st.write(explanation3)
        if st.button("Text to Speech Relationship AW"):
            perform_tts(explanation3, "relationshipaw.mp3")

        st.markdown('<h3>Order Quantity Distribution by Month</h3>', unsafe_allow_html=True)
        st.write('Distribution - Column Histogram Visualization')
        distributionaw(conn)
        explanation4 = "Visualisasi ini menampilkan distribusi jumlah pesanan (Order Quantity) berdasarkan bulan dari tahun 2001 hingga 2004. Setiap batang menunjukkan jumlah pesanan pada bulan tertentu, dengan sumbu x menunjukkan bulan dan sumbu y menunjukkan jumlah pesanan. Visualisasi ini membantu dalam melihat tren atau pola pesanan dari waktu ke waktu."
        st.write("Penjelasan:")
        st.write(explanation4)
        if st.button("Text to Speech Distribution AW"):
            perform_tts(explanation4, "distributionaw.mp3")

    st.markdown("<h2 style='text-align: center; color: white;'>IMDB Top 250 Movies By Popularity</h2>", unsafe_allow_html=True)

    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<h3>Number of Movies by Their Label</h3>', unsafe_allow_html=True)
        st.write('Comparison - Column Chart Visualization')
        comparisonimdb(data)
        explanation5 = "Visualisasi ini menampilkan jumlah film untuk setiap label. Setiap batang menunjukkan jumlah film dalam kategori tertentu, sementara sumbu x menunjukkan label dan sumbu y menunjukkan jumlah film. Visualisasi ini membantu dalam memahami distribusi film berdasarkan labelnya."
        st.write("Penjelasan:")
        st.write(explanation5)
        if st.button("Text to Speech Comparison IMDB"):
            perform_tts(explanation5, "comparisonimdb.mp3")

        st.markdown('<h3>Proportion of Total Budget by Label</h3>', unsafe_allow_html=True)
        st.write('Composition - Donut Chart Visualization')
        compositionimdb(data)
        explanation6 = "Visualisasi ini menampilkan proporsi total anggaran film yang dialokasikan untuk setiap label. Setiap bagian pada diagram lingkaran menunjukkan persentase dari total anggaran film yang dikelompokkan berdasarkan labelnya. Visualisasi ini membantu dalam memperkirakan jumlah anggaran film tergantung labelnya."
        st.write("Penjelasan:")
        st.write(explanation6)
        if st.button("Text to Speech Composition IMDB"):
            perform_tts(explanation6, "compositionimdb.mp3")

    with col4:
        st.markdown('<h3>Scatter Plot of Release Year and Rating</h3>', unsafe_allow_html=True)
        st.write('Relationship - Scatter Plot Visualization')
        relationshipimdb(data)
        explanation7 = "Visualisasi ini menampilkan hubungan antara tahun rilis dan rating film. Setiap titik pada plot menunjukkan rating film pada tahun tertentu. Visualisasi ini membantu dalam memahami tren perubahan rating film seiring waktu dan traffic kepadatan di tiap jangka waktunya."
        st.write("Penjelasan:")
        st.write(explanation7)
        if st.button("Text to Speech Relationship IMDB"):
            perform_tts(explanation7, "relationshipimdb.mp3")

        st.markdown('<h3>Film Ratings Distribution Histogram</h3>', unsafe_allow_html=True)
        st.write('Distribution - Line Histogram Visualization')
        distributionimdb(data)
        explanation8 = "Visualisasi ini menampilkan distribusi rating film dalam bentuk histogram garis. Sumbu x menunjukkan rating film, sementara sumbu y menunjukkan frekuensi kemunculan rating tersebut. Visualisasi ini membantu dalam memahami sebaran rating film secara keseluruhan dan menemukan tren atau pola dari rating film."
        st.write("Penjelasan:")
        st.write(explanation8)
        if st.button("Text to Speech Distribution IMDB"):
            perform_tts(explanation8, "distributionimdb.mp3")

# Run the app
if __name__ == "__main__":
    main()
