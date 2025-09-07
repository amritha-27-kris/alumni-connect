// src/pages/DashboardAlumni.js
import React from 'react';

function DashboardAlumni() {
  // Dummy data
  const opportunities = ['Opportunity 1', 'Opportunity 2', 'Opportunity 3', 'Opportunity 4', 'Opportunity 5'];
  const mentorships = ['Student A - Resume review', 'Student B - Interview prep', 'Student C - Skill guidance'];
  const stories = [
    'How I landed my first tech job',
    'Tips for applying to scholarships abroad',
    'Networking strategies that worked',
    'Story 4',
    'Story 5',
    'Story 6',
    'Story 7',
  ];

  return (
    <div style={{ padding: '20px', width: '100%' }}>
      <h1>Welcome, Alumni!</h1>

      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginTop: '20px' }}>
        {/* Posted Opportunities */}
        <div style={{ flex: '1 1 300px', backgroundColor: '#f0f0f0', padding: '15px', borderRadius: '8px' }}>
          <h2>💼 Posted Opportunities ({opportunities.length})</h2>
          <ul>
            {opportunities.map((op, idx) => (
              <li key={idx}>{op}</li>
            ))}
          </ul>
        </div>

        {/* Mentorships Offered */}
        <div style={{ flex: '1 1 300px', backgroundColor: '#f0f0f0', padding: '15px', borderRadius: '8px' }}>
          <h2>🎓 Mentorships Offered ({mentorships.length})</h2>
          <ul>
            {mentorships.map((m, idx) => (
              <li key={idx}>{m}</li>
            ))}
          </ul>
        </div>

        {/* Stories Shared */}
        <div style={{ flex: '1 1 300px', backgroundColor: '#f0f0f0', padding: '15px', borderRadius: '8px' }}>
          <h2>📖 Stories Shared ({stories.length})</h2>
          <ul>
            {stories.map((s, idx) => (
              <li key={idx}>{s}</li>
            ))}
          </ul>
        </div>
      </div>

      {/* Post new opportunity form */}
      <div style={{ marginTop: '30px', backgroundColor: '#e0f7fa', padding: '15px', borderRadius: '8px', maxWidth: '500px' }}>
        <h2>Post New Opportunity</h2>
        <form>
          <input type="text" placeholder="Opportunity Title" style={{ width: '100%', marginBottom: '10px', padding: '8px' }} />
          <select style={{ width: '100%', marginBottom: '10px', padding: '8px' }}>
            <option>Job</option>
            <option>Internship</option>
            <option>Scholarship</option>
          </select>
          <textarea placeholder="Description" style={{ width: '100%', marginBottom: '10px', padding: '8px' }}></textarea>
          <button type="submit">Post</button>
        </form>
      </div>
    </div>
  );
}

export default DashboardAlumni;
