import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from components.greeks import GreeksCalculator

st.set_page_config(
    page_title="Greeks Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    .subheader-text {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 20px;
    }
    
    .greek-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
        text-align: center;
    }
    
    .greek-label {
        font-size: 0.9rem;
        color: #666;
        margin-bottom: 8px;
    }
    
    .greek-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #667eea;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 Options Greeks Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader-text">Analyze the risk sensitivities of your options positions</div>', unsafe_allow_html=True)

# Sidebar inputs
with st.sidebar:
    st.header("Parameters")
    current_price = st.number_input("Current Asset Price", value=100.0, min_value=0.01)
    strike = st.number_input("Strike Price", value=100.0, min_value=0.01)
    time_to_maturity = st.number_input("Time to Maturity (Years)", value=1.0, min_value=0.01)
    volatility = st.number_input("Volatility (σ)", value=0.2, min_value=0.01)
    interest_rate = st.number_input("Risk-Free Interest Rate", value=0.05)
    
    st.markdown("---")
    st.subheader("Analysis Range")
    spot_min = st.number_input('Min Spot Price', min_value=0.01, value=current_price*0.7, step=0.01)
    spot_max = st.number_input('Max Spot Price', min_value=0.01, value=current_price*1.3, step=0.01)
    vol_min = st.slider('Min Volatility', min_value=0.01, max_value=1.0, value=volatility*0.5, step=0.01)
    vol_max = st.slider('Max Volatility', min_value=0.01, max_value=1.0, value=volatility*1.5, step=0.01)
    resolution = st.slider('Resolution', min_value=10, max_value=50, value=20, step=5)

# Create Greeks Calculator
greeks_calc = GreeksCalculator(time_to_maturity, strike, volatility, interest_rate)

# Generate spot range
spot_range = np.linspace(spot_min, spot_max, resolution)
vol_range = np.linspace(vol_min, vol_max, 10)

# Calculate Greeks for range
greeks_df = greeks_calc.calculate_greeks_range(spot_range)

# Tabs for different views
tab1, tab2 = st.tabs(["📊 Line Charts", "🔥 Heatmaps"])

with tab1:
    st.subheader("Greeks vs Spot Price")
    st.markdown("Interactive line charts showing how each Greek changes with spot price")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Greek selector
    greek_options = ['delta', 'gamma', 'theta', 'vega', 'rho']
    
    for greek in greek_options:
        st.markdown(f"### {greek.capitalize()}")
        fig = greeks_calc.plot_greeks_lines(greeks_df, greek)
        st.plotly_chart(fig, width='stretch')
        
        # Add explanation
        if greek == 'delta':
            st.info("**Delta** measures the rate of change of option price with respect to the underlying asset price. Call delta ranges from 0 to 1, put delta from -1 to 0.")
        elif greek == 'gamma':
            st.info("**Gamma** measures the rate of change of delta with respect to the underlying asset price. Higher gamma means delta changes more rapidly.")
        elif greek == 'theta':
            st.info("**Theta** measures the rate of change of option price with respect to time (time decay). Typically negative for long options.")
        elif greek == 'vega':
            st.info("**Vega** measures the rate of change of option price with respect to volatility. Higher vega means more sensitivity to volatility changes.")
        elif greek == 'rho':
            st.info("**Rho** measures the rate of change of option price with respect to interest rates.")
        
        st.markdown("<br>", unsafe_allow_html=True)

with tab2:
    st.subheader("Greeks Heatmaps")
    st.markdown("2D visualization of Greeks across spot price and volatility ranges")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Greek selector for heatmap
    selected_greek = st.selectbox(
        "Select Greek to visualize:",
        options=greek_options,
        format_func=lambda x: x.capitalize()
    )
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### Call {selected_greek.capitalize()}")
        fig_call, _ = greeks_calc.plot_greeks_heatmap(spot_range, vol_range, selected_greek)
        st.pyplot(fig_call)
        plt.close(fig_call)
    
    with col2:
        st.markdown(f"#### Put {selected_greek.capitalize()}")
        _, fig_put = greeks_calc.plot_greeks_heatmap(spot_range, vol_range, selected_greek)
        st.pyplot(fig_put)
        plt.close(fig_put)

# Display current Greeks values
st.markdown("---")
st.markdown('<div style="font-size: 1.8rem; font-weight: 700; margin: 20px 0;">📊 Current Greeks Values</div>', unsafe_allow_html=True)

from BlackScholes import BlackScholes
bs = BlackScholes(time_to_maturity, strike, current_price, volatility, interest_rate)
current_greeks = bs.calculate_greeks()

# Helper function for color-coded metrics
def render_colored_metric(label: str, value: float, precision: int = 4):
    """Render a metric with color coding based on value sign"""
    color = "#667eea" if value >= 0 else "#ff6b6b"
    formatted_value = f"{value:.{precision}f}"
    
    html = f"""
    <div class="greek-card">
        <div class="greek-label">{label}</div>
        <div class="greek-value" style="color: {color};">{formatted_value}</div>
    </div>
    """
    return html

# Render metrics with color coding
col1, col2, col3, col4, col5 = st.columns(5, gap="small")

with col1:
    st.markdown(render_colored_metric("Call Δ (Delta)", current_greeks['call_delta']), unsafe_allow_html=True)
    st.markdown(render_colored_metric("Put Δ (Delta)", current_greeks['put_delta']), unsafe_allow_html=True)

with col2:
    st.markdown(render_colored_metric("Call Γ (Gamma)", current_greeks['call_gamma']), unsafe_allow_html=True)
    st.markdown(render_colored_metric("Put Γ (Gamma)", current_greeks['put_gamma']), unsafe_allow_html=True)

with col3:
    st.markdown(render_colored_metric("Call Θ (Theta)", current_greeks['call_theta']), unsafe_allow_html=True)
    st.markdown(render_colored_metric("Put Θ (Theta)", current_greeks['put_theta']), unsafe_allow_html=True)

with col4:
    st.markdown(render_colored_metric("Call ν (Vega)", current_greeks['call_vega']), unsafe_allow_html=True)
    st.markdown(render_colored_metric("Put ν (Vega)", current_greeks['put_vega']), unsafe_allow_html=True)

with col5:
    st.markdown(render_colored_metric("Call ρ (Rho)", current_greeks['call_rho']), unsafe_allow_html=True)
    st.markdown(render_colored_metric("Put ρ (Rho)", current_greeks['put_rho']), unsafe_allow_html=True)

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
