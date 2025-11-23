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
    layout="wide"
)
st.markdown("---")
st.title("📈 Options Strategy Backtesting")
st.markdown("Simulate and evaluate option trading strategies using historical market data")
with st.sidebar:
    st.header("Backtest Parameters")
    symbol = st.text_input("Stock Symbol", value="AAPL", help="Enter ticker symbol").upper()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    col1, col2 = st.columns(2)
    with col1:
        data_start = st.date_input("Data Start", value=start_date)
    with col2:
        data_end = st.date_input("Data End", value=end_date)
    st.markdown("---")
    st.subheader("Strategy Configuration")
    strategy_type = st.selectbox("Strategy Type", ["call", "put"], 
                                 format_func=lambda x: f"Buy {x.upper()} and Hold")
    entry_date = st.date_input("Entry Date", value=start_date + timedelta(days=30))
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
            engine = BacktestEngine(
                symbol=symbol,
                start_date=data_start.strftime('%Y-%m-%d'),
                end_date=data_end.strftime('%Y-%m-%d')
            )
            hist_service = HistoricalDataService()
            entry_data = hist_service.fetch_data(symbol, entry_date.strftime('%Y-%m-%d'), 
                                                 (entry_date + timedelta(days=1)).strftime('%Y-%m-%d'))
            entry_price = entry_data['Close'].iloc[0]
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
        st.success(f"✅ Backtest completed for {symbol}")
        st.subheader("Performance Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Entry Price", f"${result.entry_price:.2f}")
        with col2:
            st.metric("Exit Price", f"${result.exit_price:.2f}")
        with col3:
            pnl_color = "normal" if result.pnl >= 0 else "inverse"
            st.metric("Total P&L", f"${result.pnl:.2f}", f"{result.pnl_pct:.2f}%")
        with col4:
            st.metric("Entry Option Value", f"${result.option_entry_value:.2f}")
        with col5:
            st.metric("Exit Option Value", f"${result.option_exit_value:.2f}")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Max P&L", f"${metrics['max_pnl']:.2f}")
        with col2:
            st.metric("Min P&L", f"${metrics['min_pnl']:.2f}")
        with col3:
            st.metric("Max Drawdown", f"${metrics['max_drawdown']:.2f}")
        with col4:
            st.metric("P&L Volatility", f"${metrics['volatility']:.2f}")
        st.markdown("---")
        st.subheader("P&L Progression Over Time")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=result.dates,
            y=result.pnl_series,
            mode='lines',
            name='P&L',
            line=dict(color='blue', width=2),
            fill='tozeroy',
            fillcolor='rgba(0, 100, 255, 0.2)'
        ))
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="P&L ($)",
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, width='stretch')
        st.markdown("---")
        st.subheader("Strategy Details")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Trade Information")
            st.write(f"**Strategy:** Buy {strategy_type.upper()} and Hold")
            st.write(f"**Symbol:** {symbol}")
            st.write(f"**Entry Date:** {result.entry_date.strftime('%Y-%m-%d')}")
            st.write(f"**Exit Date:** {result.exit_date.strftime('%Y-%m-%d')}")
            st.write(f"**Holding Period:** {holding_days} days")
            st.write(f"**Strike Price:** ${strike:.2f}")
        with col2:
            st.markdown("### Market Conditions")
            st.write(f"**Entry Spot Price:** ${result.entry_price:.2f}")
            st.write(f"**Exit Spot Price:** ${result.exit_price:.2f}")
            st.write(f"**Price Change:** ${result.exit_price - result.entry_price:.2f} ({((result.exit_price/result.entry_price - 1) * 100):.2f}%)")
            st.write(f"**Volatility Used:** {volatility*100:.2f}%")
            st.write(f"**Interest Rate:** {interest_rate*100:.2f}%")
        st.markdown("---")
        st.subheader("📊 Interpretation")
        if result.pnl > 0:
            st.success(f"""
            **Profitable Strategy!** 
            The {strategy_type} option strategy generated a profit of ${result.pnl:.2f} ({result.pnl_pct:.2f}% return).
            The underlying stock moved from ${result.entry_price:.2f} to ${result.exit_price:.2f}.
            """)
        else:
            st.error(f"""
            **Loss Incurred** 
            The {strategy_type} option strategy resulted in a loss of ${result.pnl:.2f} ({result.pnl_pct:.2f}% return).
            The underlying stock moved from ${result.entry_price:.2f} to ${result.exit_price:.2f}.
            """)
        
        if metrics['max_drawdown'] > abs(result.pnl) * 0.5:
            st.warning(f"⚠️ High drawdown detected: ${metrics['max_drawdown']:.2f}. The position experienced significant unrealized losses during the holding period.")
    except ValueError as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("Please check your parameters and ensure the dates are within the available data range.")
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
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
