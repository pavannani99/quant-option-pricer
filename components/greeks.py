import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from BlackScholes import BlackScholes
# Colormap: Green (high values) -> Yellow (mid) -> Red (low values)
CUSTOM_CMAP = LinearSegmentedColormap.from_list(
    'custom_green_red',
    ['#1a9850', '#91cf60', '#d9ef8b', '#fee08b', '#fc8d59', '#d73027']
)
class GreeksCalculator:
    def __init__(self, time_to_maturity, strike, volatility, interest_rate):
        self.time_to_maturity = time_to_maturity
        self.strike = strike
        self.volatility = volatility
        self.interest_rate = interest_rate
    def calculate_greeks_range(self, spot_range):
        greeks_data = {
            'spot_price': [],
            'call_delta': [],
            'put_delta': [],
            'call_gamma': [],
            'put_gamma': [],
            'call_theta': [],
            'put_theta': [],
            'call_vega': [],
            'put_vega': [],
            'call_rho': [],
            'put_rho': []
        }
        for spot in spot_range:
            bs = BlackScholes(
                time_to_maturity=self.time_to_maturity,
                strike=self.strike,
                current_price=spot,
                volatility=self.volatility,
                interest_rate=self.interest_rate
            )
            greeks = bs.calculate_greeks()
            greeks_data['spot_price'].append(spot)
            greeks_data['call_delta'].append(greeks['call_delta'])
            greeks_data['put_delta'].append(greeks['put_delta'])
            greeks_data['call_gamma'].append(greeks['call_gamma'])
            greeks_data['put_gamma'].append(greeks['put_gamma'])
            greeks_data['call_theta'].append(greeks['call_theta'])
            greeks_data['put_theta'].append(greeks['put_theta'])
            greeks_data['call_vega'].append(greeks['call_vega'])
            greeks_data['put_vega'].append(greeks['put_vega'])
            greeks_data['call_rho'].append(greeks['call_rho'])
            greeks_data['put_rho'].append(greeks['put_rho'])
        return pd.DataFrame(greeks_data)
    def plot_greeks_lines(self, greeks_df, greek_name='delta'):
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(f'Call {greek_name.capitalize()}', f'Put {greek_name.capitalize()}')
        )
        fig.add_trace(
            go.Scatter(
                x=greeks_df['spot_price'],
                y=greeks_df[f'call_{greek_name}'],
                mode='lines',
                name=f'Call {greek_name.capitalize()}',
                line=dict(color='green', width=2),
                hovertemplate='Spot: %{x:.2f}<br>Value: %{y:.4f}<extra></extra>'
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=greeks_df['spot_price'],
                y=greeks_df[f'put_{greek_name}'],
                mode='lines',
                name=f'Put {greek_name.capitalize()}',
                line=dict(color='red', width=2),
                hovertemplate='Spot: %{x:.2f}<br>Value: %{y:.4f}<extra></extra>'
            ),
            row=1, col=2
        )
        fig.update_xaxes(title_text="Spot Price", row=1, col=1)
        fig.update_xaxes(title_text="Spot Price", row=1, col=2)
        fig.update_yaxes(title_text=greek_name.capitalize(), row=1, col=1)
        fig.update_yaxes(title_text=greek_name.capitalize(), row=1, col=2)
        fig.update_layout(
            height=400,
            showlegend=False,
            title_text=f"{greek_name.capitalize()} vs Spot Price"
        )
        return fig
    def plot_greeks_heatmap(self, spot_range, vol_range, greek_name='delta'):
        call_greek = np.zeros((len(vol_range), len(spot_range)))
        put_greek = np.zeros((len(vol_range), len(spot_range)))
        for i, vol in enumerate(vol_range):
            for j, spot in enumerate(spot_range):
                bs = BlackScholes(
                    time_to_maturity=self.time_to_maturity,
                    strike=self.strike,
                    current_price=spot,
                    volatility=vol,
                    interest_rate=self.interest_rate
                )
                greeks = bs.calculate_greeks()
                call_greek[i, j] = greeks[f'call_{greek_name}']
                put_greek[i, j] = greeks[f'put_{greek_name}']
        fig_call, ax_call = plt.subplots(figsize=(16, 12))
        sns.heatmap(call_greek, xticklabels=np.round(spot_range, 2), 
                   yticklabels=np.round(vol_range, 2), annot=True, fmt=".3f", 
                   cmap=CUSTOM_CMAP, ax=ax_call, center=0, 
                   annot_kws={"size": 10}, cbar_kws={"shrink": 0.8})
        ax_call.set_title(f'Call {greek_name.capitalize()} Heatmap', fontsize=18, fontweight='bold', pad=20)
        ax_call.set_xlabel('Spot Price', fontsize=14, fontweight='bold', labelpad=10)
        ax_call.set_ylabel('Volatility', fontsize=14, fontweight='bold', labelpad=10)
        plt.setp(ax_call.get_xticklabels(), rotation=45, ha='right', fontsize=10)
        plt.setp(ax_call.get_yticklabels(), rotation=0, fontsize=10)
        plt.tight_layout()
        fig_put, ax_put = plt.subplots(figsize=(16, 12))
        sns.heatmap(put_greek, xticklabels=np.round(spot_range, 2), 
                   yticklabels=np.round(vol_range, 2), annot=True, fmt=".3f", 
                   cmap=CUSTOM_CMAP, ax=ax_put, center=0,
                   annot_kws={"size": 10}, cbar_kws={"shrink": 0.8})
        ax_put.set_title(f'Put {greek_name.capitalize()} Heatmap', fontsize=18, fontweight='bold', pad=20)
        ax_put.set_xlabel('Spot Price', fontsize=14, fontweight='bold', labelpad=10)
        ax_put.set_ylabel('Volatility', fontsize=14, fontweight='bold', labelpad=10)
        plt.setp(ax_put.get_xticklabels(), rotation=45, ha='right', fontsize=10)
        plt.setp(ax_put.get_yticklabels(), rotation=0, fontsize=10)
        plt.tight_layout()
        return fig_call, fig_put
