import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import networkx as nx
from pyvis.network import Network

from utils import get_duckdb_conn
from charts import get_fraud_victims

def main():

    duckdb_conn = get_duckdb_conn()

    # Get the fraud actors dataframe
    fraud_receivers_df = get_fraud_victims(duckdb_conn)
    
    if fraud_receivers_df is not None and not fraud_receivers_df.empty:
        # Convert to list for selectbox
        fraud_receivers_list = fraud_receivers_df['name'].tolist()
        
        with st.sidebar:
            selected_actor = st.selectbox("Fraud Receivers", fraud_receivers_list)
        
        st.title("Analyzing PaySim Actors")
        
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
                # Create network graph
                st.subheader("Transaction Network Graph")
                
                # Create networkx graph from transactions
                # Convert datetime to string to avoid JSON serialization issues
                actor_transactions_copy = actor_transactions.copy()
                actor_transactions_copy['datetime_str'] = actor_transactions_copy['datetime'].astype(str)
                
                G = nx.from_pandas_edgelist(
                    actor_transactions_copy, 
                    source='nameOrig', 
                    target='nameDest',
                    edge_attr=['datetime_str', 'amount', 'type', 'isFraud']
                )
                
                # Create PyVis network
                net = Network(
                    height='600px',
                    width='100%',
                    bgcolor='#222222',
                    font_color='white'
                )
                
                # Convert NetworkX to PyVis
                net.from_nx(G)
                
                # Customize edges based on fraud status and add tooltips
                for edge in net.edges:
                    # Find the corresponding transaction data
                    orig = edge['from']
                    dest = edge['to']
                    
                    # Get transaction details for this edge
                    filtered_trans = actor_transactions[
                        (actor_transactions['nameOrig'] == orig) & 
                        (actor_transactions['nameDest'] == dest)
                    ]
                    
                    # Skip edge if no matching transactions found
                    if len(filtered_trans) == 0:
                        continue
                        
                    trans_data = filtered_trans.iloc[0]
                    
                    # Color edge red for fraud, blue for normal
                    edge['color'] = 'red' if trans_data['isFraud'] == 1 else 'blue'
                    edge['width'] = 3 if trans_data['isFraud'] == 1 else 1
                    
                    # Only add tooltip for fraudulent transactions
                    if trans_data['isFraud'] == 1:
                        datetime_str = trans_data['datetime'].strftime('%Y/%m/%d %H:%M') if hasattr(trans_data['datetime'], 'strftime') else str(trans_data['datetime'])
                        edge['title'] = f"FRAUD: Amount = ${trans_data['amount']:,.2f}, Datetime = {datetime_str}, Type = {trans_data['type']}"
                        # Add label for fraud transactions
                        edge['label'] = f"FRAUD ${trans_data['amount']:,.0f}"
                    else:
                        # No tooltip for normal transactions, just basic label
                        edge['label'] = f"${trans_data['amount']:,.0f}"
                
                # Customize node appearance
                for node in net.nodes:
                    if node['id'] == selected_actor:
                        node['color'] = 'orange'  # Highlight selected actor
                        node['size'] = 30
                    else:
                        node['color'] = 'lightblue'
                        node['size'] = 20
                
                # Set physics layout
                net.repulsion(
                    node_distance=200,
                    central_gravity=0.33,
                    spring_length=100,
                    spring_strength=0.10,
                    damping=0.95
                )
                
                # Enable click-to-select for edges
                net.set_options("""
                var options = {
                    "interaction": {
                        "selectConnectedEdges": false,
                        "hover": true
                    },
                    "manipulation": {
                        "enabled": false
                    },
                    "physics": {
                        "enabled": true
                    }
                }
                """)
                
                # Save and display graph
                try:
                    import tempfile
                    import os
                    
                    # Create temporary file
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp_file:
                        net.save_graph(tmp_file.name)
                        
                        # Read and display
                        with open(tmp_file.name, 'r', encoding='utf-8') as HtmlFile:
                            components.html(HtmlFile.read(), height=635)
                        
                        # Clean up
                        os.unlink(tmp_file.name)
                        
                except Exception as e:
                    st.error(f"Error creating network graph: {e}")
            
            # Show transaction data table
            st.subheader("Transaction Details")
            st.dataframe(actor_transactions, use_container_width=True)
    else:
        st.title("Analyzing PaySim Actors")
        st.error("No fraud actors found or error loading data")

if __name__ == "__main__":
    main()