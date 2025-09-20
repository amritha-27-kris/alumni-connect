// src/pages/Register.js
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

function Register() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '', role: 'student', skills: '' });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('http://localhost:5000/api/users/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form),
      });

      const data = await response.json();

      if (data.success) {
        setMessage('Registration successful! Redirecting to login...');
        setTimeout(() => {
          navigate('/');
        }, 2000);
      } else {
        setMessage(data.message || 'Registration failed');
      }
    } catch (error) {
      setMessage('Network error. Please try again.');
      console.error('Registration error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Register</h1>
      <form onSubmit={handleSubmit} style={{ maxWidth: '400px', margin: '30px auto', display: 'flex', flexDirection: 'column', gap: '10px' }}>
        <label>Name</label>
        <input name="name" value={form.name} onChange={handleChange} required />
        
        <label>Email</label>
        <input type="email" name="email" value={form.email} onChange={handleChange} required />
        
        <label>Password</label>
        <input type="password" name="password" value={form.password} onChange={handleChange} required />
        
        <label>Role</label>
        <select name="role" value={form.role} onChange={handleChange}>
          <option value="student">Student</option>
          <option value="alumni">Alumni</option>
          <option value="mentor">Mentor</option>
        </select>
        
        <label>Skills (optional)</label>
        <textarea 
          name="skills" 
          value={form.skills} 
          onChange={handleChange} 
          placeholder="e.g., Python, React, Data Science"
          rows="3"
        />
        
        <button type="submit" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>
      
      {message && (
        <p style={{ 
          marginTop: '15px', 
          color: message.includes('successful') ? 'green' : 'red',
          fontWeight: 'bold'
        }}>
          {message}
        </p>
      )}
      
      <p>Already have an account? <Link to="/">Login</Link></p>
    </div>
  );
}

export default Register;
