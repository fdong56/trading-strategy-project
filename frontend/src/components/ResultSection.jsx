import React from 'react';
import { Line } from 'react-chartjs-2';

export default function ResultSection({ plotData, chartOptions, className = "result-section-training" }) {
  return (
    <div className={className}>
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
  );
}