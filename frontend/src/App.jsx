import React, { useState } from 'react';
import './App.css';
import StockSection from './components/StockSection';
import IndicatorsSection from './components/IndicatorsSection';
import ModelSection from './components/ModelSection';
import ResultSection from './components/ResultSection';

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// Supported indicators and their parameter schemas
const INDICATOR_OPTIONS = [
  {
    key: 'gold cross',
    label: 'Gold Cross',
    params: [
      { key: 'lookback_1', label: 'Short SMA Window', type: 'number', placeholder: 'e.g. 10' },
      { key: 'lookback_2', label: 'Long SMA Window', type: 'number', placeholder: 'e.g. 15' },
    ],
  },
  {
    key: 'bbp',
    label: 'Bollinger Bands %B',
    params: [
      { key: 'lookback', label: 'Lookback', type: 'number', placeholder: 'e.g. 20' },
    ],
  },
  {
    key: 'roc',
    label: 'Rate of Change (ROC)',
    params: [
      { key: 'lookback', label: 'Lookback', type: 'number', placeholder: 'e.g. 10' },
    ],
  },
  {
    key: 'macd',
    label: 'MACD',
    params: [
      { key: 'short_period', label: 'Short Period', type: 'number', placeholder: 'e.g. 12' },
      { key: 'long_period', label: 'Long Period', type: 'number', placeholder: 'e.g. 26' },
      { key: 'signal_period', label: 'Signal Period', type: 'number', placeholder: 'e.g. 9' },
    ],
  },
  {
    key: 'rsi',
    label: 'RSI',
    params: [
      { key: 'lookback', label: 'Lookback', type: 'number', placeholder: 'e.g. 10' },
    ],
  },
];

const MODEL_CONFIGS = {
  RandomForestTrader: [
    { key: 'n_day_return', label: 'N day return', type: 'number', placeholder: 'e.g. 5' },
    { key: 'y_buy', label: 'Y Buy', type: 'number', placeholder: 'e.g. 0.008', step: '0.001' },
    { key: 'y_sell', label: 'Y Sell', type: 'number', placeholder: 'e.g. -0.008', step: '0.001' },
    { key: 'leaf_size', label: 'Leaf size', type: 'number', placeholder: 'e.g. 6' },
    { key: 'num_bags', label: 'Num of bags', type: 'number', placeholder: 'e.g. 10' },
  ],
  QLearningTrader: [
    { key: 'bins', label: 'Bins', type: 'number', placeholder: 'e.g. 10' },
    { key: 'alpha', label: 'Alpha', type: 'number', placeholder: 'e.g. 0.2', step: '0.01' },
    { key: 'gamma', label: 'Gamma', type: 'number', placeholder: 'e.g. 0.9', step: '0.01' },
    { key: 'rar', label: 'Rar', type: 'number', placeholder: 'e.g. 0.98', step: '0.01' },
    { key: 'radr', label: 'Radr', type: 'number', placeholder: 'e.g. 0.999', step: '0.001' },
    { key: 'dyna', label: 'Dyna', type: 'number', placeholder: 'e.g. 0' },
  ],
};

