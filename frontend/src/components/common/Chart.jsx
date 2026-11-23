import React, { useRef } from 'react';
import { Line, Pie, Bar, Doughnut } from 'react-chartjs-2';
import zoomPlugin from 'chartjs-plugin-zoom';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  BarElement,
  ArcElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components + plugins
ChartJS.register(
  zoomPlugin,
  LineElement,
  PointElement,
  BarElement,
  ArcElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend
);

// Helper to dynamically generate Y scales for Line charts
const generateScalesFromDatasets = (datasets) => {
  const scales = {};
  const yAxisIds = [...new Set(datasets.map(ds => ds.yAxisID))];

  yAxisIds.forEach((id, index) => {
    const dataset = datasets.find(ds => ds.yAxisID === id);
    scales[id] = {
      type: 'linear',
      position: index === 0 ? 'left' : 'right',
      title: {
        display: true,
        text: dataset?.label || `Y-Axis ${index + 1}`,
      },
      grid: {
        drawOnChartArea: index === 0,
      },
    };
  });

  return scales;
};

// Builds the dataset object based on the chart type
const buildChartData = (labels, datasets, chartType) => {
  if (chartType === 'pie'|| chartType === 'doughnut') {
    const [mainDataset] = datasets;

    return {
      labels,
      datasets: [{
        label: mainDataset?.label || '',
        data: mainDataset?.data || [],
        backgroundColor: mainDataset?.backgroundColor || [],
      }],
    };
  }

  // Default to line/bar style structure
  return {
    labels,
    datasets: datasets.map(item => ({
      type: item.type,
      label: item.label,
      data: item.data,
      borderColor: item.borderColor,
      backgroundColor: item.backgroundColor,
      yAxisID: item.yAxisID,
      barPercentage: item.barPercentage,
      tension: item.tension,
    })),
  };
};

// Main Chart component
export default function Chart({ labels=[], datasets=[], chartType = 'line' }) {
  const chartRef = useRef();
  const chartData = buildChartData(labels, datasets, chartType);

  // Options vary depending on chart type
  const options = chartType === 'pie' || chartType === 'doughnut' ? {
    responsive: true,
    plugins: {
      tooltip: { enabled: true },
      legend: { position: 'top' },
    },
  } : {
    responsive: true,
    plugins: {
      tooltip: { enabled: true },
      zoom: {
        pan: {
          enabled: true,
          mode: 'x',
          threshold: 5,
        },
        zoom: {
          wheel: { enabled: true },
          pinch: { enabled: true },
          mode: 'x',
        },
      },
      legend: { position: 'top' },
    },
    scales: generateScalesFromDatasets(chartData.datasets),
  };

  const chartComponents = {
    line: Line,
    pie: Pie,
    bar: Bar,
    doughnut: Doughnut,
  };

  const ChartComponent = chartComponents[chartType] || Line;

  return (
    <div className="chart">
      <ChartComponent ref={chartRef} data={chartData} options={options} />

      <div className="chart-btn">
        <button
          onClick={() => {
            const chartInstance = chartRef.current;

            if (chartInstance && typeof chartInstance.toBase64Image === 'function') {
              const url = chartInstance.toBase64Image();
              const link = document.createElement('a');
              link.href = url;
              link.download = 'chart.png';
              link.click();
            } else {
              alert('Chart export is not available.');
            }
          }}
        >
          Завантажити
        </button>
      </div>
    </div>
  );
}
