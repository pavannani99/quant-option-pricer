from numpy import exp, sqrt, log
from scipy.stats import norm


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

    def run(self):
        """Legacy method for backward compatibility"""
        self.calculate_prices()
        self.calculate_greeks()

    def calculate_prices(self):
        """Calculate call and put option prices"""
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
        
        return call_price, put_price

    def calculate_greeks(self):
        """Calculate all Greeks: Delta, Gamma, Theta, Vega, Rho"""
        # Ensure prices are calculated first
        if not hasattr(self, 'd1'):
            self.calculate_prices()
            
        time_to_maturity = self.time_to_maturity
        strike = self.strike
        current_price = self.current_price
        volatility = self.volatility
        interest_rate = self.interest_rate
        d1 = self.d1
        d2 = self.d2

        # Delta
        self.call_delta = norm.cdf(d1)
        self.put_delta = self.call_delta - 1

        # Gamma (same for calls and puts)
        self.call_gamma = norm.pdf(d1) / (current_price * volatility * sqrt(time_to_maturity))
        self.put_gamma = self.call_gamma

        # Theta
        theta_common = -(current_price * norm.pdf(d1) * volatility) / (2 * sqrt(time_to_maturity))
        self.call_theta = (theta_common - interest_rate * strike * exp(-interest_rate * time_to_maturity) * norm.cdf(d2)) / 365
        self.put_theta = (theta_common + interest_rate * strike * exp(-interest_rate * time_to_maturity) * norm.cdf(-d2)) / 365

        # Vega (same for calls and puts)
        self.call_vega = current_price * norm.pdf(d1) * sqrt(time_to_maturity) / 100
        self.put_vega = self.call_vega

        # Rho
        self.call_rho = strike * time_to_maturity * exp(-interest_rate * time_to_maturity) * norm.cdf(d2) / 100
        self.put_rho = -strike * time_to_maturity * exp(-interest_rate * time_to_maturity) * norm.cdf(-d2) / 100

        return {
            'call_delta': self.call_delta,
            'put_delta': self.put_delta,
            'call_gamma': self.call_gamma,
            'put_gamma': self.put_gamma,
            'call_theta': self.call_theta,
            'put_theta': self.put_theta,
            'call_vega': self.call_vega,
            'put_vega': self.put_vega,
            'call_rho': self.call_rho,
            'put_rho': self.put_rho
        }

    def calculate_pnl(self, call_purchase_price: float = 0.0, put_purchase_price: float = 0.0):
        """Calculate P&L given purchase prices"""
        # Ensure prices are calculated
        if not hasattr(self, 'call_price'):
            self.calculate_prices()
            
        call_pnl = self.call_price - call_purchase_price
        put_pnl = self.put_price - put_purchase_price
        
        return call_pnl, put_pnl


if __name__ == "__main__":
    time_to_maturity = 2
    strike = 90
    current_price = 100
    volatility = 0.2
    interest_rate = 0.05

    # Black Scholes
    BS = BlackScholes(
        time_to_maturity=time_to_maturity,
        strike=strike,
        current_price=current_price,
        volatility=volatility,
        interest_rate=interest_rate)
    BS.run()
