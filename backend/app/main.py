from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.app.models.QLearningTrader import QLearningTrader
from backend.app.models.RandomForestTrader import RandomForestTrader
import glob
from backend.app.utils.utility import compute_portvals  # Add this import at the top
import logging
import traceback
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
logging.basicConfig(level=logging.DEBUG)

# Store for trained models
trained_models: Dict[str, object] = {}

app = FastAPI(
    title="Trading Strategy API",
    description="API for training and testing trading strategies",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BaseTradingConfig(BaseModel):
    """Base configuration for trading parameters"""
    symbol: str
    start_date: datetime
    end_date: datetime
    start_val: float = 100000.0
    impact: float = 0.0
    commission: float = 0.0

class QLearningConfig(BaseTradingConfig):
    """Configuration for QLearning model parameters"""
    bins: int = 10
    alpha: float = 0.2
    gamma: float = 0.9
    rar: float = 0.98
    radr: float = 0.999
    dyna: int = 0

class DecisionTreeConfig(BaseTradingConfig):
    """Configuration for Decision Tree model parameters"""
    n_day_return: int = 5
    y_buy: float = 0.008
    y_sell: float = -0.008
    leaf_size: int = 6
    num_bags: int = 10

class ModelConfig(BaseModel):
    """Configuration for model selection and parameters"""
    model_type: str
    qlearning_config: Optional[QLearningConfig] = None
    decision_tree_config: Optional[DecisionTreeConfig] = None
    indicators_with_params: Optional[dict] = None  # New field for indicator configs

class ModelResponse(BaseModel):
    model_type: str
    parameters: Dict
    description: str

class TrainRequest(BaseModel):
    model_type: str
    qlearning_config: Optional[Dict[str, Any]] = None
    decision_tree_config: Optional[Dict[str, Any]] = None
    indicators_with_params: Dict[str, Dict[str, Any]]

class PlotRequest(BaseModel):
    model_type: str
    qlearning_config: Optional[Dict[str, Any]] = None
    decision_tree_config: Optional[Dict[str, Any]] = None
    indicators_with_params: Dict[str, Dict[str, Any]]

@app.get("/")
async def root():
    """Root endpoint returning API information"""
    return {
        "message": "Welcome to Trading Strategy API",
        "version": "1.0.0",
        "available_models": ["QLearningTrader", "RandomForestTrader"]
    }

@app.get("/api/models", response_model=List[ModelResponse])
async def list_models():
    """List available trading models and their parameters"""
    return [
        ModelResponse(
            model_type="QLearningTrader",
            parameters={
                "impact": "float (default: 0.0)",
                "commission": "float (default: 0.0)",
                "bins": "int (default: 10)",
                "alpha": "float (default: 0.2)",
                "gamma": "float (default: 0.9)",
                "rar": "float (default: 0.98)",
                "radr": "float (default: 0.999)",
                "dyna": "int (default: 0)"
            },
            description="Q-Learning based trading strategy using technical indicators"
        ),
        ModelResponse(
            model_type="RandomForestTrader",
            parameters={
                "leaf_size": "int (default: 1)"
            },
            description="Random Forest based trading strategy"
        )
    ]

# Helper function to select and instantiate the model
def get_model_and_config(request: TrainRequest):
    if request.model_type == "QLearningTrader":
        if not request.qlearning_config:
            raise HTTPException(status_code=400, detail="QLearning configuration is required")
        model = QLearningTrader(
            impact=request.qlearning_config["impact"],
            commission=request.qlearning_config["commission"],
            bins=request.qlearning_config["bins"],
            alpha=request.qlearning_config["alpha"],
            gamma=request.qlearning_config["gamma"],
            rar=request.qlearning_config["rar"],
            radr=request.qlearning_config["radr"],
            dyna=request.qlearning_config["dyna"]
        )
        base_config = request.qlearning_config
    elif request.model_type == "RandomForestTrader":
        if not request.decision_tree_config:
            raise HTTPException(status_code=400, detail="Random Forest configuration is required")
        model = RandomForestTrader(
            impact=request.decision_tree_config["impact"],
            commission=request.decision_tree_config["commission"],
            n_day_return=request.decision_tree_config["n_day_return"],
            y_buy=request.decision_tree_config["y_buy"],
            y_sell=request.decision_tree_config["y_sell"],
            leaf_size=request.decision_tree_config["leaf_size"],
            num_bags=request.decision_tree_config["num_bags"]
        )
        base_config = request.decision_tree_config
    else:
        raise HTTPException(status_code=400, detail="Invalid model type")
    return model, base_config


def handle_api_exception(e, endpoint_name):
    print(f"EXCEPTION in {endpoint_name}:", e, flush=True)
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/train")
async def train_model(request: TrainRequest):
    try:
        model, base_config = get_model_and_config(request)
        # Train the model
        model.train_model(
            symbol=base_config["symbol"],
            sd=base_config["start_date"],
            ed=base_config["end_date"],
            sv=base_config["start_val"],
            indicators_with_params=request.indicators_with_params
        )
        # Store the trained model
        trained_models[request.model_type] = model
        return {"message": f"Successfully trained {request.model_type}"}
    except Exception as e:
        handle_api_exception(e, "/api/train")
        return None


@app.post("/api/test")
async def test_model(request: TrainRequest):
    try:
        if request.model_type not in trained_models:
            raise HTTPException(status_code=400, detail=f"Model {request.model_type} has not been trained yet")
        model = trained_models[request.model_type]
        # Test the model
        base_config = request.qlearning_config if request.model_type == "QLearningTrader" else request.decision_tree_config
        trades = model.test_model(symbol=base_config["symbol"],
                                sd=base_config["start_date"],
                                ed=base_config["end_date"]
        )
        return {"trades": trades.to_dict()}
    except Exception as e:
        handle_api_exception(e, "/api/test")
        return None


@app.post("/api/plot")
async def plot_model(request: PlotRequest):
    try:
        # Get model trades using test_model endpoint
        trades_model = await test_model(request)
        # Get the base config values
        base_config = request.qlearning_config if request.model_type == "QLearningTrader" else request.decision_tree_config
        # Get benchmark trades
        trades_benchmark = trades_model.copy()
        trades_benchmark.iloc[:, :] = 0.0
        trades_benchmark.iloc[0, 0] = 1000
        # Compute portfolio value
        portvals_benchmark = compute_portvals(trades_benchmark,
                                              start_val=base_config["start_val"],
                                              commission=base_config["commission"],
                                              impact=base_config["impact"],
                                              symbol=base_config["symbol"])
        portvals_benchmark_normalized = portvals_benchmark / portvals_benchmark.iloc[0]
        portvals_model = compute_portvals(trades_model,
                                        start_val=base_config["start_val"],
                                        commission=base_config["commission"],
                                        impact=base_config["impact"],
                                        symbol=base_config["symbol"])
        portvals_model_normalized = portvals_model / portvals_model.iloc[0]
        # Convert trades to plot data
        plot_data = {
            "dates": trades_model.index.tolist(),
            "model_values": portvals_model_normalized[portvals_model_normalized.columns[0]].tolist(),
            "benchmark_values": portvals_benchmark_normalized[portvals_benchmark_normalized.columns[0]].tolist(),
            "symbol": base_config["symbol"]
        }
        return plot_data
    except Exception as e:
        handle_api_exception(e, "/api/plot")
        return None


@app.get("/api/symbols")
async def get_symbols():
    """
    Return a sorted list of all available stock symbols (from CSV files in data/).
    """
    try:
        csv_files = glob.glob("data/**/*.csv", recursive=True)
        symbols = sorted({os.path.splitext(os.path.basename(f))[0] for f in csv_files})
        return {"symbols": symbols}
    except Exception as e:
        handle_api_exception(e, "/api/symbols")
        return None