function App() {
  const [selectedModel, setSelectedModel] = useState('RandomForestTrader');
  const [config, setConfig] = useState({
    symbol: 'JPM',
    start_date: '2008-01-01',
    end_date: '2009-01-01',
    test_start_date: '2009-01-01',
    test_end_date: '2010-01-01',
    impact: '0.005',
    commission: '9.95',
    start_val: '100000',
    n_day_return: '5',
    y_buy: '0.008',
    y_sell: '-0.008',
    leaf_size: '6',
    num_bags: '10',
  });
  const [selectedIndicators, setSelectedIndicators] = useState([
    'macd', 'rsi', 'bbp'
  ]);
  const [indicatorParams, setIndicatorParams] = useState({
    macd: {
      short_period: '12',
      long_period: '26',
      signal_period: '9'
    },
    rsi: {
      lookback: '14'
    },
    bbp: {
      lookback: '20'
    }
  });
  const [trainPlotData, setTrainPlotData] = useState(null);
  const [testPlotData, setTestPlotData] = useState(null);
  
  // Handle model config changes
  const handleConfigChange = (field, value) => {
    setConfig(prev => ({ ...prev, [field]: value }));
  };

  // Handle model selection
  const handleModelChange = (e) => {
    const model = e.target.value;
    setSelectedModel(model);
    if (MODEL_CONFIGS[model]) {
      const newFields = {};
      MODEL_CONFIGS[model].forEach(param => {
        newFields[param.key] = '';
      });
      setConfig(prev => ({ ...prev, ...newFields }));
    }
  };

  // Handle indicator selection
  const handleIndicatorSelect = (idx, value) => {
    const newSelected = [...selectedIndicators];
    newSelected[idx] = value;
    setSelectedIndicators(newSelected);
    // Reset params for this indicator
    setIndicatorParams(prev => {
      const newParams = { ...prev };
      newParams[value] = {};
      return newParams;
    });
  };

  // Handle indicator parameter change
  const handleIndicatorParamChange = (indicator, paramKey, value) => {
    setIndicatorParams(prev => ({
      ...prev,
      [indicator]: {
        ...prev[indicator],
        [paramKey]: value
      }
    }));
  };

  // Build indicators_with_params for API
  const buildIndicatorsWithParams = () => {
    const result = {};
    selectedIndicators.forEach(ind => {
      if (ind) {
        result[ind] = { ...indicatorParams[ind] };
      }
    });
    return result;
  };

  // Helper to fetch plot data and set state
  async function fetchAndSetPlotData(formattedConfig, indicators_with_params, setPlotData) {
    const plotResponse = await fetch('http://localhost:8000/api/plot', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model_type: selectedModel,
        qlearning_config: selectedModel === 'QLearningTrader' ? formattedConfig : null,
        decision_tree_config: selectedModel === 'RandomForestTrader' ? formattedConfig : null,
        indicators_with_params
      })
    });

    if (!plotResponse.ok) {
      const errorData = await plotResponse.json();
      if (errorData.detail) {
        if (Array.isArray(errorData.detail)) {
          const errorMessages = errorData.detail.map(err => 
            `${err.loc[err.loc.length - 1]}: ${err.msg}`
          ).join('\n');
          throw new Error(`Validation errors:\n${errorMessages}`);
        } else {
          throw new Error(errorData.detail);
        }
      }
      throw new Error('Failed to get plot data');
    }

    const plotResult = await plotResponse.json();
    setPlotData(plotResult);
  }

  const handleTrain = async (e) => {
    e.preventDefault();
    const indicators_with_params = buildIndicatorsWithParams();
    
    // Create a copy of config with properly formatted dates
    const formattedConfig = {
      ...config,
      start_date: new Date(config.start_date).toISOString(),
      end_date: new Date(config.end_date).toISOString()
    };
    
    try {
      // Train the model
      const trainResponse = await fetch('http://localhost:8000/api/train', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model_type: selectedModel,
          qlearning_config: selectedModel === 'QLearningTrader' ? formattedConfig : null,
          decision_tree_config: selectedModel === 'RandomForestTrader' ? formattedConfig : null,
          indicators_with_params
        })
      });
      
      if (!trainResponse.ok) {
        const errorData = await trainResponse.json();
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            const errorMessages = errorData.detail.map(err => 
              `${err.loc[err.loc.length - 1]}: ${err.msg}`
            ).join('\n');
            throw new Error(`Validation errors:\n${errorMessages}`);
          } else {
            throw new Error(errorData.detail);
          }
        }
        throw new Error('Training failed');
      }

      // Get plot data for training
      await fetchAndSetPlotData(formattedConfig, indicators_with_params, setTrainPlotData);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleTest = async (e) => {
    e.preventDefault();
    const indicators_with_params = buildIndicatorsWithParams();
    
    // Create a copy of config with test dates
    const formattedConfig = {
      ...config,
      start_date: new Date(config.test_start_date).toISOString(),
      end_date: new Date(config.test_end_date).toISOString()
    };
    
    try {
      
      // Get plot data for testing
      await fetchAndSetPlotData(formattedConfig, indicators_with_params, setTestPlotData);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <>
      <header>
        <h1>📊 Trading Strategy Trainer</h1>
      </header>
      <main>
        <form onSubmit={handleTrain} style={{ width: '100%' }}>
          <div className="main-grid">
            <StockSection
              config={config}
              handleConfigChange={handleConfigChange}
            />
            <IndicatorsSection
              selectedIndicators={selectedIndicators}
              indicatorParams={indicatorParams}
              handleIndicatorSelect={handleIndicatorSelect}
              handleIndicatorParamChange={handleIndicatorParamChange}
              INDICATOR_OPTIONS={INDICATOR_OPTIONS}
            />
            <ModelSection
              selectedModel={selectedModel}
              handleModelChange={handleModelChange}
              MODEL_CONFIGS={MODEL_CONFIGS}
              config={config}
              handleConfigChange={handleConfigChange}
              handleTrain={handleTrain}
              handleTest={handleTest}
            />
            <ResultSection
              trainPlotData={trainPlotData}
              testPlotData={testPlotData}
              className="result-section"
            />
          </div>
        </form>
      </main>
      <footer>
        &copy; 2025 Trading Trainer. All rights reserved.
      </footer>
    </>
  );
}

export default App;
