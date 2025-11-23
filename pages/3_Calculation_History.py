import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.db_service import DatabaseService
from BlackScholes import BlackScholes
st.set_page_config(
    page_title="Calculation History",
    page_icon="📜",
    layout="wide"
)
st.markdown("---")
st.title("📜 Calculation History")
st.markdown("View and replay your previous Black-Scholes calculations")
try:
    db_service = DatabaseService()
    stats = db_service.get_statistics()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Calculations", stats['total_calculations'])
    with col2:
        st.metric("Total Outputs", stats['total_outputs'])
    with col3:
        if stats['first_calculation']:
            st.metric("First Calculation", stats['first_calculation'][:10])
        else:
            st.metric("First Calculation", "N/A")
    with col4:
        if stats['last_calculation']:
            st.metric("Last Calculation", stats['last_calculation'][:10])
        else:
            st.metric("Last Calculation", "N/A")
    st.markdown("---")
    limit = st.slider("Number of records to display", min_value=10, max_value=100, value=50, step=10)
    history_df = db_service.get_calculation_history(limit=limit)
    if not history_df.empty:
        st.subheader("Recent Calculations")
        display_df = history_df.copy()
        display_df['created_at'] = display_df['created_at'].str[:19]  # Trim timestamp
        display_df['volatility'] = (display_df['volatility'] * 100).round(2).astype(str) + '%'
        display_df['interest_rate'] = (display_df['interest_rate'] * 100).round(2).astype(str) + '%'
        display_df = display_df.rename(columns={
            'calculation_id': 'ID',
            'spot_price': 'Spot',
            'strike': 'Strike',
            'volatility': 'Vol',
            'time_to_expiry': 'Time',
            'interest_rate': 'Rate',
            'call_purchase_price': 'Call Purchase',
            'put_purchase_price': 'Put Purchase',
            'created_at': 'Date'
        })
        st.dataframe(display_df, width='stretch', hide_index=True)
        
        # Add CSV download button with formatted data
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name="blackscholes_calculations.csv",
            mime="text/csv"
        )
        
        st.markdown("---")
        st.subheader("🔄 Replay Calculation")
        calc_ids = history_df['calculation_id'].tolist()
        calc_labels = [f"{row['created_at'][:19]} - Spot: ${row['spot_price']:.2f}, Strike: ${row['strike']:.2f}" 
                      for _, row in history_df.iterrows()]
        selected_idx = st.selectbox("Select a calculation to replay:", 
                                     range(len(calc_labels)), 
                                     format_func=lambda x: calc_labels[x])
        if st.button("🔄 Replay Selected Calculation"):
            selected_id = calc_ids[selected_idx]
            calc_data = db_service.get_calculation_by_id(selected_id)
            st.success(f"Replaying calculation from {calc_data['created_at']}")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Input Parameters")
                st.write(f"**Spot Price:** ${calc_data['spot_price']:.2f}")
                st.write(f"**Strike Price:** ${calc_data['strike']:.2f}")
                st.write(f"**Volatility:** {calc_data['volatility']*100:.2f}%")
                st.write(f"**Time to Expiry:** {calc_data['time_to_expiry']:.2f} years")
                st.write(f"**Interest Rate:** {calc_data['interest_rate']*100:.2f}%")
                st.write(f"**Call Purchase Price:** ${calc_data['call_purchase_price']:.2f}")
                st.write(f"**Put Purchase Price:** ${calc_data['put_purchase_price']:.2f}")
            with col2:
                st.markdown("### Recalculated Results")
                bs = BlackScholes(
                    time_to_maturity=calc_data['time_to_expiry'],
                    strike=calc_data['strike'],
                    current_price=calc_data['spot_price'],
                    volatility=calc_data['volatility'],
                    interest_rate=calc_data['interest_rate']
                )
                call_price, put_price = bs.calculate_prices()
                call_pnl, put_pnl = bs.calculate_pnl(
                    calc_data['call_purchase_price'],
                    calc_data['put_purchase_price']
                )
                call_pnl_color = 'green' if call_pnl >= 0 else 'red'
                put_pnl_color = 'green' if put_pnl >= 0 else 'red'
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                        <div style="background-color: #90ee90; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                            <h4>CALL Option</h4>
                            <p style="font-size: 1.5rem; font-weight: bold;">${call_price:.2f}</p>
                            <p>P&L: <span style="color: {call_pnl_color}; font-weight: bold;">${call_pnl:.2f}</span></p>
                        </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                        <div style="background-color: #ffcccb; padding: 15px; border-radius: 10px; margin-bottom: 10px;">
                            <h4>PUT Option</h4>
                            <p style="font-size: 1.5rem; font-weight: bold;">${put_price:.2f}</p>
                            <p>P&L: <span style="color: {put_pnl_color}; font-weight: bold;">${put_pnl:.2f}</span></p>
                        </div>
                    """, unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("🗑️ Delete Calculation")
        delete_idx = st.selectbox("Select a calculation to delete:", 
                                   range(len(calc_labels)), 
                                   format_func=lambda x: calc_labels[x],
                                   key="delete_select")
        if st.button("🗑️ Delete Selected Calculation", type="secondary"):
            delete_id = calc_ids[delete_idx]
            db_service.delete_calculation(delete_id)
            st.success("Calculation deleted successfully!")
            st.rerun()
    else:
        st.info("No calculations found in the database. Start using the calculator to build your history!")
        st.markdown("""
        1. Go to the main Black-Scholes Calculator page
        2. Enter your parameters and view the results
        3. Each calculation is automatically saved
        4. Return here to view, replay, or delete past calculations

        """)
except Exception as e:
    st.error(f"Error loading calculation history: {str(e)}")
    st.info("Please check your database connection.")

# LinkedIn Footer
st.markdown("---")
linkedin_url = "https://www.linkedin.com/in/pavan-nani/"
st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <p style="margin: 5px;">Created by <strong>Simhadri Pavan Kumar</strong></p>
        <a href="{linkedin_url}" target="_blank" style="text-decoration: none;">
            <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="30" height="30" style="vertical-align: middle;">
            <span style="margin-left: 10px; color: #0077b5; font-weight: bold;">Connect on LinkedIn</span>
        </a>
    </div>
""", unsafe_allow_html=True)
