import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';

export default function ModelSection({
  selectedModel,
  handleModelChange,
  MODEL_CONFIGS,
  config,
  handleConfigChange
}) {


  const [valStartDate, setValStartDate] = useState('2009-01-01');
  const [valEndDate, setValEndDate] = useState('2010-01-01');

  // Ensure validation dates are within training period
  const minDate = '2000-02-01';
  const maxDate = '2012-09-12';



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
      <div className="date-row">
        <div>
          <label htmlFor="start">Training Start Date</label>
          <input
            type="date"
            id="start"
            value={config.start_date}
            min={minDate}
            max={maxDate}
            onChange={e => handleConfigChange('start_date', e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="end">Training End Date</label>
          <input
            type="date"
            id="end"
            value={config.end_date}
            min={config.start_date}
            max={maxDate}
            onChange={e => handleConfigChange('end_date', e.target.value)}
            required
          />
        </div>
      </div>
      <button type="submit">🚀 Train Model</button>

      <div className="date-row">
        <div>
          <label htmlFor="val_start">Testing Start Date</label>
          <input
            type="date"
            id="val_start"
            value={valStartDate}
            min={minDate}
            max={maxDate}
            onChange={e => setValStartDate(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="val_end">Testing End Date</label>
          <input
            type="date"
            id="val_end"
            value={valEndDate}
            min={valStartDate}
            max={maxDate}
            onChange={e => setValEndDate(e.target.value)}
          />
        </div>
      </div>

      <button type="submit">🚀 Test Model</button>
    </div>
  );
}