import React, { useState } from 'react';
import './App.css';

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

// List of stock symbols from data/ directory
const STOCK_SYMBOLS = [
  "ZMH", "XTO", "XYL", "YHOO", "YUM", "ZION", "XLNX", "XOM", "XRAY", "XRX", "WYN", "WYNN", "X", "XEL", "XL", "WPX", "WU", "WWY", "WY", "WYE", "WMB", "WMT", "WPI", "WPO", "WHR", "WIN", "WLP", "WM", "WEN", "WFC", "WFM", "WFR", "WFT", "WAT", "WB", "WDC", "WEC", "VRSN", "VTR", "VZ", "WAG", "WAMUQ", "VIAB", "VLO", "VMC", "VNO", "UTX", "V", "VAR", "VFC", "VIA.B", "UNP", "UPS", "URBN", "USB", "UST", "TYC", "UIS", "UNH", "UNM", "TWC", "TWX", "TXN", "TXT", "TROW", "TRV", "TSN", "TSO", "TSS", "TMO", "TRIP", "TJX", "TLAB", "TMK", "TGT", "THC", "TIE", "TIF", "TE", "TEG", "TEL", "TER", "TEX", "SYMC", "SYY", "T", "TAP", "TDC", "SWK", "SWN", "SWY", "SYK", "STX", "STZ", "SUN", "SVU", "STI", "STJ"
];

function App() {
  const [selectedModel, setSelectedModel] = useState('DecisionTreeTrader');
  const [config, setConfig] = useState({
    symbol: '',
    start_date: '',
    end_date: '',
    impact: '',
    commission: '',
    start_val: '',
    n_day_return: '',
    y_buy: '',
    y_sell: '',
    leaf_size: '',
    num_bags: '',
  });
  const [selectedIndicators, setSelectedIndicators] = useState([
    '', '', ''
  ]);
  const [indicatorParams, setIndicatorParams] = useState({});

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

  const handleSubmit = (e) => {
    e.preventDefault();
    const indicators_with_params = buildIndicatorsWithParams();
    // For now, just alert the config and indicators
    alert(
      `Model: ${selectedModel}\n` +
      `Symbol: ${config.symbol}\n` +
      `Start: ${config.start_date}\n` +
      `End: ${config.end_date}\n` +
      `Impact: ${config.impact}\n` +
      `Commission: ${config.commission}\n` +
      `Start Value: ${config.start_val}\n` +
      `Model Params:\n${JSON.stringify(
        MODEL_CONFIGS[selectedModel]?.reduce((acc, param) => {
          acc[param.label] = config[param.key];
          return acc;
        }, {}),
        null,
        2
      )}\n` +
      `Indicators with Params:\n${JSON.stringify(indicators_with_params, null, 2)}`
    );
    // Here you would POST to your backend API with indicators_with_params
  };

  return (
    <>
      <header>
        <h1>📊 Trading Strategy Trainer</h1>
      </header>
      <main>
        <div className="card">
          <h2>📈 Configure Strategy</h2>
          <form onSubmit={handleSubmit}>
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

            <label htmlFor="symbol">Stock Symbol</label>
            <select
              id="symbol"
              value={config.symbol}
              onChange={e => handleConfigChange('symbol', e.target.value)}
              required
            >
              <option value="">Select a symbol</option>
              {STOCK_SYMBOLS.map(sym => (
                <option key={sym} value={sym}>{sym}</option>
              ))}
            </select>

            <div className="chart-placeholder" title="Mock stock chart"></div>

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

            <label htmlFor="impact">Impact</label>
            <input
              type="text"
              id="impact"
              placeholder="e.g. 0.005"
              value={config.impact}
              onChange={e => handleConfigChange('impact', e.target.value)}
            />

            <label htmlFor="commission">Commission</label>
            <input
              type="text"
              id="commission"
              placeholder="e.g. 9.95"
              value={config.commission}
              onChange={e => handleConfigChange('commission', e.target.value)}
            />

            <label htmlFor="start-value">Start Value</label>
            <input
              type="text"
              id="start-value"
              placeholder="e.g. 100000"
              value={config.start_val}
              onChange={e => handleConfigChange('start_val', e.target.value)}
            />

            <div className="section">
              <h3>🧠 Model Parameters</h3>
              {selectedModel &&
                MODEL_CONFIGS[selectedModel].map(param => (
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

            <div className="section">
              <h3>📊 Select Indicators & Set Parameters</h3>
              {[0, 1, 2].map(idx => (
                <div key={idx} style={{ marginBottom: 16 }}>
                  <label>Select Indicator {idx + 1}</label>
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
                  {/* Show parameter fields for this indicator */}
                  {selectedIndicators[idx] &&
                    INDICATOR_OPTIONS.find(opt => opt.key === selectedIndicators[idx]).params.map(param => (
                      <div key={param.key} style={{ marginLeft: 12 }}>
                        <label>{param.label}</label>
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
              ))}
            </div>

            <button type="submit">🚀 Train Model</button>
          </form>
        </div>
      </main>
      <footer>
        &copy; 2025 Trading Trainer. All rights reserved.
      </footer>
    </>
  );
}

export default App;
