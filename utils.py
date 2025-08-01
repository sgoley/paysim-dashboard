import duckdb
import streamlit as st

@st.cache_resource
def get_duckdb_conn():
    DUCKDB_EXTERNAL_LOCATION = st.secrets.constants.url
    duckdb_conn = duckdb.connect()
    duckdb_conn.execute(f"attach '{DUCKDB_EXTERNAL_LOCATION}' as ext_db")
    duckdb_conn.execute("use ext_db")
    # duckdb_conn = duckdb.connect("data/paysim.duckdb")
    return duckdb_conn
