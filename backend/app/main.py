from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
import sys
import os
from utils import utility
from models.QLearningTrader import QLearningTrader
from models.DecisionTreeTrader import DecisionTreeTrader

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
        "available_models": ["QLearningTrader", "DecisionTreeTrader"]
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
            model_type="DecisionTreeTrader",
            parameters={
                "leaf_size": "int (default: 1)"
            },
            description="Decision Tree based trading strategy"
        )
    ]

@app.post("/api/train")
async def train_model(config: ModelConfig):
    """Train a trading model with specified parameters and indicator configuration"""
    try:
        if config.model_type == "QLearningTrader":
            if not config.qlearning_config:
                raise HTTPException(status_code=400, detail="QLearning configuration is required")
            model = QLearningTrader(
                impact=config.qlearning_config.impact,
                commission=config.qlearning_config.commission,
                bins=config.qlearning_config.bins,
                alpha=config.qlearning_config.alpha,
                gamma=config.qlearning_config.gamma,
                rar=config.qlearning_config.rar,
                radr=config.qlearning_config.radr,
                dyna=config.qlearning_config.dyna
            )
            # Train the model
            model.train_model(
                symbol=config.qlearning_config.symbol,
                sd=config.qlearning_config.start_date,
                ed=config.qlearning_config.end_date,
                sv=config.qlearning_config.start_val,
                indicators_with_params=config.indicators_with_params
            )
            # Store the trained model
            trained_models[config.model_type] = model
        elif config.model_type == "DecisionTreeTrader":
            if not config.decision_tree_config:
                raise HTTPException(status_code=400, detail="Decision Tree configuration is required")
            model = DecisionTreeTrader(
                impact=config.decision_tree_config.impact,
                commission=config.decision_tree_config.commission,
                n_day_return=config.decision_tree_config.n_day_return,
                y_buy=config.decision_tree_config.y_buy,
                y_sell=config.decision_tree_config.y_sell,
                leaf_size=config.decision_tree_config.leaf_size,
                num_bags=config.decision_tree_config.num_bags
            )
            # Train the model
            model.train_model(
                symbol=config.decision_tree_config.symbol,
                sd=config.decision_tree_config.start_date,
                ed=config.decision_tree_config.end_date,
                sv=config.decision_tree_config.start_val,
                indicators_with_params=config.indicators_with_params
            )
            # Store the trained model
            trained_models[config.model_type] = model
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")

        return {"message": f"Successfully trained {config.model_type}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test")
async def test_model(config: ModelConfig):
    """Test a trained model with specified parameters (uses indicators from training)"""
    try:
        # Check if the model is trained
        if config.model_type not in trained_models:
            raise HTTPException(status_code=400, detail=f"Model {config.model_type} has not been trained yet")

        model = trained_models[config.model_type]

        if config.model_type == "QLearningTrader":
            if not config.qlearning_config:
                raise HTTPException(status_code=400, detail="QLearning configuration is required")
            # Test the model (uses indicators from training)
            trades = model.test_model(
                symbol=config.qlearning_config.symbol,
                sd=config.qlearning_config.start_date,
                ed=config.qlearning_config.end_date,
                sv=config.qlearning_config.start_val
            )
        elif config.model_type == "DecisionTreeTrader":
            if not config.decision_tree_config:
                raise HTTPException(status_code=400, detail="Decision Tree configuration is required")
            # Test the model (uses indicators from training)
            trades = model.test_model(
                symbol=config.decision_tree_config.symbol,
                sd=config.decision_tree_config.start_date,
                ed=config.decision_tree_config.end_date,
                sv=config.decision_tree_config.start_val
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid model type")

        # Convert trades DataFrame to dict for JSON response
        trades_dict = trades.to_dict(orient='records')
        
        return {
            "message": f"Successfully tested {config.model_type}",
            "trades": trades_dict
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 