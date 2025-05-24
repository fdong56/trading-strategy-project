import React, { useState } from 'react'
import './App.css'

function App() {
  const [selectedModel, setSelectedModel] = useState('QLearningTrader')
  const [config, setConfig] = useState({
    symbol: '',
    start_date: '',
    end_date: '',
    start_val: 100000,
    impact: 0.0,
    commission: 0.0,
    // QLearningTrader-specific
    bins: 10,
    alpha: 0.2,
    gamma: 0.9,
    rar: 0.98,
    radr: 0.999,
    dyna: 0,
    // DecisionTreeTrader-specific
    n_day_return: 5,
    y_buy: 0.008,
    y_sell: -0.008,
    leaf_size: 6,
    num_bags: 10,
  })

  // Helper to update config fields
  const handleConfigChange = (field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value
    }))
  }

  return (
    <div className="container">
      <h1>Trading Strategy Configurator</h1>
      <form
        onSubmit={e => {
          e.preventDefault()
          console.log('Selected Model:', selectedModel)
          console.log('Config:', config)
        }}
      >
        <label>
          Select Model:
          <select
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
          >
            <option value="QLearningTrader">QLearningTrader</option>
            <option value="DecisionTreeTrader">DecisionTreeTrader</option>
          </select>
        </label>
        <br />

        <label>
          Symbol:
          <input
            type="text"
            value={config.symbol}
            onChange={e => handleConfigChange('symbol', e.target.value)}
            required
          />
        </label>
        <br />

        <label>
          Start Date:
          <input
            type="date"
            value={config.start_date}
            onChange={e => handleConfigChange('start_date', e.target.value)}
            required
          />
        </label>
        <br />

        <label>
          End Date:
          <input
            type="date"
            value={config.end_date}
            onChange={e => handleConfigChange('end_date', e.target.value)}
            required
          />
        </label>
        <br />

        <label>
          Start Value:
          <input
            type="number"
            value={config.start_val}
            onChange={e => handleConfigChange('start_val', Number(e.target.value))}
          />
        </label>
        <br />

        <label>
          Impact:
          <input
            type="number"
            step="0.01"
            value={config.impact}
            onChange={e => handleConfigChange('impact', Number(e.target.value))}
          />
        </label>
        <br />

        <label>
          Commission:
          <input
            type="number"
            step="0.01"
            value={config.commission}
            onChange={e => handleConfigChange('commission', Number(e.target.value))}
          />
        </label>
        <br />

        {/* QLearningTrader-specific fields */}
        {selectedModel === 'QLearningTrader' && (
          <>
            <label>
              Bins:
              <input
                type="number"
                value={config.bins}
                onChange={e => handleConfigChange('bins', Number(e.target.value))}
              />
            </label>
            <br />
            <label>
              Alpha:
              <input
                type="number"
                step="0.01"
                value={config.alpha}
                onChange={e => handleConfigChange('alpha', Number(e.target.value))}
              />
            </label>
            <br />
            <label>
              Gamma:
              <input
                type="number"
                step="0.01"
                value={config.gamma}
                onChange={e => handleConfigChange('gamma', Number(e.target.value))}
              />
            </label>
            <br />
            <label>
              RAR:
              <input
                type="number"
                step="0.01"
                value={config.rar}
                onChange={e => handleConfigChange('rar', Number(e.target.value))}
              />
            </label>
            <br />
            <label>
              RADR:
              <input
                type="number"
                step="0.001"
                value={config.radr}
                onChange={e => handleConfigChange('radr', Number(e.target.value))}
              />
            </label>
            <br />
            <label>
              Dyna:
              <input
                type="number"
                value={config.dyna}
                onChange={e => handleConfigChange('dyna', Number(e.target.value))}
              />
            </label>
            <br />
          </>
        )}

        {/* DecisionTreeTrader-specific fields */}
        {selectedModel === 'DecisionTreeTrader' && (
          <>
            <label>
              N Day Return:
              <input
                type="number"
                value={config.n_day_return}
                onChange={e => handleConfigChange('n_day_return', Number(e.target.value))}
              />
            </label>
            <br />
            <label>
              Y Buy:
              <input
                type="number"
                step="0.001"
                value={config.y_buy}
                onChange={e => handleConfigChange('y_buy', Number(e.target.value))}
              />
            </label>
            <br />
            <label>
              Y Sell:
              <input
                type="number"
                step="0.001"
                value={config.y_sell}
                onChange={e => handleConfigChange('y_sell', Number(e.target.value))}
              />
            </label>
            <br />
            <label>
              Leaf Size:
              <input
                type="number"
                value={config.leaf_size}
                onChange={e => handleConfigChange('leaf_size', Number(e.target.value))}
              />
            </label>
            <br />
            <label>
              Num Bags:
              <input
                type="number"
                value={config.num_bags}
                onChange={e => handleConfigChange('num_bags', Number(e.target.value))}
              />
            </label>
            <br />
          </>
        )}

        <button type="submit">Submit</button>
      </form>
    </div>
  )
}

export default App
