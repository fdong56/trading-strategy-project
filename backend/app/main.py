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


@app.post("/api/train")
async def train_model(config: ModelConfig):
    try:
        model, base_config = get_model_and_config(config)
        # Train the model
        model.train_model(
            symbol=base_config.symbol,
            sd=base_config.start_date,
            ed=base_config.end_date,
            sv=base_config.start_val,
            indicators_with_params=config.indicators_with_params
        )
        # Store the trained model
        trained_models[config.model_type] = model
        return {"message": f"Successfully trained {config.model_type}"}
    except Exception as e:
        handle_api_exception(e, "/api/train")
        return None


@app.post("/api/test")
async def test_model(config: ModelConfig):
    try:
        if config.model_type not in trained_models:
            raise HTTPException(status_code=400, detail=f"Model {config.model_type} has not been trained yet")
        model = trained_models[config.model_type]
        # Test the model
        base_config = config.qlearning_config if config.model_type == "QLearningTrader" else config.decision_tree_config
        trades = model.test_model(symbol=base_config.symbol, sd=base_config.start_date, ed=base_config.end_date)
        return trades
    except Exception as e:
        handle_api_exception(e, "/api/test")
        return None


@app.post("/api/plot")
async def plot_model(config: ModelConfig):
    try:
        # Get model trades using test_model endpoint
        trades_model = await test_model(config)
        # Get the base config values
        base_config = config.qlearning_config if config.model_type == "QLearningTrader" else config.decision_tree_config
        # Get benchmark trades
        trades_benchmark = trades_model.copy()
        trades_benchmark.iloc[:, :] = 0.0
        trades_benchmark.iloc[0, 0] = 1000
        # Compute portfolio value
        portvals_benchmark = compute_portvals(trades_benchmark,
                                              start_val=base_config.start_val,
                                              commission=base_config.commission,
                                              impact=base_config.impact,
                                              symbol=base_config.symbol)
        portvals_benchmark_normalized = portvals_benchmark / portvals_benchmark.iloc[0]

        portvals_model = compute_portvals(trades_model,
                                        start_val=base_config.start_val,
                                        commission=base_config.commission,
                                        impact=base_config.impact,
                                        symbol=base_config.symbol)
        portvals_model_normalized = portvals_model / portvals_model.iloc[0]

        # Convert trades to plot data
        plot_data = {
            "dates": trades_model.index.tolist(),
            "model_values": portvals_model_normalized[portvals_model_normalized.columns[0]].tolist(),
            "benchmark_values": portvals_benchmark_normalized[portvals_benchmark_normalized.columns[0]].tolist(),
            "symbol": base_config.symbol
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

@app.get("/api/price")
async def get_price_data(symbol: str, start_date: str, end_date: str):
    """
    Return price data for a specified symbol and date range.
    """
    try:
        file_path = f"data/{symbol}.csv"
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")
        
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'])
        mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
        filtered_df = df.loc[mask].sort_values('Date')
        
        return {
            "dates": filtered_df['Date'].dt.strftime('%Y-%m-%d').tolist(),
            "prices": filtered_df['Close'].tolist()
        }
    except Exception as e:
        handle_api_exception(e, "/api/price")
        return None



# Helper function to select and instantiate the model
def get_model_and_config(config: ModelConfig):
    if config.model_type == "QLearningTrader":
        if not config.qlearning_config:
            raise HTTPException(status_code=400, detail="QLearning configuration is required")
        base_config = config.qlearning_config
        model = QLearningTrader(
            impact=base_config.impact,
            commission=base_config.commission,
            bins=base_config.bins,
            alpha=base_config.alpha,
            gamma=base_config.gamma,
            rar=base_config.rar,
            radr=base_config.radr,
            dyna=base_config.dyna
        )
    elif config.model_type == "RandomForestTrader":
        if not config.decision_tree_config:
            raise HTTPException(status_code=400, detail="Random Forest configuration is required")
        base_config = config.decision_tree_config
        model = RandomForestTrader(
            impact=base_config.impact,
            commission=base_config.commission,
            n_day_return=base_config.n_day_return,
            y_buy=base_config.y_buy,
            y_sell=base_config.y_sell,
            leaf_size=base_config.leaf_size,
            num_bags=base_config.num_bags
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid model type")
    return model, base_config


def handle_api_exception(e, endpoint_name):
    print(f"EXCEPTION in {endpoint_name}:", e, flush=True)
    traceback.print_exc()
    raise HTTPException(status_code=500, detail=str(e))