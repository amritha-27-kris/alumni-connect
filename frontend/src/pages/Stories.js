// src/pages/Stories.js
import React from 'react';

const stories = [
  { id:1, author:'Alice', role:'Alumni', text:'Got placed at TechCorp, thanks to the mentorship program!' },
  { id:2, author:'Bob', role:'Student', text:'Scholarship helped me pursue AI research.' },
  { id:3, author:'Carol', role:'Mentor', text:'Helping students grow is my passion.' }
];

function Stories() {
  return (
    <div className="App">
      <h1>Success Stories</h1>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(300px,1fr))', gap:'20px', padding:'20px' }}>
        {stories.map(s => (
          <div key={s.id} className="card">
            <h3>👤 {s.author} ({s.role})</h3>
            <p>{s.text}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Stories;
