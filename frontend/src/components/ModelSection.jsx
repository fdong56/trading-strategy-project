import React from 'react';

export default function ModelSection({
  selectedModel,
  handleModelChange,
  MODEL_CONFIGS,
  config,
  handleConfigChange
}) {
  return (
    <div className="model-section">
      <h3>🧠 Model</h3>
      <label htmlFor="model">Choose ML Model</label>
      <select
        id="model"
        value={selectedModel}
        onChange={handleModelChange}
        required
      >
        <option value="RandomForestTrader">Random Forest</option>
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
  );
}