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
        text: "Model Performance vs Benchmark",
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
          display: true,
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

      {/* Training Results */}
      {trainPlotData ? (
        <div style={{ marginBottom: "20px" }}>
          <h4 style={{ marginBottom: "10px", color: "#374151" }}>
            Training Period Performance
          </h4>
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
                    label: "Model Performance",
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
                  title: {
                    display: false, // Hide individual chart titles since we have a shared title
                  },
                },
              }}
            />
          </div>
        </div>
      ) : (
        <div style={{ marginBottom: "20px" }}>
          <h4 style={{ marginBottom: "10px", color: "#374151" }}>
            Training Period Performance
          </h4>
          <span style={{ color: "#888" }}>
            No training result yet. Click "Train Model" to see results.
          </span>
        </div>
      )}

      {/* Testing Results */}
      {testPlotData ? (
        <div>
          <h4 style={{ marginBottom: "10px", color: "#374151" }}>
            Testing Period Performance
          </h4>
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
                    label: "Model Performance",
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
                  title: {
                    display: false, // Hide individual chart titles since we have a shared title
                  },
                },
              }}
            />
          </div>
        </div>
      ) : (
        <div>
          <h4 style={{ marginBottom: "10px", color: "#374151" }}>
            Testing Period Performance
          </h4>
          <span style={{ color: "#888" }}>
            No testing result yet. Click "Test Model" to see results.
          </span>
        </div>
      )}
    </div>
  );
}
