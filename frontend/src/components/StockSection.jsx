import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';

export default function StockSection({ config, handleConfigChange }) {

    const [stockSymbols, setStockSymbols] = useState([]);
    const [priceData, setPriceData] = useState(null);

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

    // Fetch price data for the selected symbol and date range
    useEffect(() => {
      if (config.symbol && config.start_date && config.end_date) {
        fetch(`http://localhost:8000/api/price?symbol=${config.symbol}&start_date=${config.start_date}&end_date=${config.end_date}`)
          .then(res => {
            if (!res.ok) throw new Error('Failed to fetch price data');
            return res.json();
          })
          .then(data => setPriceData(data))
          .catch(() => setPriceData(null));
      }
    }, [config.symbol, config.start_date, config.end_date]);


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
            {priceData ? (
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
                  plugins: {
                    legend: { display: false },
                    title: { display: true }
                  },
                  scales: {
                    y: {
                      title: { display: true, text: 'Adjusted Price' },
                      grid: { display: true }
                    },
                    x: {
                      title: { display: true },
                      grid: { display: false },
                      ticks: {
                        callback: function(value) {
                          const date = this.getLabelForValue(value);
                          return date;
                        }
                      }
                    }
                  }
                }}
              />
            ) : (
              <div className="chart-placeholder" title="Stock Price Chart"></div>
            )}
          </div>
        )}
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
    );
}