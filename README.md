# Trading Strategy Project

A comprehensive web application for developing, training, and testing machine learning-based trading strategies. This project combines a FastAPI backend with a React frontend to provide an interactive platform for algorithmic trading research.

A live demo of this application is available online:

- **Frontend Application**: [https://trading-frontend-g1xl.onrender.com/](https://trading-frontend-g1xl.onrender.com/)
- **Backend API**: [https://trading-backend-32vw.onrender.com/](https://trading-backend-32vw.onrender.com/)

**Important Note**: The demo is hosted on Render's free tier, which means both applications will become inactive after periods of inactivity. To ensure optimal functionality:

1. First visit the backend API to activate the server
2. Then access the frontend application

This activation process ensures both services are running before attempting to use the trading strategy features.

## Features

### Trading Models
- **QLearningTrader**: Reinforcement learning-based trading strategy using Q-Learning algorithm
- **RandomForestTrader**: Ensemble learning approach using bagged decision trees
- **Customizable Parameters**: Fine-tune model hyperparameters for optimal performance

### Technical Indicators
- **Gold Cross**: Moving average crossover strategy
- **Bollinger Bands %B**: Mean reversion indicator
- **Rate of Change (ROC)**: Momentum indicator
- **MACD**: Trend-following momentum indicator
- **RSI**: Relative Strength Index for overbought/oversold conditions

### Interactive Features
- **Real-time Visualization**: Chart.js-powered performance charts
- **Portfolio Comparison**: Model performance vs benchmark analysis
- **Historical Data**: Extensive S&P 500 stock dataset (2008-2012)
- **Parameter Tuning**: Dynamic form controls for strategy optimization

## Architecture

```
trading-strategy-project/
├── backend/                 # FastAPI backend server
│   ├── app/
│   │   ├── main.py         # API endpoints and server configuration
│   │   ├── models/         # Trading strategy implementations
│   │   │   ├── QLearningTrader.py
│   │   │   ├── RandomForestTrader.py
│   │   │   ├── QLearner.py
│   │   │   ├── TreeModel.py
│   │   │   └── BagEnsembleModel.py
│   │   └── utils/          # Utility functions
│   │       ├── indicators.py
│   │       └── utility.py
│   ├── data/               # Historical stock data (S&P 500)
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Container configuration
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── StockSection.jsx
│   │   │   ├── IndicatorsSection.jsx
│   │   │   ├── ModelSection.jsx
│   │   │   └── ResultSection.jsx
│   │   ├── App.jsx        # Main application component
│   │   └── main.jsx       # Application entry point
│   ├── package.json       # Node.js dependencies
│   └── vite.config.js     # Build configuration
└── environment.yml        # Conda environment setup
```

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework for building APIs
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **SciPy**: Scientific computing
- **Uvicorn**: ASGI server for FastAPI

### Frontend
- **React 19**: Modern JavaScript library for building user interfaces
- **Vite**: Fast build tool and development server
- **Chart.js**: Interactive charts and visualizations
- **React Chart.js 2**: React wrapper for Chart.js

### Data
- **Historical Stock Data**: S&P 500 constituents (2008-2012)
- **CSV Format**: Standard financial data format
- **Real-time Processing**: On-demand data loading and analysis

## Installation

### Prerequisites
- Python 3.9+
- Node.js 16+
- npm or yarn

### Option 1: Using Conda (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd trading-strategy-project
   ```

2. **Create and activate conda environment**
   ```bash
   conda env create -f environment.yml
   conda activate strategy_env
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Option 2: Manual Setup

1. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

### Development Mode

1. **Start the Backend Server**
   ```bash
   # From the project root directory
   uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000 --log-level debug
   ```

2. **Start the Frontend Development Server**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Usage Guide

### 1. Stock Selection
- Choose from available S&P 500 stocks in the dropdown
- Set training and testing date ranges
- Configure initial portfolio value and trading costs

### 2. Technical Indicators
- Select from available technical indicators
- Configure indicator-specific parameters
- Combine multiple indicators for enhanced signals

### 3. Model Configuration
- Choose between QLearningTrader and RandomForestTrader
- Adjust model-specific hyperparameters
- Set trading thresholds and learning rates

### 4. Training and Testing
- **Train Model**: Click "Train Model" to train the selected strategy
- **Test Model**: Click "Test Model" to evaluate performance
- **View Results**: Interactive charts show portfolio performance vs benchmark

## API Endpoints

### Core Endpoints
- `GET /`: API information and available models
- `POST /api/train`: Train a trading model
- `POST /api/test`: Test a trained model
- `POST /api/plot`: Generate performance visualization data

### Data Endpoints
- `GET /api/symbols`: List available stock symbols
- `GET /api/price`: Retrieve historical price data

### Model Configuration
```json
{
  "model_type": "RandomForestTrader",
  "qlearning_config": {
    "symbol": "JPM",
    "start_date": "2008-01-01",
    "end_date": "2009-01-01",
    "start_val": 100000,
    "bins": 10,
    "alpha": 0.2,
    "gamma": 0.9
  },
  "indicators_with_params": {
    "rsi": {"lookback": 14},
    "macd": {"short_period": 12, "long_period": 26}
  }
}
```

## Trading Strategies

### QLearningTrader
- **Algorithm**: Q-Learning reinforcement learning
- **Features**: State discretization, reward shaping, exploration vs exploitation
- **Parameters**: Learning rate (alpha), discount factor (gamma), random action rate (rar)

### RandomForestTrader
- **Algorithm**: Bagged ensemble of decision trees
- **Features**: Feature engineering, ensemble voting, overfitting prevention
- **Parameters**: Leaf size, number of bags, buy/sell thresholds

## Testing and Validation

### Performance Metrics
- Portfolio value over time
- Sharpe ratio calculation
- Maximum drawdown analysis
- Benchmark comparison (buy-and-hold strategy)

### Data Validation
- Historical data integrity checks
- Parameter boundary validation
- Model convergence verification

## Security Considerations

- CORS configuration for cross-origin requests
- Input validation and sanitization
- Error handling and logging
- Rate limiting (recommended for production)

---

**Note**: This application is for educational and research purposes. Trading strategies should be thoroughly tested before use in live markets.