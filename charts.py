import duckdb
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils import get_duckdb_conn

duckdb_conn = get_duckdb_conn()

# ------- agg query ----------

def get_agg_transactions(duckdb_conn):
    try:
        # Alternative approach: calculate datetime by adding hours to base timestamp
        agg_transactions = duckdb_conn.sql(f"""
            SELECT 
                datetime,
                type, 
                isFraud,
                count(distinct tx_sk) as dcount_tx,
                sum(amount) as sumAmount,
                mean(amount) as meanAmount,
                median(amount) as medianAmount                 
            FROM paysim
            group by all
        """).df()
        return agg_transactions
    except Exception as e:
        print(f"Error in get_agg_transactions: {e}")


# ------- scatter chart ----------

# Create scatter plot with fraud color coding
fig1 = px.scatter(
    get_agg_transactions(duckdb_conn),
    x="datetime",
    y="medianAmount", 
    color="isFraud",
    color_discrete_sequence=px.colors.qualitative.Alphabet,
    color_discrete_map={"0": 'blue', "1": 'red'},
    labels={
        "datetime": "Transaction Date/Time",
        "amount": "Median Transaction Amount",
        "isFraud": "Fraud Status"
    },
    title="Transaction Amounts Over Time (White = Fraud, Blue = Normal)",
    log_y=True
)

# ------- hourly query ----------

def get_agg_hourly(duckdb_conn):
    try:
        # Alternative approach: calculate datetime by adding hours to base timestamp
        agg_hourly = duckdb_conn.sql(f"""
            SELECT 
                date_part('hour', datetime) as dt_hour,
                type, 
                isFraud,
                count(distinct tx_sk) as dcount_tx,
                sum(amount) as sumAmount,
                mean(amount) as meanAmount,
                median(amount) as medianAmount                 
            FROM paysim
            group by all
        """).df()
        return agg_hourly
    except Exception as e:
        print(f"Error in get_agg_hourly: {e}")

# ------- hourly chart ----------

fig2 = px.bar(
    get_agg_hourly(duckdb_conn),
    x="dcount_tx",
    y="dt_hour", 
    color="isFraud",
    facet_col="type",
    color_discrete_sequence=px.colors.qualitative.Alphabet,
    color_discrete_map={"0": 'blue', "1": 'red'},
    labels={
        "dcount_tx": "Distinct Count Tx",
        "dt_hour": "Hour of Day",
        "isFraud": "Fraud Status"
    },
    title="Transactions by Hour of Day (Red = Fraud, Blue = Normal)",
    orientation='h',
    barmode='stack'
)


# ------- bad actors query ----------

def get_bad_actors(duckdb_conn):
    try:
        bad_actors = duckdb_conn.sql(f"""
            SELECT 
                nameOrig,
                nameDest,
                type, 
                isFraud,
                count(distinct tx_sk) as dcount_tx,
                sum(amount) as sumAmount,
                mean(amount) as meanAmount,
                median(amount) as medianAmount                 
            FROM paysim
            where isFraud = 1
            group by all
            order by 1 desc
        """).df()
        return bad_actors
    except Exception as e:
        print(f"Error in bad_actors: {e}")