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
    layout="wide"
)
st.markdown("---")
st.title("📊 Historical Data & Volatility Analysis")
st.markdown("Fetch real market data and calculate historical volatility for option pricing")
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
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Current Price", f"${current_price:.2f}")
        with col2:
            st.metric("Historical Volatility", f"{hist_volatility*100:.2f}%")
        with col3:
            st.metric("Price Change", f"${stats['change']:.2f}", f"{stats['change_pct']:.2f}%")
        with col4:
            st.metric("Price Range", f"${stats['min']:.2f} - ${stats['max']:.2f}")
        st.subheader("Historical Price Chart")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['Close'],
            mode='lines',
            name='Close Price',
            line=dict(color='blue', width=2)
        ))
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price ($)",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, width='stretch')
        st.subheader("Rolling Volatility")
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
            line=dict(color='orange', width=2)
        ))
        fig_vol.update_layout(
            xaxis_title="Date",
            yaxis_title="Volatility (%)",
            hovermode='x unified',
            height=300
        )
        st.plotly_chart(fig_vol, width='stretch')
        st.markdown("---")
        st.subheader("Option Pricing with Historical Volatility")
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
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
                <div style="background-color: #90ee90; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3>CALL Option</h3>
                    <h2>$""" + f"{call_price:.2f}" + """</h2>
                    <p>Strike: $""" + f"{strike:.2f}" + """</p>
                    <p>Delta: """ + f"{greeks['call_delta']:.4f}" + """</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
                <div style="background-color: #ffcccb; padding: 20px; border-radius: 10px; text-align: center;">
                    <h3>PUT Option</h3>
                    <h2>$""" + f"{put_price:.2f}" + """</h2>
                    <p>Strike: $""" + f"{strike:.2f}" + """</p>
                    <p>Delta: """ + f"{greeks['put_delta']:.4f}" + """</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📋 Use These Parameters")
        param_text = f"""
        **Copy these values to the main calculator:**
        - Current Asset Price: ${current_price:.2f}
        - Volatility (σ): {hist_volatility:.4f}
        - Strike Price: ${strike:.2f}
        """
        st.info(param_text)
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
