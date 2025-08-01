import plotly.express as px
import streamlit as st

from utils import get_duckdb_conn
from charts import fig1, fig2

st.set_page_config(layout="wide")

def main():

    st.title("Analyzing PaySim Data")

    duckdb_conn = get_duckdb_conn()

    st.divider()

    st.subheader("High Level Metrics")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(label="# Trx", value=duckdb_conn.sql("select count(*) from paysim").fetchone()[0])

    with col2: 
        st.metric(label="# Flagged Trx", value=duckdb_conn.sql("select count(*) from paysim where isFraud = 1").fetchone()[0])

    with col3: 
        st.metric(label="# Orig", value=duckdb_conn.sql("select count(distinct nameOrig) from paysim").fetchone()[0])

    with col4: 
        st.metric(label="# Dest", value=duckdb_conn.sql("select count(distinct nameDest) from paysim").fetchone()[0])

    st.divider()

    st.subheader("Descriptive Analysis")
    
    st.plotly_chart(fig1, use_container_width=True)

    st.divider()
    
    st.plotly_chart(fig2, use_container_width=True)

if __name__ == "__main__":
    main()