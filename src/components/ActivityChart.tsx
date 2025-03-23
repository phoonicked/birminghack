import React from "react";
import { Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const ActivityChart: React.FC = () => {
  // Mock data: 24 data points representing hourly visits
  const data = {
    labels: Array.from({ length: 24 }, (_, i) => `${i}:00`),
    datasets: [
      {
        label: "Visits",
        data: [5, 10, 8, 12, 15, 7, 3, 4, 8, 16, 20, 18, 10, 5, 2, 0, 3, 7, 9, 11, 14, 16, 12, 8],
        backgroundColor: "rgba(37, 99, 235, 0.6)", // Blue-ish color
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: true,
        text: "Hourly Visits",
        font: {
          size: 16,
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          precision: 0,
        },
      },
    },
  };

  return <Bar data={data} options={options} />;
};

export default ActivityChart;
