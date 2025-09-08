// src/App.js
import './App.css';
import React from 'react';
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
  const role = 'alumni'; // or 'student'

  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected routes */}
        <Route
          path="/*"
          element={
            <div style={{ display: 'flex' }}>
              <SidebarNavbar role={role} />
              <div style={{ flex: 1, padding: '20px' }}>
                <Routes>
                  {role === 'alumni' ? (
                    <>
                      <Route path="dashboard" element={<DashboardAlumni />} />
                      <Route path="opportunities" element={<Opportunities />} />
                      <Route path="mentorship" element={<Mentorship />} />
                      <Route path="stories" element={<Stories />} />
                    </>
                  ) : (
                    <>
                      <Route path="dashboard" element={<DashboardStudent />} />
                      <Route path="opportunities" element={<Opportunities />} />
                      <Route path="mentorship" element={<Mentorship />} />
                      <Route path="stories" element={<Stories />} />
                    </>
                  )}
                </Routes>
              </div>
            </div>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
