// src/components/SidebarNavbar.js
import React from 'react';
import { Link, useLocation } from 'react-router-dom';

function SidebarNavbar({ role, onLogout }) {
  // Define nav items for each role
  const navItems = role === 'alumni'
    ? [
        { path: '/dashboard', icon: '🏠', label: 'Dashboard' },
        { path: '/opportunities', icon: '💼', label: 'Opportunities' },
        { path: '/mentorship', icon: '🎓', label: 'Mentorship' },
        { path: '/stories', icon: '📖', label: 'Stories' },
      ]
    : [
        { path: '/dashboard', icon: '🏠', label: 'Dashboard' },
        { path: '/opportunities', icon: '💼', label: 'Opportunities' },
        { path: '/mentorship', icon: '🎓', label: 'Mentorship' },
        { path: '/stories', icon: '📖', label: 'Stories' },
      ];

  const location = useLocation();

  return (
    <div style={{
      width: '60px',
      height: '100vh',
      backgroundColor: '#282c34',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      paddingTop: '20px',
      gap: '20px',
      position: 'relative'
    }}>
      {navItems.map(item => (
        <Link
          key={item.path}
          to={item.path}
          style={{
            color: 'white',
            textDecoration: 'none',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            position: 'relative',
            fontSize: '24px',
            height: '60px',
            backgroundColor: location.pathname === item.path ? '#61dafb' : 'transparent',
            borderRadius: '10px'
          }}
        >
          {item.icon}
          <span style={{
            position: 'absolute',
            left: '70px',
            whiteSpace: 'nowrap',
            opacity: 0,
            transition: 'opacity 0.3s',
            color: 'white',
            fontWeight: 'bold'
          }} className="sidebar-label">
            {item.label}
          </span>
        </Link>
      ))}
      
      {/* Logout button at the bottom */}
      <button
        onClick={onLogout}
        style={{
          position: 'absolute',
          bottom: '20px',
          color: 'white',
          backgroundColor: '#dc3545',
          border: 'none',
          borderRadius: '10px',
          width: '40px',
          height: '40px',
          fontSize: '20px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
        title="Logout"
      >
        🚪
      </button>
      
      <style>{`
        div a:hover .sidebar-label {
          opacity: 1;
        }
      `}</style>
    </div>
  );
}

export default SidebarNavbar;
