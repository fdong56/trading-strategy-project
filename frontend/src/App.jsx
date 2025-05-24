import React, { useState } from 'react';
import './App.css';

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
  const [selectedModel, setSelectedModel] = useState('');
  const [config, setConfig] = useState({
    symbol: '',
    start_date: '',
    end_date: '',
    impact: '',
    commission: '',
    start_val: '',
    // Model-specific fields will be added dynamically
  });

  const handleConfigChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleModelChange = (e) => {
    const model = e.target.value;
    setSelectedModel(model);
    // Optionally reset model-specific fields
    if (MODEL_CONFIGS[model]) {
      const newFields = {};
      MODEL_CONFIGS[model].forEach(param => {
        newFields[param.key] = '';
      });
      setConfig(prev => ({
        ...prev,
        ...newFields,
      }));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // For now, just alert the config
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
      )}`
    );
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
              <option value="">Select a model</option>
              <option value="DecisionTreeTrader">Random Forest</option>
              <option value="QLearningTrader">Q Learning</option>
            </select>

            <label htmlFor="symbol">Stock Symbol</label>
            <input
              type="text"
              id="symbol"
              placeholder="e.g. AAPL"
              value={config.symbol}
              onChange={e => handleConfigChange('symbol', e.target.value)}
              required
            />

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
