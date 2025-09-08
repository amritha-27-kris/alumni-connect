// src/pages/Register.js
import React, { useState } from 'react';
import { Link } from 'react-router-dom';

function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '' });

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });
  const handleSubmit = e => {
    e.preventDefault();
    alert('Registered! (Demo only)');
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
        <button type="submit">Register</button>
      </form>
      <p>Already have an account? <Link to="/">Login</Link></p>
    </div>
  );
}

export default Register;
