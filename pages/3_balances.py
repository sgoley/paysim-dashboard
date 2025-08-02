import plotly.express as px
import streamlit as st

from utils import get_duckdb_conn
from charts import get_orig_balance_trust, get_dest_balance_trust, get_unequal_balances, create_trust_pie_chart

st.set_page_config(layout="wide")

def main():

    with st.sidebar:
        st.page_link('streamlit_app.py', label='Dashboard', icon='📊')
        st.page_link('pages/1_tx_profile.py', label='Tx Profiling', icon='🔍')
        st.page_link('pages/2_actors.py', label='Payment Network', icon='🛜')
        st.page_link('pages/3_balances.py', label='Balances', icon='⚖️')
        st.page_link('pages/4_waterfall.py', label='Waterfall', icon='🌊')

    duckdb_conn = get_duckdb_conn()

    st.title("⚖️ Balances")
    
    st.subheader("Balance Trust Analysis")
    
    # Create two columns for side-by-side pie charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Origin Balance Trust")
        orig_balance_trust = get_orig_balance_trust(duckdb_conn)
        if orig_balance_trust is not None:
            orig_pie = create_trust_pie_chart(
                orig_balance_trust, 
                "Origin Balance Trust Distribution",
                "trust_orig_balance"
            )
            if orig_pie:
                st.plotly_chart(orig_pie, use_container_width=True)
        else:
            st.error("Could not load origin balance trust data")
    
    with col2:
        st.subheader("Destination Balance Trust")
        dest_balance_trust = get_dest_balance_trust(duckdb_conn)
        if dest_balance_trust is not None:
            dest_pie = create_trust_pie_chart(
                dest_balance_trust,
                "Destination Balance Trust Distribution", 
                "trust_dest_balance"
            )
            if dest_pie:
                st.plotly_chart(dest_pie, use_container_width=True)
        else:
            st.error("Could not load destination balance trust data")

    st.divider()
    
    st.subheader("Fraudulent Transaction Details")
    unequal = get_unequal_balances(duckdb_conn)
    if unequal is not None:
        st.dataframe(unequal, use_container_width=True)
    else:
        st.error("Could not load fraudulent transaction data")

if __name__ == "__main__":
    main()