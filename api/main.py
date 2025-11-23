from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from BlackScholes import BlackScholes
from api.models import (
    OptionPriceRequest, OptionPriceResponse,
    GreeksRequest, GreeksResponse,
    PnLRequest, PnLResponse,
    ErrorResponse
)

app = FastAPI(
    title="Black-Scholes Options Pricing API",
    description="REST API for Black-Scholes option pricing, Greeks calculation, and P&L analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Black-Scholes Options Pricing API",
        "version": "1.0.0",
        "endpoints": {
            "/price": "Calculate option prices",
            "/greeks": "Calculate option Greeks",
            "/pnl": "Calculate P&L",
            "/docs": "API documentation"
        }
    }


@app.post("/price", response_model=OptionPriceResponse)
def calculate_price(request: OptionPriceRequest):
    """Calculate call and put option prices"""
    try:
        bs = BlackScholes(
            time_to_maturity=request.time_to_maturity,
            strike=request.strike,
            current_price=request.spot_price,
            volatility=request.volatility,
            interest_rate=request.interest_rate
        )
        call_price, put_price = bs.calculate_prices()
        
        return OptionPriceResponse(
            call_price=call_price,
            put_price=put_price
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/greeks", response_model=GreeksResponse)
def calculate_greeks(request: GreeksRequest):
    """Calculate option Greeks"""
    try:
        bs = BlackScholes(
            time_to_maturity=request.time_to_maturity,
            strike=request.strike,
            current_price=request.spot_price,
            volatility=request.volatility,
            interest_rate=request.interest_rate
        )
        greeks = bs.calculate_greeks()
        
        return GreeksResponse(**greeks)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/pnl", response_model=PnLResponse)
def calculate_pnl(request: PnLRequest):
    """Calculate option prices and P&L"""
    try:
        bs = BlackScholes(
            time_to_maturity=request.time_to_maturity,
            strike=request.strike,
            current_price=request.spot_price,
            volatility=request.volatility,
            interest_rate=request.interest_rate
        )
        call_price, put_price = bs.calculate_prices()
        call_pnl, put_pnl = bs.calculate_pnl(
            request.call_purchase_price,
            request.put_purchase_price
        )
        
        return PnLResponse(
            call_price=call_price,
            put_price=put_price,
            call_pnl=call_pnl,
            put_pnl=put_pnl
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
