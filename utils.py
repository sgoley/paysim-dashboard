import duckdb
import streamlit as st

@st.cache_resource
def get_duckdb_conn():
    duckdb_conn = duckdb.connect("data/paysim.duckdb")
    return duckdb_conn
