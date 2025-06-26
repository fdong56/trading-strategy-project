import React from "react";
import { Line } from "react-chartjs-2";

export default function ResultSection({
  trainPlotData,
  testPlotData,
  className = "result-section",
}) {
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
        labels: {
          usePointStyle: true,
          pointStyle: "line",
        },
      },
      title: {
        display: true,
        text: "Model vs Benchmark",
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        title: {
          display: true,
          text: "Normalized Portfolio Value",
        },
      },
      x: {
        title: {
          display: false,
          text: "Date",
        },
        grid: { display: false },
        ticks: {
          callback: function (value) {
            const date = new Date(this.getLabelForValue(value));
            return date.toISOString().split("T")[0];
          },
        },
      },
    },
  };

  return (
    <div className={className}>
      <h3>🏆 Performance Results</h3>
      {/* Shared Legend: only show if there is at least one result */}
      {(trainPlotData || testPlotData) && (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 24, marginBottom: 16 }}>
          <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{
              display: "inline-block",
              width: 18,
              height: 4,
              background: "rgb(75, 192, 192)",
              borderRadius: 2
            }}></span>
            <span style={{ color: "#374151", fontWeight: 500 }}>ML Model</span>
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <span style={{
              display: "inline-block",
              width: 18,
              height: 4,
              background: "rgb(255, 99, 132)",
              borderRadius: 2
            }}></span>
            <span style={{ color: "#374151", fontWeight: 500 }}>Benchmark</span>
          </span>
        </div>
      )}

      {/* Training Results */}
      {trainPlotData ? (
        <div style={{ marginBottom: "20px" }}>
          <div
            style={{
              background: "white",
              padding: "20px",
              borderRadius: "8px",
            }}
          >
            <Line
              data={{
                labels: trainPlotData.dates,
                datasets: [
                  {
                    label: "Model",
                    data: trainPlotData.model_values,
                    borderColor: "rgb(75, 192, 192)",
                    tension: 0.1,
                    pointRadius: 0,
                  },
                  {
                    label: "Benchmark",
                    data: trainPlotData.benchmark_values,
                    borderColor: "rgb(255, 99, 132)",
                    tension: 0.1,
                    pointRadius: 0,
                  },
                ],
              }}
              options={{
                ...chartOptions,
                plugins: {
                  ...chartOptions.plugins,
                  legend: {
                    display: false,
                  },
                  title: {
                    display: true,
                    text: "Training Period",
                    font: { size: 16, weight: "bold" },
                    color: "#374151",
                    padding: { bottom: 16 }
                  },
                },
              }}
            />
          </div>
        </div>
      ) : (
        <div style={{ marginBottom: "20px" }}>
          <span style={{ color: "#888" }}>
            No training result yet. Click "Train Model" to see results.
          </span>
        </div>
      )}

      {/* Testing Results */}
      {testPlotData ? (
        <div>
          <div
            style={{
              background: "white",
              padding: "20px",
              borderRadius: "8px",
            }}
          >
            <Line
              data={{
                labels: testPlotData.dates,
                datasets: [
                  {
                    label: "Model",
                    data: testPlotData.model_values,
                    borderColor: "rgb(75, 192, 192)",
                    tension: 0.1,
                    pointRadius: 0,
                  },
                  {
                    label: "Benchmark",
                    data: testPlotData.benchmark_values,
                    borderColor: "rgb(255, 99, 132)",
                    tension: 0.1,
                    pointRadius: 0,
                  },
                ],
              }}
              options={{
                ...chartOptions,
                plugins: {
                  ...chartOptions.plugins,
                  legend: {
                    display: false,
                  },
                  title: {
                    display: true,
                    text: "Testing Period",
                    font: { size: 16, weight: "bold" },
                    color: "#374151",
                    padding: { bottom: 16 }
                  },
                },
              }}
            />
          </div>
        </div>
      ) : (
        <div>
          <span style={{ color: "#888" }}>
            No testing result yet. Click "Test Model" to see results.
          </span>
        </div>
      )}
    </div>
  );
}
