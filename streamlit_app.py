import plotly.express as px
import streamlit as st
from numerize.numerize import numerize

from utils import get_duckdb_conn
from charts import figbar

st.set_page_config(layout="wide")

def main():
    # builds the sidebar menu
    with st.sidebar:
        st.page_link('streamlit_app.py', label='Dashboard', icon='📊')
        st.page_link('pages/1_tx_profile.py', label='Tx Profiling', icon='🔍')
        st.page_link('pages/2_actors.py', label='Payment Network', icon='🛜')


    st.title(f'📊 Dashboard')

    duckdb_conn = get_duckdb_conn()

    st.divider()

    st.subheader("High Level Metrics")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        num_trx = duckdb_conn.sql("select count(*) from paysim").fetchone()[0]
        st.metric(label="\# Trx", value=numerize(num_trx))

    with col2:
        num_trx = duckdb_conn.sql("select sum(amount) from paysim").fetchone()[0]
        st.metric(label="$ Trx", value=numerize(num_trx))

    with col3:
        num_orig = duckdb_conn.sql("select count(distinct nameOrig) from paysim").fetchone()[0]
        st.metric(label="\# Orig", value=numerize(num_orig))

    with col4:
        num_dest = duckdb_conn.sql("select count(distinct nameDest) from paysim").fetchone()[0]
        st.metric(label="\# Dest", value=numerize(num_dest))

    with col5:
        num_fraud_trx = duckdb_conn.sql("select count(*) from paysim where isFraud = 1").fetchone()[0]
        st.metric(label="\# Flagged Trx", value=numerize(num_fraud_trx))

    with col6:
        sum_fraud_amount = duckdb_conn.sql("select sum(amount) from paysim where isFraud = 1").fetchone()[0]
        st.metric(label="$ Flagged Trx", value=f"${numerize(sum_fraud_amount)}")

    st.divider()

    st.plotly_chart(figbar, use_container_width=True)

    st.divider()

    st.subheader("Latest 100 transactions")

    top100 = duckdb_conn.sql("select * from paysim order by datetime desc limit 100").df()
    top100
    
if __name__ == "__main__":
    main()