import React, { useState } from 'react';

interface LoginProps {
  onLoginSuccess: () => void;
}


const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // --- Palette ---
  const colors = {
    bg: '#222831',
    card: '#393E46',
    accent: '#00ADB5',
    text: '#EEEEEE',
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/users/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        onLoginSuccess(); 
      } else {
        setError(data.detail || 'Invalid credentials');
      }
    } catch (err) {
      setError('Network error. Is the backend running?');
    } finally {
      setIsLoading(false);
    }
  };


  const styles: { [key: string]: React.CSSProperties } = {
    container: {
      height: '100vh',
      width: '100vw',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      backgroundColor: colors.bg,
      fontFamily: 'Arial, sans-serif',
      margin: 0,
    },
    card: {
      width: '100%',
      maxWidth: '500px',
      padding: '2rem',
      backgroundColor: colors.card,
      borderRadius: '8px',
      boxShadow: '0 4px 6px rgba(0,0,0,0.3)',
      textAlign: 'center',
    },
    title: {
      color: colors.text,
      marginBottom: '1.5rem',
      fontSize: '1.8rem',
    },
    inputGroup: {
      marginBottom: '1rem',
      textAlign: 'left', // Now accepted
    },
    label: {
      display: 'block',
      color: colors.text,
      marginBottom: '0.5rem',
      fontSize: '0.9rem',
    },
    input: {
      width: '100%',
      padding: '10px',
      borderRadius: '4px',
      border: `1px solid ${colors.accent}`,
      backgroundColor: colors.bg,
      color: colors.text,
      fontSize: '1rem',
      boxSizing: 'border-box',
      outline: 'none',
    },
    button: {
      width: '100%',
      padding: '12px',
      marginTop: '1rem',
      backgroundColor: colors.accent,
      color: colors.text,
      border: 'none',
      borderRadius: '4px',
      fontSize: '1rem',
      cursor: 'pointer',
      fontWeight: 'bold',
      transition: 'opacity 0.2s',
      opacity: isLoading ? 0.7 : 1, // Moving dynamic style here is cleaner
    },
    error: {
      color: '#ff6b6b',
      marginBottom: '1rem',
      fontSize: '0.9rem',
    },
  };

  return (
    <div style={styles.container}>
      <div style={styles.card}>
        <h2 style={styles.title}>Welcome Back</h2>

        {error && <p style={styles.error}>{error}</p>}

        <form onSubmit={handleSubmit}>
          <div style={styles.inputGroup}>
            <label htmlFor="username" style={styles.label}>Username</label>
            <input
              type="text"
              name="username"
              id="username"
              value={formData.username}
              onChange={handleChange}
              style={styles.input}
              required
            />
          </div>

          <div style={styles.inputGroup}>
            <label htmlFor="password" style={styles.label}>Password</label>
            <input
              type="password"
              name="password"
              id="password"
              value={formData.password}
              onChange={handleChange}
              style={styles.input}
              required
            />
          </div>

          <button
            type="submit"
            style={styles.button}
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;