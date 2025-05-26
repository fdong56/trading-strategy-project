import React, { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';

export default function ValidationSection({config }) {

  const [valStartDate, setValStartDate] = useState('2009-01-01');
  const [valEndDate, setValEndDate] = useState('2010-01-01');
  const [validationPriceData, setValidationPriceData] = useState(null);


  useEffect(() => {
    if (config.symbol && valStartDate && valEndDate) {
      fetch(`http://localhost:8000/api/price?symbol=${config.symbol}&start_date=${valStartDate}&end_date=${valEndDate}`)
        .then(res => {
          if (!res.ok) throw new Error('Failed to fetch validation price data');
          return res.json();
        })
        .then(data => setValidationPriceData(data))
        .catch(() => setValidationPriceData(null));
    }
  }, [config.symbol, valStartDate, valEndDate]);

  return (
    <div className="validation-section" style={{ background: 'white', padding: '20px', borderRadius: '8px', border: '1px solid #ccc', marginTop: 32 }}>
      <h3>🔍 Validation</h3>
      <div className="date-row">
        <div>
          <label htmlFor="val-start">Validation Start Date</label>
          <input
            type="date"
            id="val-start"
            value={valStartDate}
            min="2000-02-01"
            max="2012-09-12"
            onChange={e => setValStartDate(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="val-end">Validation End Date</label>
          <input
            type="date"
            id="val-end"
            value={valEndDate}
            min="2000-02-01"
            max="2012-09-12"
            onChange={e => setValEndDate(e.target.value)}
          />
        </div>
      </div>
      {validationPriceData && validationPriceData.dates && validationPriceData.prices && (
        <div style={{ marginTop: 16, marginBottom: 16 }}>
          <Line
            data={{
              labels: validationPriceData.dates,
              datasets: [
                {
                  label: `${config.symbol} Price`,
                  data: validationPriceData.prices,
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