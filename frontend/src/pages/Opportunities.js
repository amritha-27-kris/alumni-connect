// src/pages/Opportunities.js
import React from 'react';

const dummyOpportunities = [
  { id:1, title:'Frontend Internship', type:'Internship', company:'TechCorp', desc:'Work on React apps.' },
  { id:2, title:'Scholarship: AI Research', type:'Scholarship', company:'AI Institute', desc:'Funding for AI projects.' },
  { id:3, title:'Backend Developer', type:'Job', company:'CodeLabs', desc:'Build REST APIs with Flask.' }
];

function Opportunities() {
  return (
    <div className="App">
      <h1>Opportunities</h1>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fit,minmax(300px,1fr))', gap:'20px', padding:'20px' }}>
        {dummyOpportunities.map(op => (
          <div key={op.id} className="card">
            <h3>{op.title} <span style={{backgroundColor:'#61dafb',padding:'2px 8px',borderRadius:'5px',fontSize:'0.8rem',marginLeft:'5px'}}>{op.type}</span></h3>
            <p><strong>Company:</strong> {op.company} 🚀</p>
            <p>{op.desc}</p>
            <button>Apply</button>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Opportunities;
