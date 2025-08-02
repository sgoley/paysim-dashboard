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
                CASE WHEN isFraud = 1 THEN 'Fraud' ELSE 'Normal' END as isFraud,
                count(distinct tx_sk) as dcount_tx,
                sum(abs_amount) as sumAmount,
                mean(abs_amount) as meanAmount,
                median(abs_amount) as medianAmount                 
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
    color_discrete_map={'Normal': '#5848d5', 'Fraud': '#f77088'}, 
    barmode='group',
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
    color_discrete_map={'Normal': '#5848d5', 'Fraud': '#f77088'},
    labels={
        "datetime": "Transaction Date/Time",
        "amount": "Median Transaction Amount",
        "isFraud": "Fraud Status",
        "type": "Tx Type"
    },
    title="Transaction Counts Over Time (median)",
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
    color_discrete_map={'Normal': '#5848d5', 'Fraud': '#f77088'},
    labels={
        "datetime": "Transaction Date/Time",
        "amount": "Mean Transaction Amount",
        "isFraud": "Fraud Status",
        "type": "Tx Type"
    },
    title="Transaction $ Amounts Over Time (mean)",
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
                CASE WHEN isFraud = 1 THEN 'Fraud' ELSE 'Normal' END as isFraud,
                count(distinct tx_sk) as dcount_tx,
                sum(abs_amount) as sumAmount,
                mean(abs_amount) as meanAmount,
                median(abs_amount) as medianAmount                 
            FROM paysim
            group by all
        """).df()
        return agg_hourly
    except Exception as e:
        print(f"Error in get_agg_hourly: {e}")

# ------- hourly chart ----------

fighour = px.bar(
    get_agg_hourly(duckdb_conn).sort_values('type', ascending=True),
    x="dcount_tx",
    y="dt_hour", 
    color="isFraud",
    facet_col="type",
    color_discrete_map={'Normal': '#5848d5', 'Fraud': '#f77088'},
    labels={
        "dcount_tx": "Distinct Count Tx",
        "dt_hour": "Hour of Day",
        "isFraud": "Fraud Status"
    },
    title="Transactions Counts by Hour of Day",
    orientation='h',
    log_x=True,
    barmode='stack'
)

# ------- hourly sum chart ----------

figsum = px.bar(
    get_agg_hourly(duckdb_conn).sort_values('type', ascending=True),
    x="sumAmount",
    y="dt_hour", 
    color="isFraud",
    facet_col="type",
    color_discrete_map={'Normal': '#5848d5', 'Fraud': '#f77088'},
    labels={
        "sumAmount": "Sum Tx $",
        "dt_hour": "Hour of Day",
        "isFraud": "Fraud Status"
    },
    title="Transactions $ Amounts by Hour of Day",
    orientation='h',
    log_x=True,
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

# ------- balances query ----------

def get_unequal_balances(duckdb_conn):
    try:
        unequal_balances = duckdb_conn.sql("""
            SELECT 
                datetime,
                tx_sk,
                type,
                amount,
                abs_amount,

                nameOrig,
                post_balance_orig,
                amount_orig,

                nameDest,
                amount_dest,
                post_balance_dest                
            FROM paysim
            where isFraud = 1
            order by abs_amount desc, datetime asc
        """).df()
        return unequal_balances
    except Exception as e:
        print(f"Error in get_unequal_balances: {e}")
        return None

# ------- trusted balances query ----------

def get_orig_balance_trust(duckdb_conn):
    try:
        orig_balance_trust = duckdb_conn.sql("""
            SELECT 
                trust_orig_balance,
                COUNT(*) as count
            FROM paysim
            GROUP BY trust_orig_balance
        """).df()
        return orig_balance_trust
    except Exception as e:
        print(f"Error in get_orig_balance_trust: {e}")
        return None

def get_dest_balance_trust(duckdb_conn):
    try:
        dest_balance_trust = duckdb_conn.sql("""
            SELECT 
                trust_dest_balance,
                COUNT(*) as count
            FROM paysim
            GROUP BY trust_dest_balance
        """).df()
        return dest_balance_trust
    except Exception as e:
        print(f"Error in get_dest_balance_trust: {e}")
        return None

def create_trust_pie_chart(trust_data, title, trust_column):
    """Create a pie chart showing trust vs untrust proportions"""
    if trust_data is not None and not trust_data.empty:
        # Calculate percentages
        total = trust_data['count'].sum()
        trust_data['percentage'] = (trust_data['count'] / total * 100).round(1)
        
        # Create labels with percentages
        labels = []
        values = []
        colors = []
        
        for _, row in trust_data.iterrows():
            if row[trust_column]:
                labels.append(f"Trusted ({row['percentage']}%)")
                colors.append('#05dde3')  # Light blue for trusted
            else:
                labels.append(f"Untrusted ({row['percentage']}%)")
                colors.append('#f77088')  # Red for untrusted
            values.append(row['count'])
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            textinfo='label+percent',
            textposition='auto'
        )])
        
        fig.update_layout(
            title=title,
            showlegend=True,
            height=400
        )
        
        return fig
    return None