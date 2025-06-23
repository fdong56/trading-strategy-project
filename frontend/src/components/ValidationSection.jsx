import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';

export default function ValidationSection({ config }) {
  
  const [valStartDate, setValStartDate] = useState('2009-01-01');
  const [valEndDate, setValEndDate] = useState('2010-01-01');
  const [priceData, setPriceData] = useState(null);

  // Ensure validation dates are within training period
  const minDate = '2000-02-01';
  const maxDate = '2012-09-12';

  useEffect(() => {
    if (config.symbol && valStartDate && valEndDate) {
      fetch(`http://localhost:8000/api/price?symbol=${config.symbol}&start_date=${valStartDate}&end_date=${valEndDate}`)
        .then(res => {
          if (!res.ok) throw new Error('Failed to fetch price data');
          return res.json();
        })
        .then(data => setPriceData(data))
        .catch(() => setPriceData(null));
    }
  }, [config.symbol, valStartDate, valEndDate]);

  return (
    <div className="validation-section">
      <h3>📈 Validation</h3>
      <div className="date-row">
        <div>
          <label htmlFor="val_start">Validation Start Date</label>
          <input
            type="date"
            id="val_start"
            value={valStartDate}
            min={minDate}
            max={valEndDate}
            onChange={e => setValStartDate(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="val_end">Validation End Date</label>
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
    </div>
  );
}