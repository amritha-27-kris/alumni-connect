import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

function Login() {
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });

  const handleChange = e => setForm({ ...form, [e.target.name]: e.target.value });

  const handleSubmit = e => {
    e.preventDefault();
    // TODO: Replace with actual backend authentication
    if (form.email && form.password) {
      alert('Login successful!');
      navigate('/dashboard');
    } else {
      alert('Please enter email and password');
    }
  };

  return (
<div className="App">
  <h1>Login</h1>
  {/* src/components/Login.js */}
  <form
    onSubmit={handleSubmit}
    style={{ maxWidth: '400px', margin: '30px auto', display: 'flex', flexDirection: 'column', gap: '10px' }}
  >
    <input
      type="email"
      name="email"
      value={form.email}
      onChange={handleChange}
      required
    />

    <label>Password</label>
    <input
      type="password"
      name="password"
      value={form.password}
      onChange={handleChange}
      required
    />

    <button type="submit" style={{ marginTop: '10px' }}>Login</button>
  </form>

  <p style={{ marginTop: '15px' }}>
    Don't have an account? <Link to="/register">Sign up</Link>
  </p>
</div>

  );
}

export default Login;
