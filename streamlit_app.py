import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go
from numpy import log, sqrt, exp
import matplotlib.pyplot as plt
import seaborn as sns

#######################
# Page configuration
st.set_page_config(
    page_title="Black-Scholes Option Pricing Model",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded")

st.markdown(f"""
<style>
/* Adjust the size and alignment of the CALL and PUT value containers */
.metric-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;
    width: auto;
    margin: 10px auto;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}}

/* Custom classes for CALL and PUT values */
.metric-call {{
    background: linear-gradient(135deg, #90ee90 0%, #7ed97e 100%);
    color: #1a5c1a;
    margin-right: 10px;
}}

.metric-put {{
    background: linear-gradient(135deg, #ffcccb 0%, #ff9999 100%);
    color: #8b0000;
}}

/* Style for the value text */
.metric-value {{
    font-size: 2rem;
    font-weight: bold;
    margin: 5px 0;
}}

/* Style for the label text */
.metric-label {{
    font-size: 1.1rem;
    margin-bottom: 8px;
    font-weight: 600;
}}

/* P&L styling */
.pnl-positive {{
    color: #00cc00;
    font-weight: bold;
    font-size: 1.4rem;
}}

.pnl-negative {{
    color: #ff0000;
    font-weight: bold;
    font-size: 1.4rem;
}}

.pnl-container {{
    margin-top: 15px;
    padding: 15px;
    border-radius: 10px;
    background-color: #f0f0f0;
    border: 2px solid #ddd;
}}

/* Spacing improvements */
.stColumn {{
    padding: 10px;
}}

/* Table styling */
.dataframe {{
    margin: 20px 0;
}}

</style>
""", unsafe_allow_html=True)

# BlackScholes class definition
class BlackScholes:
    def __init__(
        self,
        time_to_maturity: float,
        strike: float,
        current_price: float,
        volatility: float,
        interest_rate: float,
    ):
        self.time_to_maturity = time_to_maturity
        self.strike = strike
        self.current_price = current_price
        self.volatility = volatility
        self.interest_rate = interest_rate

    def calculate_prices(
        self,
    ):
        time_to_maturity = self.time_to_maturity
        strike = self.strike
        current_price = self.current_price
        volatility = self.volatility
        interest_rate = self.interest_rate

        d1 = (
            log(current_price / strike) +
            (interest_rate + 0.5 * volatility ** 2) * time_to_maturity
            ) / (
                volatility * sqrt(time_to_maturity)
            )
        d2 = d1 - volatility * sqrt(time_to_maturity)

        call_price = current_price * norm.cdf(d1) - (
            strike * exp(-(interest_rate * time_to_maturity)) * norm.cdf(d2)
        )
        put_price = (
            strike * exp(-(interest_rate * time_to_maturity)) * norm.cdf(-d2)
        ) - current_price * norm.cdf(-d1)

        self.call_price = call_price
        self.put_price = put_price
        self.d1 = d1
        self.d2 = d2

        # GREEKS
        # Delta
        self.call_delta = norm.cdf(d1)
        self.put_delta = 1 - norm.cdf(d1)

        # Gamma
        self.call_gamma = norm.pdf(d1) / (
            strike * volatility * sqrt(time_to_maturity)
        )
        self.put_gamma = self.call_gamma

        return call_price, put_price

    def calculate_pnl(self, call_purchase_price: float = 0.0, put_purchase_price: float = 0.0):
        """Calculate P&L given purchase prices"""
        # Ensure prices are calculated
        if not hasattr(self, 'call_price'):
            self.calculate_prices()
            
        call_pnl = self.call_price - call_purchase_price
        put_pnl = self.put_price - put_purchase_price
        
        return call_pnl, put_pnl


# Sidebar for User Inputs
with st.sidebar:
    st.title("📊 Black-Scholes Model")
    st.write("`Created by:`")
    linkedin_url = "https://www.linkedin.com/in/pavan-nani/"
    st.markdown(f'<a href="{linkedin_url}" target="_blank" style="text-decoration: none; color: inherit;"><img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25" height="25" style="vertical-align: middle; margin-right: 10px;">`Simhadri Pavan Kumar`</a>', unsafe_allow_html=True)
    
    st.markdown("---")

    current_price = st.number_input("Current Asset Price", value=100.0)
    strike = st.number_input("Strike Price", value=100.0)
    time_to_maturity = st.number_input("Time to Maturity (Years)", value=1.0)
    volatility = st.number_input("Volatility (σ)", value=0.2)
    interest_rate = st.number_input("Risk-Free Interest Rate", value=0.05)

    st.markdown("---")
    st.subheader("P&L Calculator")
    call_purchase_price = st.number_input("Call Purchase Price", value=0.0, min_value=0.0, step=0.01)
    put_purchase_price = st.number_input("Put Purchase Price", value=0.0, min_value=0.0, step=0.01)

    st.markdown("---")
    st.subheader("Heatmap Configuration")
    spot_min = st.number_input('Min Spot Price', min_value=0.01, value=current_price*0.8, step=0.01)
    spot_max = st.number_input('Max Spot Price', min_value=0.01, value=current_price*1.2, step=0.01)
    vol_min = st.slider('Min Volatility for Heatmap', min_value=0.01, max_value=1.0, value=volatility*0.5, step=0.01)
    vol_max = st.slider('Max Volatility for Heatmap', min_value=0.01, max_value=1.0, value=volatility*1.5, step=0.01)
    step_count = st.slider('Heatmap Resolution (Grid Size)', min_value=5, max_value=20, value=10, step=1)
    
    # Validation
    if spot_min >= spot_max:
        st.error("⚠️ Min Spot Price must be less than Max Spot Price")
        spot_max = spot_min + 10
    if vol_min >= vol_max:
        st.error("⚠️ Min Volatility must be less than Max Volatility")
        vol_max = vol_min + 0.1
    
    spot_range = np.linspace(spot_min, spot_max, step_count)
    vol_range = np.linspace(vol_min, vol_max, step_count)



# Import HeatmapGenerator and DatabaseService
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from components.heatmap import HeatmapGenerator
from database.db_service import DatabaseService

# Initialize database service
@st.cache_resource
def get_db_service():
    return DatabaseService()


# Main Page for Output Display
st.title("Black-Scholes Pricing Model")

# Table of Inputs
input_data = {
    "Current Asset Price": [current_price],
    "Strike Price": [strike],
    "Time to Maturity (Years)": [time_to_maturity],
    "Volatility (σ)": [volatility],
    "Risk-Free Interest Rate": [interest_rate],
}
input_df = pd.DataFrame(input_data)
st.table(input_df)

# Calculate Call and Put values
bs_model = BlackScholes(time_to_maturity, strike, current_price, volatility, interest_rate)
call_price, put_price = bs_model.calculate_prices()

# Calculate P&L
call_pnl, put_pnl = bs_model.calculate_pnl(call_purchase_price, put_purchase_price)

# Save calculation to database
try:
    db_service = get_db_service()
    calculation_id = db_service.save_calculation({
        'spot_price': current_price,
        'strike': strike,
        'volatility': volatility,
        'time_to_expiry': time_to_maturity,
        'interest_rate': interest_rate,
        'call_purchase_price': call_purchase_price,
        'put_purchase_price': put_purchase_price
    })
except Exception as e:
    st.warning(f"Could not save to database: {str(e)}")

# Display Call and Put Values in colored tables
col1, col2 = st.columns([1,1], gap="small")

with col1:
    # Using the custom class for CALL value
    st.markdown(f"""
        <div class="metric-container metric-call">
            <div>
                <div class="metric-label">CALL Value</div>
                <div class="metric-value">${call_price:.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Display P&L for Call
    if call_purchase_price > 0:
        call_pnl_color = "#00C853" if call_pnl >= 0 else "#FF1744"
        call_pnl_sign = "+" if call_pnl >= 0 else ""
        st.markdown(f"""
            <div class="pnl-container">
                <div style="font-size: 0.9rem;">P&L:</div>
                <div style="color: {call_pnl_color}; font-weight: bold; font-size: 1.4rem;">{call_pnl_sign}${call_pnl:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

with col2:
    # Using the custom class for PUT value
    st.markdown(f"""
        <div class="metric-container metric-put">
            <div>
                <div class="metric-label">PUT Value</div>
                <div class="metric-value">${put_price:.2f}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Display P&L for Put
    if put_purchase_price > 0:
        put_pnl_color = "#00C853" if put_pnl >= 0 else "#FF1744"
        put_pnl_sign = "+" if put_pnl >= 0 else ""
        st.markdown(f"""
            <div class="pnl-container">
                <div style="font-size: 0.9rem;">P&L:</div>
                <div style="color: {put_pnl_color}; font-weight: bold; font-size: 1.4rem;">{put_pnl_sign}${put_pnl:.2f}</div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("")
st.title("Options Price - Interactive Heatmap")

# Toggle between Price and P&L heatmaps
heatmap_type = st.radio("Heatmap Type:", ["Option Price", "P&L Analysis"], horizontal=True)

if heatmap_type == "Option Price":
    st.info("Explore how option prices fluctuate with varying 'Spot Prices and Volatility' levels using interactive heatmap parameters, all while maintaining a constant 'Strike Price'.")
else:
    st.info("Analyze profit/loss across different market scenarios. Green indicates profit, red indicates loss.")

# Create HeatmapGenerator
heatmap_gen = HeatmapGenerator(time_to_maturity, strike, interest_rate)

# Interactive Sliders and Heatmaps for Call and Put Options
st.markdown("<br>", unsafe_allow_html=True)
col1, col2 = st.columns([1,1], gap="large")

if heatmap_type == "Option Price":
    # Generate both heatmaps once
    heatmap_fig_call, heatmap_fig_put = heatmap_gen.generate_price_heatmap(spot_range, vol_range)
    
    with col1:
        st.subheader("Call Price Heatmap")
        st.pyplot(heatmap_fig_call)
        plt.close(heatmap_fig_call)  # Close to free memory

    with col2:
        st.subheader("Put Price Heatmap")
        st.pyplot(heatmap_fig_put)
        plt.close(heatmap_fig_put)  # Close to free memory
else:
    # Generate both P&L heatmaps once
    heatmap_fig_call, heatmap_fig_put = heatmap_gen.generate_pnl_heatmap(spot_range, vol_range, call_purchase_price, put_purchase_price)
    
    with col1:
        st.subheader("Call P&L Heatmap")
        st.pyplot(heatmap_fig_call)
        plt.close(heatmap_fig_call)  # Close to free memory

    with col2:
        st.subheader("Put P&L Heatmap")
        st.pyplot(heatmap_fig_put)
        plt.close(heatmap_fig_put)  # Close to free memory

# Import and render footer
from components.common import render_footer
render_footer()
