import React from 'react';

function Dashboard() {
  const stats = [
    { title: 'Opportunities', count: 12, icon: '💼' },
    { title: 'Mentorships', count: 5, icon: '🎓' },
    { title: 'Stories', count: 8, icon: '📖' }
  ];

  return (
    <div className="App">
      <h1>Welcome, User!</h1>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))',
        gap: '20px',
        padding: '20px'
      }}>
        {stats.map((s, i) => (
          <div key={i} className="card">
            <h3>{s.icon} {s.title}</h3>
            <p>{s.count} items</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Dashboard;
