from pydantic import BaseModel, Field
from typing import Optional


class OptionPriceRequest(BaseModel):
    """Request model for option pricing"""
    spot_price: float = Field(..., gt=0, description="Current asset price")
    strike: float = Field(..., gt=0, description="Strike price")
    time_to_maturity: float = Field(..., gt=0, description="Time to maturity in years")
    volatility: float = Field(..., gt=0, description="Volatility (sigma)")
    interest_rate: float = Field(..., description="Risk-free interest rate")


class OptionPriceResponse(BaseModel):
    """Response model for option pricing"""
    call_price: float = Field(..., description="Call option price")
    put_price: float = Field(..., description="Put option price")


class GreeksRequest(BaseModel):
    """Request model for Greeks calculation"""
    spot_price: float = Field(..., gt=0, description="Current asset price")
    strike: float = Field(..., gt=0, description="Strike price")
    time_to_maturity: float = Field(..., gt=0, description="Time to maturity in years")
    volatility: float = Field(..., gt=0, description="Volatility (sigma)")
    interest_rate: float = Field(..., description="Risk-free interest rate")


class GreeksResponse(BaseModel):
    """Response model for Greeks"""
    call_delta: float
    put_delta: float
    call_gamma: float
    put_gamma: float
    call_theta: float
    put_theta: float
    call_vega: float
    put_vega: float
    call_rho: float
    put_rho: float


class PnLRequest(BaseModel):
    """Request model for P&L calculation"""
    spot_price: float = Field(..., gt=0, description="Current asset price")
    strike: float = Field(..., gt=0, description="Strike price")
    time_to_maturity: float = Field(..., gt=0, description="Time to maturity in years")
    volatility: float = Field(..., gt=0, description="Volatility (sigma)")
    interest_rate: float = Field(..., description="Risk-free interest rate")
    call_purchase_price: float = Field(0.0, ge=0, description="Call purchase price")
    put_purchase_price: float = Field(0.0, ge=0, description="Put purchase price")


class PnLResponse(BaseModel):
    """Response model for P&L"""
    call_price: float
    put_price: float
    call_pnl: float
    put_pnl: float


class ErrorResponse(BaseModel):
    """Error response model"""
    error: dict = Field(..., description="Error details")
