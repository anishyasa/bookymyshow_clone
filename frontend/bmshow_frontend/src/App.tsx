// App.tsx
import React, { useState, useEffect } from 'react';
import Login from './login';
import MovieHomepage from './MovieHomepage';

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isCheckingAuth, setIsCheckingAuth] = useState<boolean>(true);

  useEffect(() => {
    // 1. Check if user is already logged in (e.g., on page refresh)
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
    }
    setIsCheckingAuth(false);
  }, []);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    // Clear tokens and reset state
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setIsAuthenticated(false);
  };

  // --- Styles ---
  const styles = {
    loading: {
      height: '100vh',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: '#222831',
      color: '#EEEEEE',
      fontFamily: 'Arial, sans-serif',
    },
    logoutBtn: {
      position: 'fixed' as 'fixed',
      bottom: '20px',
      right: '20px',
      padding: '10px 20px',
      backgroundColor: '#FF4C4C',
      color: 'white',
      border: 'none',
      borderRadius: '50px',
      cursor: 'pointer',
      boxShadow: '0 4px 6px rgba(0,0,0,0.3)',
      fontWeight: 'bold',
      zIndex: 1000,
    }
  };

  if (isCheckingAuth) {
    return <div style={styles.loading}>Loading...</div>;
  }

  return (
    <div>
      {isAuthenticated ? (
        <>
          <MovieHomepage />
          {/* Simple Floating Logout Button */}
          <button onClick={handleLogout} style={styles.logoutBtn}>
            Logout
          </button>
        </>
      ) : (
        <Login onLoginSuccess={handleLoginSuccess} />
      )}
    </div>
  );
};

export default App;