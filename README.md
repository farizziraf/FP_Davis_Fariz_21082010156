# Data Visualization: AdventureWork Dataset and IMDB Top 250 Movies Data Scraping using Python

## Table of Contents
- [Introduction](#introduction)
  - [Personal Introduction](#personal-introduction)
  - [Project Introduction](#project-introduction)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup](#setup)
  - [Clone Repository](#clone-repository)
  - [Import Database](#import-database)
  - [.streamlit/secret.toml](#secretsecretstoml)
  - [Usage](#usage)
- [Datasets](#datasets)
- [Streamlit Dashboard](#streamlit-dashboard)
- [Author](#author)

## Introduction

### Personal Introduction
Hello, my name is Fariz with NPM: 21082010156. This project is part of my Tugas Besar (major assignment) for the Data Visualization course, Par B. Through this project, I aim to demonstrate my skills in data handling, scraping, and visualization using Python.

### Project Introduction
This project focuses on data visualization using Python. It involves two main tasks:
1. Visualizing the AdventureWork dataset.
2. Scraping and visualizing data from the IMDB Top 250 movies list.

## Project Structure
The project structure is as follows:
```bash
.
├── .streamlit (.gitignore)
│   ├── secrets.toml (.gitignore)
├── dataset
│   ├── aw.sql
│   ├── imdbscrap.csv
├── app.py
├── requirements.txt
└── README.md
```

## Requirements
- Python
- Mysql (XAMPP)
- Streamlit
- Pandas
- Plotly
- Gtts
- Mysql-connector-python

## Setup

### Clone Repository
1. Clone the repository:
    ```sh
    git clone https://github.com/farizziraf/FP_Davis_Fariz_21082010156.git
    ```

2. Change to the project directory:
    ```sh
    cd FP_Davis_Fariz_21082010156
    ```

### Import Database
1. Install XAMPP and start MySQL server.
2. Import the AdventureWork database file 'aw.sql'.

### .secret/secrets.toml
1. Create a `.secret` directory in the root of the project:
    ```sh
    mkdir .secret
    ```

2. Create a `secrets.toml` file inside the `.secret` directory:
    ```sh
    touch .secret/secrets.toml
    ```

3. Add your secret configurations to the `secrets.toml` file.
    Example:
    ```toml
    [database]
    host = "your_host"
    port = "your_port"
    database = "your_database"
    username = "your_username"
    password = "your_password"
    ```

### Usage
1. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

2. Run the project:
    ```sh
    streamlit run app.py
    ```

## Datasets
- **AdventureWork Dataset:** This dataset contains fictional business data for a bike manufacturing company.
- **IMDB Top 250 Movies:** This dataset contains data scraped from the [IMDB website](https://www.imdb.com/chart/top/?sort=popularity%2Casc), listing the top 250 movies.

## Streamlit Dashboard
The Streamlit dashboard contains visualizations of both the AdventureWork dataset and the IMDB Top 250 Movies data. Each dataset has visualization segments including:
- Comparison
- Relationship
- Composition
- Distribution

Each segment includes explanations related to the visualizations, along with a text-to-speech feature that reads out the explanations.

You can view the Streamlit dashboard for this project at the following link:
[Streamlit Dashboard](https://fp-davis-fariz-21082010156.streamlit.app/)

## Author
Nama: Fariz<br>
NPM: 21082010156<br>
Tugas Besar Data Visualisasi Par B