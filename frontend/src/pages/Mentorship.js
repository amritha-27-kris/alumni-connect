// src/pages/Mentorship.js
import React from 'react';

const mentors = [
  { id:1, name:'Alice', topic:'Resume Building', schedule:'Sep 10, 3 PM' },
  { id:2, name:'Bob', topic:'Interview Prep', schedule:'Sep 12, 5 PM' },
  { id:3, name:'Carol', topic:'Skill Development', schedule:'Sep 15, 4 PM' }
];

function Mentorship() {
  return (
    <div className="App">
      <h1>Mentorship Sessions</h1>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(300px,1fr))', gap:'20px', padding:'20px' }}>
        {mentors.map(m => (
          <div key={m.id} className="card">
            <h3>👩‍🏫 {m.name}</h3>
            <p><strong>Topic:</strong> {m.topic}</p>
            <p><strong>Schedule:</strong> {m.schedule}</p>
            <button>Book</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Mentorship;
