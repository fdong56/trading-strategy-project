import React from 'react';
import { Line } from 'react-chartjs-2';

export default function StockSection({ config, stockSymbols, handleConfigChange, priceData }) {
  return (
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
            min="2000-02-01"
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
            max="2012-09-12"
            onChange={e => handleConfigChange('end_date', e.target.value)}
            required
          />
        </div>
      </div>
      {priceData && priceData.dates && priceData.prices && (
        <div style={{ marginTop: 16, marginBottom: 16, border: '1px solid #ccc', borderRadius: '8px' }}>
          <Line
            data={{
              labels: priceData.dates,
              datasets: [
                {
                  label: `${config.symbol} Price`,
                  data: priceData.prices,
                  borderColor: 'rgb(54, 162, 235)',
                  backgroundColor: 'rgba(54, 162, 235, 0.1)',
                  tension: 0.1,
                  pointRadius: 0
                }
              ]
            }}
            options={{
              responsive: true,
              plugins: { legend: { display: false }, title: { display: true } },
              scales: {
                y: { title: { display: true, text: 'Adjusted Price' }, grid: { display: true } },
                x: { title: { display: true }, grid: { display: false } }
              }
            }}
          />
        </div>
      )}
    </div>
  );
} 