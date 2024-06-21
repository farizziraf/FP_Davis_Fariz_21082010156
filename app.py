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
        yaxis_title='Sales Amount (US$)',
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
        explanation1 = "Visualisasi ini menampilkan perbandingan jumlah karyawan (Employee Count) di setiap departemen. Jumlah karyawan dapat dilihat dari panjang batang pada grafik, di mana departemen dengan batang paling panjang memiliki jumlah karyawan terbanyak, sementara departemen dengan batang yang lebih pendek memiliki jumlah karyawan lebih sedikit. Analisis ini membantu dalam memahami distribusi tenaga kerja di berbagai departemen perusahaan. Terlihat bahwa jumlah karyawan terbanyak berada pada departemen Production, sedangkan jumlah karyawan paling sedikit berada pada departemen Executive. Jumlah karyawan yang besar di departemen Production berbanding lurus dengan fokus perusahaan yang bergerak di bidang produksi sepeda (Cycles). Sementara itu, departemen Executive adalah departemen dengan hierarki tertinggi di antara departemen lainnya, yang secara logis memiliki jumlah karyawan lebih sedikit karena semakin tinggi hierarki, jumlah karyawan cenderung semakin mengerucut atau sedikit."
        st.write("Penjelasan:")
        st.write(explanation1)
        if st.button("Text to Speech Comparison AW"):
            perform_tts(explanation1, "comparisonaw.mp3")

        st.markdown('<h3>Reseller Place by Region</h3>', unsafe_allow_html=True)
        st.write('Composition - Donut Chart Visualization')
        compositionaw(conn)
        explanation2 = "Visualisasi ini menampilkan proporsi jumlah reseller untuk setiap wilayah (Sales Territory Region). Setiap bagian pada grafik donat menunjukkan persentase jumlah reseller dalam wilayah tersebut terhadap total jumlah reseller di seluruh wilayah. Potongan donat yang lebih besar menunjukkan wilayah dengan lebih banyak reseller, sementara potongan donat yang lebih kecil menandakan wilayah dengan jumlah reseller yang lebih sedikit. Terlihat bahwa proporsi atau sebaran reseller di setiap wilayah tidak ada yang dominan atau condong pada satu wilayah saja. Proporsi reseller di setiap wilayah berkisar antara 5,71 persen hingga 18,7 persen. Hal ini menunjukkan distribusi yang relatif merata di antara berbagai wilayah."
        st.write("Penjelasan:")
        st.write(explanation2)
        if st.button("Text to Speech Composition AW"):
            perform_tts(explanation2, "compositionaw.mp3")

    with col2:
        st.markdown('<h3>Scatter Plot of Sales Amount by Product Category</h3>', unsafe_allow_html=True)
        st.write('Relationship - Scatter Plot Visualization')
        relationshipaw(conn)
        explanation3 = "Visualisasi ini menampilkan perbandingan jumlah penjualan (Sales Amount) untuk setiap kategori produk (Product Category). Sebaran data menunjukkan bagaimana penjualan terdistribusi di antara berbagai kategori produk, yang ditandai oleh ketebalan titik atau bulatan pada plot. Terlihat bahwa sebaran jumlah penjualan dari tiap kategori produk berbeda-beda. Pada kategori Bikes, sebaran jumlah penjualannya berada di kisaran 540 hingga 3578 USD. Pada kategori Clothing, sebaran jumlah penjualannya berada di kisaran 9 hingga 70 USD. Sedangkan pada kategori Accessories, sebaran jumlah penjualannya berada di kisaran 2 hingga 159 USD. Hal ini bisa terjadi karena perusahaan ini berfokus pada penjualan sepeda (Cycles), sehingga jumlah penjualan pada kategori produk Bikes lebih tinggi dibandingkan dengan kategori produk lainnya. Selain itu, kisaran harga Bikes lebih mahal daripada Clothing dan Accessories, yang juga mempengaruhi perbedaan jumlah penjualan di setiap kategori produk."
        st.write("Penjelasan:")
        st.write(explanation3)
        if st.button("Text to Speech Relationship AW"):
            perform_tts(explanation3, "relationshipaw.mp3")

        st.markdown('<h3>Order Quantity Distribution by Month</h3>', unsafe_allow_html=True)
        st.write('Distribution - Column Histogram Visualization')
        distributionaw(conn)
        explanation4 = "Visualisasi ini menampilkan distribusi jumlah pesanan (Order Quantity) berdasarkan bulan dari tahun 2001 hingga 2004. Setiap batang menunjukkan jumlah pesanan pada bulan tertentu, dengan sumbu x menunjukkan bulan dan sumbu y menunjukkan jumlah pesanan. Visualisasi ini membantu dalam melihat tren atau pola pesanan dari waktu ke waktu. Terlihat bahwa dari tahun 2001 hingga 2004, distribusi jumlah pesanan menunjukkan kestabilan selama dua tahun, dari Juli 2001 hingga Juni 2003. Kemudian, ada tren kenaikan yang signifikan mulai Juli 2003 dan seterusnya. Kenaikan jumlah pesanan yang drastis terlihat mulai dari bulan Juli 2003 hingga Juni 2004, di mana jumlah pesanan terus meningkat setiap bulannya."
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
        explanation5 = "Visualisasi ini menampilkan jumlah film untuk setiap label. Setiap batang menunjukkan jumlah film dalam kategori tertentu, dengan sumbu x menunjukkan label dan sumbu y menunjukkan jumlah film. Visualisasi ini membantu dalam memahami distribusi film berdasarkan labelnya. Terlihat bahwa dalam daftar 250 film terpopuler, jumlah film terbanyak ada pada label R, sementara jumlah film tersedikit ada pada label NC-17. Hal ini bisa terjadi karena film berlabel R memiliki banyak peminat atau sangat populer di kalangan masyarakat. Terdapat 101 film berlabel R yang masuk dalam daftar 250 film terpopuler disebabkan oleh batasan usia yang yang tidak terlalu ketat, dimana penonton dibawah 17 tahun masih bisa menonton tapi harus didampingi oleh orangtua atau yang lebih dewasa. Di sisi lain, hanya ada satu film berlabel NC-17 yang masuk dalam daftar tersebut. Ini mungkin disebabkan oleh batasan usia yang ketat, di mana penonton di bawah 17 tahun dilarang menonton film berlabel NC-17, sehingga sulit mendapatkan pasar yang luas."
        st.write("Penjelasan:")
        st.write(explanation5)
        if st.button("Text to Speech Comparison IMDB"):
            perform_tts(explanation5, "comparisonimdb.mp3")

        st.markdown('<h3>Proportion of Total Budget by Label</h3>', unsafe_allow_html=True)
        st.write('Composition - Donut Chart Visualization')
        compositionimdb(data)
        explanation6 = "Visualisasi ini menampilkan proporsi total anggaran film yang dialokasikan untuk setiap label. Setiap bagian atau potongan pada diagram donat menunjukkan persentase dari total anggaran film yang dikelompokkan berdasarkan labelnya. Terlihat bahwa proporsi total anggaran film yang dialokasikan untuk setiap label berbeda-beda, berkisar antara 0,0000102 persen hingga 36,2 persen. Proporsi anggaran yang besar diperuntukkan untuk pembuatan film dengan label PG-13 dan R, masing-masing sebesar 36,2 persen untuk label PG-13 dan 35,5 persen untuk label R. Hal ini disebabkan oleh tingginya minat pasar terhadap film dengan rating tersebut, sehingga banyak film dengan label PG-13 dan R dibuat dengan anggaran yang besar. Di sisi lain, sedikit anggaran untuk film dengan label Passed, NC-17, dan Approved, masing-masing hanya 0,0000102 persen untuk label Passed, 0,0459 persen untuk label NC-17, dan 0,373 persen untuk label Approved. Hal ini disebabkan oleh sedikitnya film dengan label tersebut yang masuk dalam daftar TOP 250 Movies terpopuler dan kurangnya pasar yang besar untuk jenis film ini."
        st.write("Penjelasan:")
        st.write(explanation6)
        if st.button("Text to Speech Composition IMDB"):
            perform_tts(explanation6, "compositionimdb.mp3")

    with col4:
        st.markdown('<h3>Scatter Plot of Release Year and Rating</h3>', unsafe_allow_html=True)
        st.write('Relationship - Scatter Plot Visualization')
        relationshipimdb(data)
        explanation7 = "Visualisasi ini menampilkan hubungan antara tahun rilis dan rating film. Setiap titik pada plot menunjukkan rating film pada tahun tertentu. Visualisasi ini membantu dalam memahami tren perubahan rating film seiring waktu dan trafik kepadatan di tiap jangka waktu. Terlihat bahwa trafik atau aktivitas terpadat terjadi pada film-film yang dirilis antara tahun 1990-an hingga 2010-an. Hal ini disebabkan oleh tingkat kepopuleran tinggi dari film-film yang dirilis dalam periode tersebut. Masyarakat kemungkinan besar akrab dengan atau pernah menonton film-film yang rilis pada tahun-tahun tersebut. Selain itu, pasar film global pada periode ini sangat luas dan diminati oleh banyak orang. Yang dimana industri film mengalami ledakan popularitas global dengan kemunculan film-film blockbuster yang memikat perhatian publik secara luas. Ini juga merupakan masa di mana teknologi digital dan internet mulai memengaruhi cara film diproduksi, didistribusikan, dan dikonsumsi oleh penonton di seluruh dunia."
        st.write("Penjelasan:")
        st.write(explanation7)
        if st.button("Text to Speech Relationship IMDB"):
            perform_tts(explanation7, "relationshipimdb.mp3")

        st.markdown('<h3>Film Ratings Distribution Histogram</h3>', unsafe_allow_html=True)
        st.write('Distribution - Line Histogram Visualization')
        distributionimdb(data)
        explanation8 = "Visualisasi ini menampilkan distribusi rating film dalam bentuk histogram garis. Sumbu x menunjukkan rating film, sementara sumbu y menunjukkan frekuensi kemunculan rating tersebut. Visualisasi ini membantu dalam memahami sebaran rating film secara keseluruhan dan menemukan tren atau pola dari rating film. Terlihat bahwa film-film yang masuk dalam TOP 250 Movies terpopuler memiliki rating antara 8 hingga 9,2. Rating yang paling banyak ditemui adalah 8,1, dengan jumlah 71 film. Untuk rating di atas 8,1, jumlah film secara bertahap menurun. Hal ini menunjukkan bahwa film-film dengan rating tinggi cenderung mendominasi dalam daftar TOP 250 Movies terpopuler. Namun, perlu dicatat bahwa rating film tidak selalu mencerminkan jumlah orang yang memberikan ulasan. Sebagai contoh, sebuah film dengan rating 8,5 mungkin hanya didasarkan pada sedikit ulasan yang memberikan nilai tinggi, sementara film dengan rating 7,5 bisa jadi memiliki lebih banyak ulasan yang memberikan skor lebih rendah. Oleh karena itu, rating tinggi tidak selalu menjamin bahwa film tersebut populer secara luas oleh masyarakat atau memiliki banyak penggemar."
        st.write("Penjelasan:")
        st.write(explanation8)
        if st.button("Text to Speech Distribution IMDB"):
            perform_tts(explanation8, "distributionimdb.mp3")

# Run the app
if __name__ == "__main__":
    main()
