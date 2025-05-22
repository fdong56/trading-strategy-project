from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Any
import sys
import os
from models.QLearningTrader import QLearningTrader
from models.DecisionTreeTrader import DecisionTreeTrader
from utils import utility

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

app = FastAPI(title="Trading Strategy API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TradingRequest(BaseModel):
    model_type: str  # "qlearning" or "decisiontree"
    symbol: str
    start_date: datetime
    end_date: datetime
    test_start_date: datetime
    test_end_date: datetime
    parameters: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "Welcome to Trading Strategy API"}

@app.get("/api/models")
async def get_available_models():
    return {
        "models": [
            {
                "name": "QLearningTrader",
                "parameters": {
                    "impact": {"type": "float", "default": 0.0},
                    "commission": {"type": "float", "default": 0.0},
                    "bins": {"type": "int", "default": 10},
                    "alpha": {"type": "float", "default": 0.2},
                    "gamma": {"type": "float", "default": 0.9}
                }
            },
            {
                "name": "DecisionTreeTrader",
                "parameters": {
                    "impact": {"type": "float", "default": 0.0},
                    "commission": {"type": "float", "default": 0.0},
                    "n_day_return": {"type": "int", "default": 5},
                    "y_buy": {"type": "float", "default": 0.008},
                    "y_sell": {"type": "float", "default": -0.008},
                    "leaf_size": {"type": "int", "default": 6},
                    "num_bags": {"type": "int", "default": 10}
                }
            }
        ]
    }

@app.post("/api/trade")
async def execute_trade(request: TradingRequest):
    try:
        # Create a model instance
        if request.model_type.lower() == "qlearning":
            model = QLearningTrader(**request.parameters)
        elif request.model_type.lower() == "decisiontree":
            model = DecisionTreeTrader(**request.parameters)
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")

        # Train the model
        model.train_model(
            symbol=request.symbol,
            sd=request.start_date,
            ed=request.end_date
        )

        # Test the model
        trades = model.test_model(
            symbol=request.symbol,
            sd=request.test_start_date,
            ed=request.test_end_date
        )

        # Calculate performance metrics
        portvals = utility.compute_portvals(trades, start_val=100000,
                                            commission=request.parameters.get('commission', 0.0),
                                            impact=request.parameters.get('impact', 0.0),
                                            symbol=request.symbol)
        
        # Calculate cumulative return
        cum_ret = portvals.iloc[-1] / portvals.iloc[0] - 1

        return {
            "status": "success",
            "trades": trades.to_dict(),
            "performance": {
                "cumulative_return": float(cum_ret),
                "portfolio_values": portvals.to_dict()
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 