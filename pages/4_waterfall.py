import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from utils import get_duckdb_conn
from charts import get_fraud_victims

def main():
    # Custom CSS to fix selectbox styling
    st.markdown("""
    <style>
    .stSelectbox div[data-baseweb="select"] > div:first-child {
        background-color: #ffffff !important;
        border-color: #5848d5 !important;
    }
    
    /* Target the dropdown container */
    div[role="listbox"] {
        background-color: #ffffff !important;
    }
    
    div[role="listbox"] ul {
        background-color: #ffffff !important;
    }
    
    /* Target all dropdown list items */
    div[role="listbox"] li {
        background-color: #ffffff !important;
    }
    
    /* Target dropdown options with more specific selectors */
    div[data-baseweb="menu"] div[role="option"] {
        background-color: #ffffff !important;
    }
    
    div[data-baseweb="menu"] div[role="option"]:hover {
        background-color: #f8f9fa !important;
    }
    
    /* Additional targeting for select options */
    .stSelectbox div[data-baseweb="select"] div[role="option"] {
        background-color: #ffffff !important;
    }
    
    div[role="listbox"] li:hover {
        background-color: #f8f9fa !important;
    }
    </style>
    """, unsafe_allow_html=True)

    duckdb_conn = get_duckdb_conn()

    # Get the fraud actors dataframe
    fraud_receivers_df = get_fraud_victims(duckdb_conn)
    
    if fraud_receivers_df is not None and not fraud_receivers_df.empty:
        # Convert to list for selectbox
        fraud_receivers_list = fraud_receivers_df['name'].tolist()
        
        with st.sidebar:
            st.page_link('streamlit_app.py', label='Dashboard', icon='📊')
            st.page_link('pages/1_tx_profile.py', label='Tx Profiling', icon='🔍')
            st.page_link('pages/2_actors.py', label='Payment Network', icon='🛜')
            st.page_link('pages/3_balances.py', label='Balances', icon='⚖️')
            st.page_link('pages/4_waterfall.py', label='Waterfall', icon='💧')


            st.divider()

            selected_actor = st.selectbox("Fraud Receivers", fraud_receivers_list)
        
        st.title("💧 Transaction Waterfall Chart")
        
        # Display selected actor information
        if selected_actor:
            st.subheader(f"Analysis for: {selected_actor}")
            
            # Show all transactions for this actor
            actor_transactions = duckdb_conn.sql(f"""
                SELECT *
                FROM paysim 
                WHERE nameOrig = '{selected_actor}' OR nameDest = '{selected_actor}'
                ORDER BY datetime
            """).df()
            
            if not actor_transactions.empty:
                # Create waterfall chart
                st.subheader("Account Balance Waterfall Chart")
                
                # Calculate balance changes for waterfall chart
                waterfall_data = []
                running_balance = 0
                
                # Process transactions chronologically
                for idx, row in actor_transactions.iterrows():
                    # Determine if this is an inflow or outflow for the selected actor
                    if row['nameOrig'] == selected_actor:
                        # Outgoing transaction (negative)
                        amount_change = -row['amount']
                        transaction_type = f"OUT: {row['type']}"
                    else:
                        # Incoming transaction (positive)
                        amount_change = row['amount']
                        transaction_type = f"IN: {row['type']}"
                    
                    # Set color based on fraud status and transaction direction
                    if row['isFraud'] == 1:
                        color = '#f77088'  # Error red for fraud transactions
                    elif amount_change > 0:
                        color = '#05dde3'  # Light blue for positive (inflow) transactions
                    else:
                        color = '#5848d5'  # Purple for negative (outflow) transactions
                    
                    waterfall_data.append({
                        'datetime': row['datetime'],
                        'transaction_type': transaction_type,
                        'amount_change': amount_change,
                        'running_balance': running_balance + amount_change,
                        'is_fraud': row['isFraud'],
                        'color': color,
                        'datetime_str': row['datetime'].strftime('%m/%d %H:%M')
                    })
                    
                    running_balance += amount_change
                
                # Create waterfall chart data
                if waterfall_data:
                    measures = ['relative'] * len(waterfall_data) + ['total']
                    x_values = [item['datetime_str'] for item in waterfall_data] + ['Final Balance']
                    y_values = [item['amount_change'] for item in waterfall_data] + [0]
                    text_values = [f"{item['amount_change']:+,.0f}" for item in waterfall_data] + [f"${running_balance:,.0f}"]
                    colors = [item['color'] for item in waterfall_data] + ['#5848d5']
                    
                    # Create hover text with transaction details
                    hover_text = []
                    for item in waterfall_data:
                        fraud_status = "FRAUD" if item['is_fraud'] == 1 else "Normal"
                        hover_text.append(
                            f"Type: {item['transaction_type']}<br>"
                            f"Amount: ${abs(item['amount_change']):,.2f}<br>"
                            f"Time: {item['datetime_str']}<br>"
                            f"Status: {fraud_status}<br>"
                            f"Running Balance: ${item['running_balance']:,.2f}"
                        )
                    hover_text.append(f"Final Balance: ${running_balance:,.2f}")
                    
                    # Create custom waterfall chart using bar charts for color control
                    fig = go.Figure()
                    
                    # Calculate cumulative positions for waterfall effect
                    cumulative = 0
                    for i, item in enumerate(waterfall_data):
                        # Determine bar position and height
                        if item['amount_change'] >= 0:
                            # Positive change - bar starts at current cumulative
                            y_base = cumulative
                            y_height = item['amount_change']
                        else:
                            # Negative change - bar starts at cumulative + change
                            y_base = cumulative + item['amount_change']
                            y_height = abs(item['amount_change'])
                        
                        # Add individual bar
                        fig.add_trace(go.Bar(
                            x=[item['datetime_str']],
                            y=[y_height],
                            base=[y_base],
                            marker_color=item['color'],
                            text=[f"{item['amount_change']:+,.0f}"],
                            textposition="outside",
                            hovertext=[hover_text[i]],
                            hoverinfo="text",
                            showlegend=False,
                            name=""
                        ))
                        
                        cumulative += item['amount_change']
                    
                    # Add final balance bar
                    fig.add_trace(go.Bar(
                        x=["Final Balance"],
                        y=[abs(running_balance)],
                        base=[0 if running_balance >= 0 else running_balance],
                        marker_color="#0d0c52",
                        text=[f"${running_balance:,.0f}"],
                        textposition="outside",
                        hovertext=[f"Final Balance: ${running_balance:,.2f}"],
                        hoverinfo="text",
                        showlegend=False,
                        name=""
                    ))
                    
                    fig.update_layout(
                        title=f"Account Balance Changes for {selected_actor}",
                        showlegend=False,
                        height=600,
                        xaxis_title="Transaction Timeline",
                        yaxis_title="Amount ($)",
                        xaxis={'tickangle': 45}
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Summary metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        total_inflow = sum([item['amount_change'] for item in waterfall_data if item['amount_change'] > 0])
                        st.metric("Total Inflow", f"${total_inflow:,.2f}")
                    with col2:
                        total_outflow = sum([item['amount_change'] for item in waterfall_data if item['amount_change'] < 0])
                        st.metric("Total Outflow", f"${abs(total_outflow):,.2f}")
                    with col3:
                        net_change = total_inflow + total_outflow
                        st.metric("Net Change", f"${net_change:,.2f}")
                    with col4:
                        fraud_transactions = sum([1 for item in waterfall_data if item['is_fraud'] == 1])
                        st.metric("Fraud Transactions", fraud_transactions)
                else:
                    st.warning("No transaction data available for waterfall chart.")
            
            # Show transaction data table
            st.subheader("Transaction Details")
            st.dataframe(actor_transactions, use_container_width=True)
    else:
        st.title("Analyzing PaySim Actors")
        st.error("No fraud actors found or error loading data")

if __name__ == "__main__":
    main()