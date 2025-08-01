import duckdb
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from utils import get_duckdb_conn

duckdb_conn = get_duckdb_conn()

# ------- scatter query ----------

def get_agg_transactions(duckdb_conn):
    try:
        # Alternative approach: calculate datetime by adding hours to base timestamp
        agg_transactions = duckdb_conn.sql(f"""
            SELECT 
                cast(datetime as date) as datetime,
                type, 
                isFraud,
                count(distinct tx_sk) as dcount_tx,
                sum(amount) as sumAmount,
                mean(amount) as meanAmount,
                median(amount) as medianAmount                 
            FROM paysim
            group by all
            order by 1
        """).df()
        return agg_transactions
    except Exception as e:
        print(f"Error in get_agg_transactions: {e}")

# ------- bar chart ----------

figbar = px.bar(
    get_agg_transactions(duckdb_conn).sort_values('isFraud', ascending=False),
    x="datetime",
    y="dcount_tx", 
    color="isFraud",
    # color_discrete_sequence=px.colors.qualitative.Alphabet,
    color_discrete_map={"0": 'blue', "1": 'red'},
    labels={
        "datetime": "Transaction Date/Time",
        "dcount_tx": "Count of Tx",
        "isFraud": "Fraud Status"
    },
    title="Transaction Counts Over Time",
    log_y=True
)

# ------- median scatter chart ----------

# Create scatter plot with fraud color coding
figmedian = px.scatter(
    get_agg_transactions(duckdb_conn).sort_values('type', ascending=True),
    x="datetime",
    y="medianAmount", 
    color="isFraud",
    color_discrete_sequence=px.colors.qualitative.Alphabet,
    color_discrete_map={"0": 'blue', "1": 'red'},
    labels={
        "datetime": "Transaction Date/Time",
        "amount": "Median Transaction Amount",
        "isFraud": "Fraud Status",
        "type": "Tx Type"
    },
    title="Transaction Amounts Over Time (median)",
    facet_col="type",
    log_y=True
)

# ------- mean scatter chart ----------

# Create scatter plot with fraud color coding
figmean = px.scatter(
    get_agg_transactions(duckdb_conn).sort_values('type', ascending=True),
    x="datetime",
    y="meanAmount", 
    color="isFraud",
    color_discrete_sequence=px.colors.qualitative.Alphabet,
    color_discrete_map={"0": 'blue', "1": 'red'},
    labels={
        "datetime": "Transaction Date/Time",
        "amount": "Mean Transaction Amount",
        "isFraud": "Fraud Status",
        "type": "Tx Type"
    },
    title="Transaction Amounts Over Time (mean)",
    facet_col="type",
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

fighour = px.bar(
    get_agg_hourly(duckdb_conn).sort_values('isFraud'),
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

def get_fraud_victims(duckdb_conn):
    try:
        fraud_victims = duckdb_conn.sql("""
            SELECT 
                nameDest as name,
                count(*)
            FROM paysim
            WHERE isFraud = 1
            GROUP BY 1
            HAVING count(*) >= 1
            ORDER BY name
        """).df()
        return fraud_victims
    except Exception as e:
        print(f"Error in get_fraud_victims: {e}")
        return None