import duckdb
import streamlit as st
import os

@st.cache_resource
def get_duckdb_conn():
    local_db_path = "data/paysim.duckdb"
    
    if os.path.exists(local_db_path):
        duckdb_conn = duckdb.connect(local_db_path)
    else:
        DUCKDB_EXTERNAL_LOCATION = st.secrets.constants.url
        duckdb_conn = duckdb.connect()
        duckdb_conn.execute(f"attach '{DUCKDB_EXTERNAL_LOCATION}' as ext_db")
        duckdb_conn.execute("use ext_db")
    
    return duckdb_conn
