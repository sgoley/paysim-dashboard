import plotly.express as px
import streamlit as st

from utils import get_duckdb_conn
from charts import get_unequal_balances

st.set_page_config(layout="wide")

def main():

    with st.sidebar:
        st.page_link('streamlit_app.py', label='Dashboard', icon='📊')
        st.page_link('pages/1_tx_profile.py', label='Tx Profiling', icon='🔍')
        st.page_link('pages/2_actors.py', label='Payment Network', icon='🛜')
        st.page_link('pages/3_balances.py', label='Balances', icon='⚖️')

    duckdb_conn = get_duckdb_conn()

    st.title("⚖️ Balances")

    unequal = get_unequal_balances(duckdb_conn)
    unequal

if __name__ == "__main__":
    main()