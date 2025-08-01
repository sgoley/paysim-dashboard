import plotly.express as px
import streamlit as st

from utils import get_duckdb_conn
from charts import fighour

st.set_page_config(layout="wide")

def main():

    st.title("Analyzing PaySim Data")

    duckdb_conn = get_duckdb_conn()

    st.divider()

    st.subheader("Descriptive Analysis")
        
    st.plotly_chart(fighour, use_container_width=True)

    st.divider()

if __name__ == "__main__":
    main()