import streamlit as st
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.backtest import BacktestEngine
from services.historical_data import HistoricalDataService

st.set_page_config(
    page_title="Strategy Backtesting",
    page_icon="📈",
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
    
    .success-box {
        background: linear-gradient(135deg, #C8E6C9 0%, #A5D6A7 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #2E7D32;
    }
    
    .loss-box {
        background: linear-gradient(135deg, #FFCDD2 0%, #EF9A9A 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #C62828;
    }
    
    .info-card {
        background: #F8F9FA;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #1565C0;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📈 Options Strategy Backtesting</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader-text">Simulate and evaluate option trading strategies using historical market data</div>', unsafe_allow_html=True)
with st.sidebar:
    st.header("Backtest Parameters")
    symbol = st.text_input("Stock Symbol", value="AAPL", help="Enter ticker symbol").upper()
    
    today = datetime.now().date()
    one_year_ago = today - timedelta(days=365)
    
    col1, col2 = st.columns(2)
    with col1:
        data_start = st.date_input("Data Start", value=one_year_ago)
    with col2:
        data_end = st.date_input("Data End", value=today, max_value=today)
    
    # Validate date range
    if data_start >= data_end:
        st.error("❌ Start date must be before end date")
        st.stop()
    st.markdown("---")
    st.subheader("Strategy Configuration")
    strategy_type = st.selectbox("Strategy Type", ["call", "put"], 
                                 format_func=lambda x: f"Buy {x.upper()} and Hold")
    entry_date = st.date_input("Entry Date", value=one_year_ago + timedelta(days=30), 
                               min_value=data_start, max_value=data_end)
    
    # Validate entry date
    if entry_date < data_start or entry_date > data_end:
        st.error(f"❌ Entry date must be within data range ({data_start} to {data_end})")
    holding_days = st.slider("Holding Period (Days)", min_value=1, max_value=365, value=30)
    st.markdown("---")
    st.subheader("Option Parameters")
    strike_pct = st.slider("Strike (% of entry price)", min_value=80, max_value=120, value=100, step=5)
    volatility = st.number_input("Volatility (σ)", value=0.25, min_value=0.01, step=0.01)
    interest_rate = st.number_input("Risk-Free Rate", value=0.05, step=0.01)
    run_backtest = st.button("🚀 Run Backtest", type="primary")
if run_backtest or 'backtest_result' in st.session_state:
    try:
        with st.spinner(f"Running backtest for {symbol}..."):
            # Convert dates to strings
            start_str = data_start.strftime('%Y-%m-%d')
            end_str = data_end.strftime('%Y-%m-%d')
            
            # Create engine with error handling
            try:
                engine = BacktestEngine(
                    symbol=symbol,
                    start_date=start_str,
                    end_date=end_str
                )
            except ValueError as e:
                st.error(f"❌ Failed to fetch data: {str(e)}")
                st.info("💡 Tip: Try a different date range or verify the stock symbol is correct.")
                st.stop()
            
            # Get entry price from the available data
            entry_date_str = entry_date.strftime('%Y-%m-%d')
            
            # Find the closest available date in our dataset for entry price
            available_dates = engine.price_data.index.date
            entry_date_obj = entry_date
            
            # Find the closest date that exists in our data
            closest_date_idx = None
            min_diff = float('inf')
            
            for i, date in enumerate(available_dates):
                diff = abs((date - entry_date_obj).days)
                if diff < min_diff:
                    min_diff = diff
                    closest_date_idx = i
            
            if closest_date_idx is not None:
                entry_price = engine.price_data['Close'].iloc[closest_date_idx]
                actual_entry_date = available_dates[closest_date_idx]
                if min_diff > 0:
                    st.info(f"ℹ️ Using closest available date {actual_entry_date} for entry price (requested: {entry_date_str})")
            else:
                st.error("❌ Could not find suitable entry date in the data")
                st.stop()
            
            strike = entry_price * (strike_pct / 100)
            result = engine.run_strategy(
                strategy_type=strategy_type,
                strike=strike,
                entry_date=entry_date.strftime('%Y-%m-%d'),
                holding_days=holding_days,
                volatility=volatility,
                interest_rate=interest_rate
            )
            st.session_state['backtest_result'] = result
            st.session_state['backtest_metrics'] = engine.calculate_metrics(result.pnl_series)
        result = st.session_state['backtest_result']
        metrics = st.session_state['backtest_metrics']
        
        st.markdown("---")
        st.markdown('<div style="font-size: 1.8rem; font-weight: 700; margin: 20px 0;">📊 Performance Summary</div>', unsafe_allow_html=True)
        
        # Key metrics in professional cards
        col1, col2, col3, col4, col5 = st.columns(5, gap="small")
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">Entry Price</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1565C0;">${result.entry_price:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">Exit Price</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1565C0;">${result.exit_price:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            pnl_color = "#2E7D32" if result.pnl >= 0 else "#C62828"
            pnl_sign = "+" if result.pnl >= 0 else ""
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">Total P&L</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: {pnl_color};">{pnl_sign}${result.pnl:.2f}</div>
                <div style="font-size: 0.85rem; color: {pnl_color};">{pnl_sign}{result.pnl_pct:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">Entry Option Value</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1565C0;">${result.option_entry_value:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col5:
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">Exit Option Value</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1565C0;">${result.option_exit_value:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Additional metrics
        col1, col2, col3, col4 = st.columns(4, gap="small")
        
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">Max P&L</div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #2E7D32;">${metrics['max_pnl']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">Min P&L</div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #C62828;">${metrics['min_pnl']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">Max Drawdown</div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #F57C00;">${metrics['max_drawdown']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-box">
                <div style="font-size: 0.9rem; color: #666;">P&L Volatility</div>
                <div style="font-size: 1.6rem; font-weight: 700; color: #1565C0;">${metrics['volatility']:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown('<div style="font-size: 1.8rem; font-weight: 700; margin: 20px 0;">📈 P&L Progression Over Time</div>', unsafe_allow_html=True)
        
        # Create professional P&L chart
        fig = go.Figure()
        
        # Determine color based on P&L
        pnl_color = '#2E7D32' if result.pnl >= 0 else '#C62828'
        fill_color = 'rgba(46, 125, 50, 0.1)' if result.pnl >= 0 else 'rgba(198, 40, 40, 0.1)'
        
        # Add P&L line
        fig.add_trace(go.Scatter(
            x=result.dates,
            y=result.pnl_series,
            mode='lines',
            name='P&L',
            line=dict(color=pnl_color, width=3),
            fill='tozeroy',
            fillcolor=fill_color,
            hovertemplate='<b>Date:</b> %{x|%Y-%m-%d}<br><b>P&L:</b> $%{y:.2f}<extra></extra>'
        ))
        
        # Add zero line
        fig.add_hline(y=0, line_dash="dash", line_color="#666", opacity=0.4, annotation_text="Break-even")
        
        # Add max P&L line
        fig.add_hline(y=metrics['max_pnl'], line_dash="dot", line_color="#2E7D32", opacity=0.2)
        
        # Add min P&L line
        fig.add_hline(y=metrics['min_pnl'], line_dash="dot", line_color="#C62828", opacity=0.2)
        
        fig.update_layout(
            xaxis_title="📅 Date",
            yaxis_title="💰 P&L ($)",
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
        st.markdown('<div style="font-size: 1.8rem; font-weight: 700; margin: 20px 0;">📋 Strategy Details</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            st.markdown("""
            <div class="info-card">
                <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 15px;">🎯 Trade Information</div>
            </div>
            """, unsafe_allow_html=True)
            st.write(f"**Strategy Type:** Buy {strategy_type.upper()} and Hold")
            st.write(f"**Stock Symbol:** {symbol}")
            st.write(f"**Entry Date:** {result.entry_date.strftime('%Y-%m-%d')}")
            st.write(f"**Exit Date:** {result.exit_date.strftime('%Y-%m-%d')}")
            st.write(f"**Holding Period:** {holding_days} days")
            st.write(f"**Strike Price:** ${strike:.2f}")
        
        with col2:
            st.markdown("""
            <div class="info-card">
                <div style="font-size: 1.2rem; font-weight: 700; margin-bottom: 15px;">📊 Market Conditions</div>
            </div>
            """, unsafe_allow_html=True)
            st.write(f"**Entry Spot Price:** ${result.entry_price:.2f}")
            st.write(f"**Exit Spot Price:** ${result.exit_price:.2f}")
            price_change = result.exit_price - result.entry_price
            price_change_pct = ((result.exit_price/result.entry_price - 1) * 100)
            price_color = "🟢" if price_change >= 0 else "🔴"
            st.write(f"**Price Change:** {price_color} ${price_change:.2f} ({price_change_pct:.2f}%)")
            st.write(f"**Volatility Used:** {volatility*100:.2f}%")
            st.write(f"**Interest Rate:** {interest_rate*100:.2f}%")
        
        st.markdown("---")
        st.markdown('<div style="font-size: 1.8rem; font-weight: 700; margin: 20px 0;">💡 Strategy Interpretation</div>', unsafe_allow_html=True)
        
        if result.pnl > 0:
            st.markdown(f"""
            <div class="success-box">
                <div style="font-size: 1.3rem; font-weight: 700; margin-bottom: 10px;">✅ Profitable Strategy!</div>
                <div style="font-size: 1rem; line-height: 1.6;">
                    The <strong>{strategy_type.upper()}</strong> option strategy generated a profit of <strong style="color: #00c853;">${result.pnl:.2f}</strong> 
                    with a return of <strong style="color: #00c853;">{result.pnl_pct:.2f}%</strong>.<br>
                    The underlying stock moved from <strong>${result.entry_price:.2f}</strong> to <strong>${result.exit_price:.2f}</strong>.
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="loss-box">
                <div style="font-size: 1.3rem; font-weight: 700; margin-bottom: 10px;">⚠️ Loss Incurred</div>
                <div style="font-size: 1rem; line-height: 1.6;">
                    The <strong>{strategy_type.upper()}</strong> option strategy resulted in a loss of <strong style="color: #ff1744;">${result.pnl:.2f}</strong> 
                    with a return of <strong style="color: #ff1744;">{result.pnl_pct:.2f}%</strong>.<br>
                    The underlying stock moved from <strong>${result.entry_price:.2f}</strong> to <strong>${result.exit_price:.2f}</strong>.
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if metrics['max_drawdown'] > abs(result.pnl) * 0.5:
            st.warning(f"⚠️ High drawdown detected: ${metrics['max_drawdown']:.2f}. The position experienced significant unrealized losses during the holding period.")
    except ValueError as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("💡 Troubleshooting tips:\n- Verify the stock symbol is correct (e.g., AAPL, MSFT, GOOGL)\n- Try a different date range\n- Ensure the start date is before the end date\n- Check your internet connection")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        import traceback
        with st.expander("📋 Error Details"):
            st.code(traceback.format_exc())
else:
    st.info("👆 Configure your backtest parameters in the sidebar and click 'Run Backtest' to begin")
    st.markdown("""
    1. **Select a stock symbol** and date range for historical data
    2. **Choose your strategy**: Buy Call or Buy Put
    3. **Set entry date** and holding period
    4. **Configure option parameters**: Strike price, volatility, interest rate
    5. Click "Run Backtest" to simulate the strategy
    - **Performance Metrics**: Total P&L, return percentage, max drawdown
    - **P&L Chart**: Visual representation of profit/loss over time
    - **Trade Details**: Entry/exit prices, dates, and market conditions
    - **Interpretation**: Analysis of strategy performance
    - **Buy Call and Hold**: Profit if stock price rises above strike
    - **Buy Put and Hold**: Profit if stock price falls below strike
    - This backtest assumes you hold the option until the exit date
    - Option values are calculated using the Black-Scholes model
    - Past performance does not guarantee future results
    - Consider transaction costs and slippage in real trading
    """)

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
