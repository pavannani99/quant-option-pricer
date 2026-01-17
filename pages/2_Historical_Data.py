import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.historical_data import HistoricalDataService
from BlackScholes import BlackScholes

st.set_page_config(
    page_title="Historical Data Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling
st.markdown("""
<style>
    /* Professional Color Scheme */
    :root {
        --primary-blue: #1565C0;
        --primary-orange: #F57C00;
        --success-green: #2E7D32;
        --error-red: #C62828;
        --light-bg: #F8F9FA;
        --border-color: #E0E0E0;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #1565C0 0%, #0D47A1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }
    
    .subheader-text {
        font-size: 1.1rem;
        color: #555;
        margin-bottom: 20px;
    }
    
    .metric-box {
        background: linear-gradient(135deg, #F8F9FA 0%, #E3F2FD 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #1565C0;
        margin: 10px 0;
    }
    
    .option-card-call {
        background: linear-gradient(135deg, #C8E6C9 0%, #A5D6A7 100%);
        padding: 25px;
        border-radius: 12px;
        border-left: 4px solid #2E7D32;
        text-align: center;
    }
    
    .option-card-put {
        background: linear-gradient(135deg, #FFCDD2 0%, #EF9A9A 100%);
        padding: 25px;
        border-radius: 12px;
        border-left: 4px solid #C62828;
        text-align: center;
    }
    
    .info-box {
        background: #F8F9FA;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1565C0;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 Historical Data & Volatility Analysis</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader-text">Fetch real market data and calculate historical volatility for option pricing</div>', unsafe_allow_html=True)
hist_service = HistoricalDataService()
with st.sidebar:
    st.header("Market Data Parameters")
    symbol = st.text_input("Stock Symbol", value="AAPL", help="Enter ticker symbol (e.g., AAPL, TSLA, MSFT)").upper()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    col1, col2 = st.columns(2)
    with col1:
        start = st.date_input("Start Date", value=start_date)
    with col2:
        end = st.date_input("End Date", value=end_date)
    volatility_window = st.slider("Volatility Window (days)", min_value=30, max_value=252, value=252, 
                                   help="Number of days to use for volatility calculation")
    fetch_button = st.button("📥 Fetch Data", type="primary")
    st.markdown("---")
    st.header("Option Parameters")
    strike_pct = st.slider("Strike (% of current price)", min_value=80, max_value=120, value=100, step=5)
    time_to_maturity = st.number_input("Time to Maturity (Years)", value=1.0, min_value=0.01)
    interest_rate = st.number_input("Risk-Free Interest Rate", value=0.05)
if fetch_button or 'historical_data' in st.session_state:
    try:
        with st.spinner(f"Fetching data for {symbol}..."):
            df = hist_service.fetch_data(symbol, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
            st.session_state['historical_data'] = df
            st.session_state['symbol'] = symbol
            current_price = hist_service.get_current_price(symbol)
            hist_volatility = hist_service.calculate_historical_volatility(df, volatility_window)
            stats = hist_service.get_price_statistics(df)
            st.session_state['current_price'] = current_price
            st.session_state['hist_volatility'] = hist_volatility
            st.session_state['stats'] = stats
        st.success(f"✅ Successfully fetched data for {symbol}")
        
        st.markdown("---")
        st.markdown('<div style="font-size: 1.8rem; font-weight: 700; margin: 20px 0;">📈 Market Statistics</div>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4, gap="small")
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">Current Price</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1565C0;">${current_price:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">Historical Volatility</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1565C0;">{hist_volatility*100:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            price_change_color = "#2E7D32" if stats['change'] >= 0 else "#C62828"
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">Price Change</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: {price_change_color};">${stats['change']:.2f}</div>
                <div style="font-size: 0.85rem; color: {price_change_color};">{stats['change_pct']:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">Price Range</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1565C0;">${stats['min']:.2f} - ${stats['max']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<div style="font-size: 1.8rem; font-weight: 700; margin: 20px 0;">📊 Historical Price Chart</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='#1565C0', width=3),
            fill='tozeroy',
            fillcolor='rgba(21, 101, 192, 0.1)',
            hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Price:</b> $%{y:.2f}<extra></extra>'
        ))
        fig.update_layout(
            xaxis_title="📅 Date",
            yaxis_title="💰 Price ($)",
            hovermode='x unified',
            height=450,
            template='plotly_white',
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='#F8F9FA',
            paper_bgcolor='white',
            margin=dict(l=50, r=50, t=50, b=50),
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#E0E0E0'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#E0E0E0')
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        st.markdown('<div style="font-size: 1.8rem; font-weight: 700; margin: 20px 0;">📉 Rolling Volatility (30-Day)</div>', unsafe_allow_html=True)
        rolling_vol = []
        dates = []
        for i in range(30, len(df)):
            window_df = df.iloc[i-30:i]
            vol = hist_service.calculate_historical_volatility(window_df, window=30)
            rolling_vol.append(vol * 100)
            dates.append(df.index[i])
        fig_vol = go.Figure()
        fig_vol.add_trace(go.Scatter(
            x=dates,
            y=rolling_vol,
            mode='lines',
            name='30-Day Rolling Volatility',
            line=dict(color='#F57C00', width=3),
            fill='tozeroy',
            fillcolor='rgba(245, 124, 0, 0.1)',
            hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>Volatility:</b> %{y:.2f}%<extra></extra>'
        ))
        fig_vol.update_layout(
            xaxis_title="📅 Date",
            yaxis_title="📊 Volatility (%)",
            hovermode='x unified',
            height=400,
            template='plotly_white',
            font=dict(family="Arial, sans-serif", size=12),
            plot_bgcolor='#F8F9FA',
            paper_bgcolor='white',
            margin=dict(l=50, r=50, t=50, b=50),
            xaxis=dict(showgrid=True, gridwidth=1, gridcolor='#E0E0E0'),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='#E0E0E0')
        )
        st.plotly_chart(fig_vol, use_container_width=True)
        
        st.markdown("---")
        st.markdown('<div style="font-size: 1.8rem; font-weight: 700; margin: 20px 0;">💰 Option Pricing with Historical Volatility</div>', unsafe_allow_html=True)
        strike = current_price * (strike_pct / 100)
        bs = BlackScholes(
            time_to_maturity=time_to_maturity,
            strike=strike,
            current_price=current_price,
            volatility=hist_volatility,
            interest_rate=interest_rate
        )
        call_price, put_price = bs.calculate_prices()
        greeks = bs.calculate_greeks()
        
        col1, col2 = st.columns(2, gap="large")
        with col1:
            st.markdown(f"""
            <div class="option-card-call">
                <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 10px;">📈 CALL Option</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: #1B5E20; margin: 15px 0;">${call_price:.2f}</div>
                <div style="font-size: 0.95rem; color: #333; margin: 10px 0;">
                    <div>Strike: <strong>${strike:.2f}</strong></div>
                    <div>Delta: <strong>{greeks['call_delta']:.4f}</strong></div>
                    <div>Gamma: <strong>{greeks['call_gamma']:.4f}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="option-card-put">
                <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 10px;">📉 PUT Option</div>
                <div style="font-size: 2.2rem; font-weight: 700; color: #B71C1C; margin: 15px 0;">${put_price:.2f}</div>
                <div style="font-size: 0.95rem; color: #333; margin: 10px 0;">
                    <div>Strike: <strong>${strike:.2f}</strong></div>
                    <div>Delta: <strong>{greeks['put_delta']:.4f}</strong></div>
                    <div>Gamma: <strong>{greeks['put_gamma']:.4f}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<div style="font-size: 1.8rem; font-weight: 700; margin: 20px 0; color: #1565C0;">💡 Use These Parameters</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background: #E3F2FD; padding: 20px; border-radius: 10px; border-left: 4px solid #1565C0; margin: 10px 0;">
            <div style="font-size: 1rem; color: #333; line-height: 1.8;">
                <strong style="color: #1565C0;">Copy these values to the main calculator:</strong><br>
                <div style="margin-top: 10px;">
                    <div>📊 Current Asset Price: <strong style="color: #1565C0;">${current_price:.2f}</strong></div>
                    <div>📈 Volatility (σ): <strong style="color: #1565C0;">{hist_volatility:.4f}</strong></div>
                    <div>🎯 Strike Price: <strong style="color: #1565C0;">${strike:.2f}</strong></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error fetching historical data: {str(e)}")
        st.info("Please check the symbol and date range.")

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
