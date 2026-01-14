import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './login';
import MovieHomepage from './MovieHomepage';
import MovieSchedule from './MovieSchedule';
import SeatSelection from './SeatSelection';

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsAuthenticated(!!token);
    setLoading(false);
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
  };

  if (loading) return <div style={{color: '#fff'}}>Loading...</div>;

  return (
    <div style={{ width: '100vw', minHeight: '100vh', backgroundColor: '#222831', fontFamily: "'Inter', sans-serif" }}>
      {!isAuthenticated ? (
        <Login onLoginSuccess={handleLoginSuccess} />
      ) : (
        <BrowserRouter>
          <Routes>
            {/* Route 1: Homepage */}
            <Route 
              path="/" 
              element={<MovieHomepage onLogout={handleLogout} />} 
            />
            
            {/* Route 2: Schedule Page (Dynamic ID) */}
            <Route 
              path="/movie/:id" 
              element={<MovieSchedule />} 
            />

            {/* Redirect unknown routes to home */}
            <Route path="*" element={<Navigate to="/" />} />
            <Route 
              path="/show/:showId/seats" 
              element={<SeatSelection />} 
            />
          </Routes>
        </BrowserRouter>
      )}
    </div>
  );
};

export default App;