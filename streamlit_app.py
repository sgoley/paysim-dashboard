import plotly.express as px
import streamlit as st
from numerize.numerize import numerize

from utils import get_duckdb_conn
from charts import figbar, figmedian, figmean

st.set_page_config(layout="wide")

def main():

    st.title("Analyzing PaySim Data")

    duckdb_conn = get_duckdb_conn()

    st.divider()

    st.subheader("High Level Metrics")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        num_trx = duckdb_conn.sql("select count(*) from paysim").fetchone()[0]
        st.metric(label="# Trx", value=numerize(num_trx))

    with col2:
        num_orig = duckdb_conn.sql("select count(distinct nameOrig) from paysim").fetchone()[0]
        st.metric(label="# Orig", value=numerize(num_orig))

    with col3:
        num_dest = duckdb_conn.sql("select count(distinct nameDest) from paysim").fetchone()[0]
        st.metric(label="# Dest", value=numerize(num_dest))

    with col4:
        num_fraud_trx = duckdb_conn.sql("select count(*) from paysim where isFraud = 1").fetchone()[0]
        st.metric(label="# Flagged Trx", value=numerize(num_fraud_trx))

    with col5:
        sum_fraud_amount = duckdb_conn.sql("select sum(amount) from paysim where isFraud = 1").fetchone()[0]
        st.metric(label="$ Flagged Trx", value=f"${numerize(sum_fraud_amount)}")
    
    with col6:
        num_fraud_dest = duckdb_conn.sql("select count(distinct nameDest) from paysim where isFraud = 1").fetchone()[0]
        st.metric(label="# Flagged Dest", value=numerize(num_fraud_dest))

    st.divider()

    st.plotly_chart(figbar, use_container_width=True)

    st.plotly_chart(figmedian, use_container_width=True)

    st.plotly_chart(figmean, use_container_width=True)

if __name__ == "__main__":
    main()