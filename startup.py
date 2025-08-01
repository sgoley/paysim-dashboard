#!/usr/bin/env python3
"""
Startup script for PaySim Streamlit app.
Downloads, extracts, and loads the PaySim dataset into DuckDB.
"""

import os
import zipfile
import requests
import duckdb
import streamlit as st
from pathlib import Path

DATA_DIR = Path("data")
ZIP_FILE = DATA_DIR / "paysim1.zip"
CSV_FILE = DATA_DIR / "PS_20174392719_1491204439457_log.csv"
DB_FILE = DATA_DIR / "paysim.duckdb"
DATASET_URL = "https://www.kaggle.com/api/v1/datasets/download/ealaxi/paysim1"

def download_dataset():
    """Download the PaySim dataset if not already present."""
    if ZIP_FILE.exists():
        print(f"Dataset already exists at {ZIP_FILE}")
        return
    
    print(f"Downloading dataset from {DATASET_URL}...")
    DATA_DIR.mkdir(exist_ok=True)
    
    response = requests.get(DATASET_URL, stream=True)
    response.raise_for_status()
    
    with open(ZIP_FILE, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    
    print(f"Dataset downloaded to {ZIP_FILE}")

def extract_dataset():
    """Extract the dataset if CSV doesn't exist."""
    if CSV_FILE.exists():
        print(f"CSV already exists at {CSV_FILE}")
        return
    
    if not ZIP_FILE.exists():
        raise FileNotFoundError(f"Zip file not found at {ZIP_FILE}")
    
    print(f"Extracting {ZIP_FILE}...")
    with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
        zip_ref.extractall(DATA_DIR)
    
    print(f"Dataset extracted to {DATA_DIR}")

def create_duckdb_table():
    """Create DuckDB instance and load CSV data into 'paysim' table."""
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV file not found at {CSV_FILE}")
    
    print(f"Creating DuckDB instance at {DB_FILE}...")
    conn = duckdb.connect(DB_FILE)
    
    # Create table from CSV
    conn.execute(f"""
        CREATE OR REPLACE TABLE paysim AS 
        SELECT * FROM read_csv_auto('{CSV_FILE}')
    """)

    # create datetime as first column
    conn.execute(f"""
        CREATE OR REPLACE TABLE paysim AS
        SELECT *
            , '{st.secrets.constants.datetime_base}'::TIMESTAMP + INTERVAL (step) HOUR as datetime
            , hash( datetime || Type || nameOrig || nameDest || amount ) as tx_sk
        FROM paysim
    """)
    
    # Get table info
    row_count = conn.execute("SELECT COUNT(*) FROM paysim").fetchone()[0]
    columns = conn.execute("DESCRIBE paysim").fetchall()
    head = conn.execute("select * from paysim limit 10").df()
    dupes = conn.execute("select tx_sk, count(*) from paysim group by 1 having count(*) > 1").fetchone()[0]
    
    print(f"Created 'paysim' table with {row_count:,} rows and {len(columns)} columns")
    print("Columns:", [col[0] for col in columns])
    print(head)
    print(dupes)
    
    conn.close()
    print(f"DuckDB database ready at {DB_FILE}")

def main():
    """Main startup routine."""
    try:
        print("Starting PaySim dataset setup...")
        download_dataset()
        extract_dataset()
        create_duckdb_table()
        print("Setup complete! DuckDB instance ready for Streamlit app.")
    except Exception as e:
        print(f"Error during setup: {e}")
        raise

if __name__ == "__main__":
    main()