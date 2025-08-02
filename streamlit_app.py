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
        st.page_link('pages/3_balances.py', label='Balances', icon='⚖️')

        st.divider()

        preview_select = st.selectbox('Table Preview', ['Top 100', 'Latest 100', '20 Each Type', '100 Fraud'])


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

    st.subheader("Transaction Preview")

    # Execute different queries based on selectbox selection
    if preview_select == 'Top 100':
        preview_df = duckdb_conn.sql("""
            SELECT * FROM paysim 
            ORDER BY ABS(amount) DESC 
            LIMIT 100
        """).df()
    elif preview_select == 'Latest 100':
        preview_df = duckdb_conn.sql("""
            SELECT * FROM paysim 
            ORDER BY datetime DESC 
            LIMIT 100
        """).df()
    elif preview_select == '20 Each Type':
        preview_df = duckdb_conn.sql("""
            SELECT * FROM (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY type ORDER BY RANDOM()) as rn
                FROM paysim
            ) t
            WHERE rn <= 20
            ORDER BY type, rn
        """).df()
    elif preview_select == '100 Fraud':
        preview_df = duckdb_conn.sql("""
            SELECT * FROM (
                SELECT *, ROW_NUMBER() OVER (PARTITION BY type ORDER BY RANDOM()) as rn
                FROM paysim
            ) t
            WHERE isFraud = 1
            ORDER BY type, rn
        """).df()
    else:
        preview_df = duckdb_conn.sql("SELECT * FROM paysim LIMIT 100").df()
    
    st.dataframe(preview_df, use_container_width=True)
    
if __name__ == "__main__":
    main()