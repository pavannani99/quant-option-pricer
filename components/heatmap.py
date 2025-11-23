import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple
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
class HeatmapGenerator:
    def __init__(self, time_to_maturity, strike, interest_rate):
        self.time_to_maturity = time_to_maturity
        self.strike = strike
        self.interest_rate = interest_rate
    def generate_price_heatmap(self, spot_range, vol_range):
        call_prices = np.zeros((len(vol_range), len(spot_range)))
        put_prices = np.zeros((len(vol_range), len(spot_range)))
        for i, vol in enumerate(vol_range):
            for j, spot in enumerate(spot_range):
                bs_temp = BlackScholes(
                    time_to_maturity=self.time_to_maturity,
                    strike=self.strike,
                    current_price=spot,
                    volatility=vol,
                    interest_rate=self.interest_rate
                )
                bs_temp.calculate_prices()
                call_prices[i, j] = bs_temp.call_price
                put_prices[i, j] = bs_temp.put_price
        fig_call, ax_call = plt.subplots(figsize=(16, 12))
        sns.heatmap(call_prices, 
                   xticklabels=[f'{x:.1f}' for x in spot_range], 
                   yticklabels=[f'{y:.3f}' for y in vol_range], 
                   annot=True, 
                   fmt=".2f", 
                   cmap=CUSTOM_CMAP, 
                   ax=ax_call,
                   cbar_kws={'label': 'Option Price ($)', 'shrink': 0.8},
                   annot_kws={'size': 10})
        ax_call.set_title('CALL Option Price', fontsize=18, fontweight='bold', pad=20)
        ax_call.set_xlabel('Spot Price ($)', fontsize=14, fontweight='bold', labelpad=10)
        ax_call.set_ylabel('Volatility (σ)', fontsize=14, fontweight='bold', labelpad=10)
        plt.setp(ax_call.get_xticklabels(), rotation=45, ha='right', fontsize=10)
        plt.setp(ax_call.get_yticklabels(), rotation=0, fontsize=10)
        plt.tight_layout()
        fig_put, ax_put = plt.subplots(figsize=(16, 12))
        sns.heatmap(put_prices, 
                   xticklabels=[f'{x:.1f}' for x in spot_range], 
                   yticklabels=[f'{y:.3f}' for y in vol_range], 
                   annot=True, 
                   fmt=".2f", 
                   cmap=CUSTOM_CMAP, 
                   ax=ax_put,
                   cbar_kws={'label': 'Option Price ($)', 'shrink': 0.8},
                   annot_kws={'size': 10})
        ax_put.set_title('PUT Option Price', fontsize=18, fontweight='bold', pad=20)
        ax_put.set_xlabel('Spot Price ($)', fontsize=14, fontweight='bold', labelpad=10)
        ax_put.set_ylabel('Volatility (σ)', fontsize=14, fontweight='bold', labelpad=10)
        plt.setp(ax_put.get_xticklabels(), rotation=45, ha='right', fontsize=10)
        plt.setp(ax_put.get_yticklabels(), rotation=0, fontsize=10)
        plt.tight_layout()
        return fig_call, fig_put
    def generate_pnl_heatmap(self, spot_range, vol_range, call_purchase_price=0.0, put_purchase_price=0.0):
        call_pnl = np.zeros((len(vol_range), len(spot_range)))
        put_pnl = np.zeros((len(vol_range), len(spot_range)))
        for i, vol in enumerate(vol_range):
            for j, spot in enumerate(spot_range):
                bs_temp = BlackScholes(
                    time_to_maturity=self.time_to_maturity,
                    strike=self.strike,
                    current_price=spot,
                    volatility=vol,
                    interest_rate=self.interest_rate
                )
                bs_temp.calculate_prices()
                call_pnl[i, j] = bs_temp.call_price - call_purchase_price
                put_pnl[i, j] = bs_temp.put_price - put_purchase_price
        fig_call, ax_call = plt.subplots(figsize=(16, 12))
        sns.heatmap(call_pnl, 
                   xticklabels=[f'{x:.1f}' for x in spot_range], 
                   yticklabels=[f'{y:.3f}' for y in vol_range], 
                   annot=True, 
                   fmt=".2f", 
                   cmap=CUSTOM_CMAP, 
                   center=0, 
                   ax=ax_call,
                   cbar_kws={'label': 'P&L ($)', 'shrink': 0.8},
                   annot_kws={'size': 10})
        ax_call.set_title('CALL P&L (Green=Profit, Red=Loss)', fontsize=18, fontweight='bold', pad=20)
        ax_call.set_xlabel('Spot Price ($)', fontsize=14, fontweight='bold', labelpad=10)
        ax_call.set_ylabel('Volatility (σ)', fontsize=14, fontweight='bold', labelpad=10)
        plt.setp(ax_call.get_xticklabels(), rotation=45, ha='right', fontsize=10)
        plt.setp(ax_call.get_yticklabels(), rotation=0, fontsize=10)
        plt.tight_layout()
        fig_put, ax_put = plt.subplots(figsize=(16, 12))
        sns.heatmap(put_pnl, 
                   xticklabels=[f'{x:.1f}' for x in spot_range], 
                   yticklabels=[f'{y:.3f}' for y in vol_range], 
                   annot=True, 
                   fmt=".2f", 
                   cmap=CUSTOM_CMAP, 
                   center=0, 
                   ax=ax_put,
                   cbar_kws={'label': 'P&L ($)', 'shrink': 0.8},
                   annot_kws={'size': 10})
        ax_put.set_title('PUT P&L (Green=Profit, Red=Loss)', fontsize=18, fontweight='bold', pad=20)
        ax_put.set_xlabel('Spot Price ($)', fontsize=14, fontweight='bold', labelpad=10)
        ax_put.set_ylabel('Volatility (σ)', fontsize=14, fontweight='bold', labelpad=10)
        plt.setp(ax_put.get_xticklabels(), rotation=45, ha='right', fontsize=10)
        plt.setp(ax_put.get_yticklabels(), rotation=0, fontsize=10)
        plt.tight_layout()
        return fig_call, fig_put
