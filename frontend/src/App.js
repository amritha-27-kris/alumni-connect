// src/App.js
import './App.css';
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './components/Login';
import Register from './pages/Register';
import DashboardStudent from './pages/DashboardStudent';
import DashboardAlumni from './pages/DashboardAlumni';
import Opportunities from './pages/Opportunities';
import Mentorship from './pages/Mentorship';
import Stories from './pages/Stories';
import SidebarNavbar from './components/SidebarNavbar';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is logged in on app load
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
    setLoading(false);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
  };

  if (loading) {
    return <div className="App"><h1>Loading...</h1></div>;
  }

  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes */}
        {user && (
          <Route
            path="/*"
            element={
              <div style={{ display: 'flex' }}>
                <SidebarNavbar role={user.role} onLogout={handleLogout} />
                <div style={{ flex: 1, padding: '20px' }}>
                  <Routes>
                    {user.role === 'alumni' ? (
                      <>
                        <Route path="dashboard" element={<DashboardAlumni user={user} />} />
                        <Route path="opportunities" element={<Opportunities user={user} />} />
                        <Route path="mentorship" element={<Mentorship user={user} />} />
                        <Route path="stories" element={<Stories user={user} />} />
                      </>
                    ) : (
                      <>
                        <Route path="dashboard" element={<DashboardStudent user={user} />} />
                        <Route path="opportunities" element={<Opportunities user={user} />} />
                        <Route path="mentorship" element={<Mentorship user={user} />} />
                        <Route path="stories" element={<Stories user={user} />} />
                      </>
                    )}
                  </Routes>
                </div>
              </div>
            }
          />
        )}
      </Routes>
    </Router>
  );
}

export default App;
