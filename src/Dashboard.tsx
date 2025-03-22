import React from "react";

interface CardProps {
  title: string;
  value: string;
}

const Card: React.FC<CardProps> = ({ title, value }) => {
  return (
    <div className="card">
      <h2 className="card-title">{title}</h2>
      <p className="card-value">{value}</p>
    </div>
  );
};

const Dashboard: React.FC = () => {
  const username = "John Doe"; // Mock username

  return (
    <div className="dashboard">
      <h1 className="dashboard-greeting">Hey, {username}</h1>
      <div className="cards-grid">
        {/* 1) Left-Top: Alerts */}
        <Card title="Alerts" value="You have 5 new alerts" />

        {/* 2) Right (spans two rows): Activity */}
        <Card title="Activity" value="Active for 3 hours today" />

        {/* 3) Left-Bottom: Total Sales */}
        <Card title="Total Sales" value="$1,234" />
      </div>
    </div>
  );
};

export default Dashboard;