import plotly.express as px
import streamlit as st

from utils import get_duckdb_conn
from charts import figmedian, figmean, fighour, figsum

st.set_page_config(layout="wide")

def main():

    with st.sidebar:
        st.page_link('streamlit_app.py', label='Dashboard', icon='📊')
        st.page_link('pages/1_tx_profile.py', label='Tx Profiling', icon='🔍')
        st.page_link('pages/2_actors.py', label='Payment Network', icon='🛜')


    st.title("🔍 Tx Profiling")

    duckdb_conn = get_duckdb_conn()

    st.divider()

    st.subheader("Descriptive Analysis")

    st.plotly_chart(figmedian, use_container_width=True)

    st.divider()

    st.plotly_chart(figmean, use_container_width=True)

    st.divider()

    st.plotly_chart(fighour, use_container_width=True)

    st.divider()

    st.plotly_chart(figsum, use_container_width=True)

    st.divider()

if __name__ == "__main__":
    main()