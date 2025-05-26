import React, { useState, useEffect } from 'react';
import './App.css';
import { Line } from 'react-chartjs-2';
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
  DecisionTreeTrader: [
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
  const [selectedModel, setSelectedModel] = useState('DecisionTreeTrader');
  const [config, setConfig] = useState({
    symbol: '',
    start_date: '2008-01-01',
    end_date: '2009-01-01',
    impact: '',
    commission: '',
    start_val: '',
    n_day_return: '',
    y_buy: '',
    y_sell: '',
    leaf_size: '',
    num_bags: '',
  });
  const [stockSymbols, setStockSymbols] = useState([]);
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
  const [trainingResult, setTrainingResult] = useState(null);
  const [plotData, setPlotData] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/symbols')
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP error! status: ${res.status}`);
        }
        return res.json();
      })
      .then(data => setStockSymbols(data.symbols))
      .catch(error => {
        console.error('Error fetching symbols:', error);
        setStockSymbols([]);
      });
  }, []);

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

  const handleSubmit = async (e) => {
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
          decision_tree_config: selectedModel === 'DecisionTreeTrader' ? formattedConfig : null,
          indicators_with_params
        })
      });
      
      if (!trainResponse.ok) {
        const errorData = await trainResponse.json();
        // Handle FastAPI validation errors
        if (errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            // Format validation errors
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
      
      const trainResult = await trainResponse.json();
      setTrainingResult(trainResult);

      // Get plot data
      const plotResponse = await fetch('http://localhost:8000/api/plot', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model_type: selectedModel,
          qlearning_config: selectedModel === 'QLearningTrader' ? formattedConfig : null,
          decision_tree_config: selectedModel === 'DecisionTreeTrader' ? formattedConfig : null,
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
    } catch (error) {
      console.error('Error:', error);
      setTrainingResult({ 
        message: 'Error occurred', 
        error: error.message || error.toString() 
      });
    }
  };

  // Chart options
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          pointStyle: 'line'
        }
      },
      title: {
        display: true,
        text: 'Model Performance vs Benchmark'
      }
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: 'Normalized Portfolio Value'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Date'
        },
        ticks: {
          callback: function(value, index, values) {
            const date = new Date(this.getLabelForValue(value));
            return date.toISOString().split('T')[0];
          }
        }
      }
    }
  };

  return (
    <>
      <header>
        <h1>📊 Trading Strategy Trainer</h1>
      </header>
      <main>
        <form onSubmit={handleSubmit} style={{ width: '100%' }}>
          <div className="main-grid">
            <div className="stock-section">
              <h3>📈 Stock</h3>
              <label htmlFor="symbol">Stock Symbol</label>
              <select
                id="symbol"
                value={config.symbol}
                onChange={e => handleConfigChange('symbol', e.target.value)}
                required
              >
                <option value="">Select a symbol</option>
                {stockSymbols.map(sym => (
                  <option key={sym} value={sym}>{sym}</option>
                ))}
              </select>
              <div className="date-row">
                <div>
                  <label htmlFor="start">Start Date</label>
                  <input
                    type="date"
                    id="start"
                    value={config.start_date}
                    onChange={e => handleConfigChange('start_date', e.target.value)}
                    required
                  />
                </div>
                <div>
                  <label htmlFor="end">End Date</label>
                  <input
                    type="date"
                    id="end"
                    value={config.end_date}
                    onChange={e => handleConfigChange('end_date', e.target.value)}
                    required
                  />
                </div>
              </div>
              <div className="chart-placeholder" title="Mock stock chart"></div>
              <div className="date-row">
                <div>
                  <label htmlFor="impact">Impact</label>
                  <input
                    type="text"
                    id="impact"
                    placeholder="e.g. 0.005"
                    value={config.impact}
                    onChange={e => handleConfigChange('impact', e.target.value)}
                  />
                </div>
                <div>
                  <label htmlFor="commission">Commission</label>
                  <input
                    type="text"
                    id="commission"
                    placeholder="e.g. 9.95"
                    value={config.commission}
                    onChange={e => handleConfigChange('commission', e.target.value)}
                  />
                </div>
                <div>
                  <label htmlFor="start-value">Start Value</label>
                  <input
                    type="text"
                    id="start-value"
                    placeholder="e.g. 100000"
                    value={config.start_val}
                    onChange={e => handleConfigChange('start_val', e.target.value)}
                  />
                </div>
              </div>
            </div>
            <div className="indicators-section">
              <h3>📊 Indicators</h3>
              {[0, 1, 2].map(idx => (
                <div key={idx} style={{ marginBottom: 16 }}>
                  <label style={{ fontWeight: 'bold', fontSize: '1.08rem', color: '#1f2937' }}>Select Indicator {idx + 1}</label>
                  <select
                    value={selectedIndicators[idx]}
                    onChange={e => handleIndicatorSelect(idx, e.target.value)}
                    required
                  >
                    <option value="">Select indicator</option>
                    {INDICATOR_OPTIONS.filter(opt => !selectedIndicators.includes(opt.key) || selectedIndicators[idx] === opt.key).map(opt => (
                      <option key={opt.key} value={opt.key}>{opt.label}</option>
                    ))}
                  </select>
                  {selectedIndicators[idx] && (() => {
                    const params = INDICATOR_OPTIONS.find(opt => opt.key === selectedIndicators[idx]).params;
                    const rows = [];
                    for (let i = 0; i < params.length; i += 3) {
                      rows.push(
                        <div className="date-row" key={`indi-row-${idx}-${i}`}>
                          {params.slice(i, i + 3).map(param => (
                            <div key={param.key} style={{ marginLeft: 12 }}>
                              <label style={{ fontStyle: 'italic', fontWeight: 'normal' }}>{param.label}</label>
                              <input
                                className="param-input"
                                type={param.type}
                                placeholder={param.placeholder}
                                value={indicatorParams[selectedIndicators[idx]]?.[param.key] || ''}
                                onChange={e => handleIndicatorParamChange(selectedIndicators[idx], param.key, e.target.value)}
                                required
                              />
                            </div>
                          ))}
                        </div>
                      );
                    }
                    return rows;
                  })()}
                </div>
              ))}
            </div>
            <div className="model-section">
              <h3>🧠 Model</h3>
              <label htmlFor="model">Choose ML Model</label>
              <select
                id="model"
                value={selectedModel}
                onChange={handleModelChange}
                required
              >
                <option value="DecisionTreeTrader">Random Forest</option>
                <option value="QLearningTrader">Q Learning</option>
              </select>
              <br />
              {selectedModel && (
                <>
                  {(() => {
                    const params = MODEL_CONFIGS[selectedModel];
                    const rows = [];
                    for (let i = 0; i < params.length; i += 3) {
                      rows.push(
                        <div className="date-row" key={`model-row-${i}`}>
                          {params.slice(i, i + 3).map(param => (
                            <div key={param.key}>
                              <label htmlFor={param.key}>{param.label}</label>
                              <input
                                className="param-input"
                                type={param.type}
                                id={param.key}
                                placeholder={param.placeholder}
                                value={config[param.key] || ''}
                                step={param.step}
                                onChange={e => handleConfigChange(param.key, e.target.value)}
                              />
                            </div>
                          ))}
                        </div>
                      );
                    }
                    return rows;
                  })()}
                </>
              )}
              <button type="submit">🚀 Train Model</button>
            </div>
            <div className="result-section">
              <h3>🧠 Training Result</h3>
              {plotData ? (
                <div style={{ background: 'white', padding: '20px', borderRadius: '8px' }}>
                  <Line
                    data={{
                      labels: plotData.dates,
                      datasets: [
                        {
                          label: 'Model Performance',
                          data: plotData.model_values,
                          borderColor: 'rgb(75, 192, 192)',
                          tension: 0.1,
                          pointRadius: 0
                        },
                        {
                          label: 'Benchmark',
                          data: plotData.benchmark_values,
                          borderColor: 'rgb(255, 99, 132)',
                          tension: 0.1,
                          pointRadius: 0
                        }
                      ]
                    }}
                    options={chartOptions}
                  />
                </div>
              ) : (
                <span style={{ color: '#888' }}>No training result yet.</span>
              )}
            </div>
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
