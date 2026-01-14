import React, { useState, useEffect } from 'react';

// --- Types ---
interface Movie {
  id: number;
  title: string;
  poster_url: string;
  duration_minutes: number;
  description: string;
  genres: string[];
  available_languages: string[];
  available_formats: string[];
  show_count: number;
}

interface HomepageResponse {
  movies: Movie[];
  filters: any;
  metadata: {
    city_id: number;
  };
}

const MovieHomepage = () => {
  const [movies, setMovies] = useState<Movie[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  
  // Defaulting to Bangalore (ID: 1)
  const [selectedCityId, setSelectedCityId] = useState<number>(1);

  // Hardcoded cities for the dropdown
  const cities = [
    { id: 1, name: 'Bangalore' },
    { id: 2, name: 'Mumbai' }
  ];

  // --- Palette ---
  const colors = {
    bg: '#222831',
    card: '#393E46',
    accent: '#00ADB5',
    text: '#EEEEEE',
    textSecondary: '#B0B0B0', // Slightly dimmer text
  };

  useEffect(() => {
    fetchMovies();
  }, [selectedCityId]);

  const fetchMovies = async () => {
    setLoading(true);
    setError('');
    
    // 1. Get the token we saved during login
    const token = localStorage.getItem('access_token');

    try {
      const response = await fetch(`http://localhost:8000/api/movies/homepage/?city_id=${selectedCityId}`, {
        method: 'GET', // Explicitly state the method
        // 2. Attach the token to the headers
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` 
        }
      });
      
      if (response.status === 401) {
        // Optional: If token expired, force logout (or handle refresh logic)
        setError('Session expired. Please logout and login again.');
        return;
      }

      if (!response.ok) {
        throw new Error('Failed to fetch movies');
      }

      const data: HomepageResponse = await response.json();
      setMovies(data.movies);
    } catch (err) {
      setError('Could not load movies. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCityChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCityId(Number(e.target.value));
  };

  // --- Styles ---
  const styles: { [key: string]: React.CSSProperties } = {
    pageContainer: {
      minHeight: '100vh',
      backgroundColor: colors.bg,
      color: colors.text,
      fontFamily: 'Arial, sans-serif',
    },
    navBar: {
      position: 'sticky',
      top: 0,
      zIndex: 100,
      backgroundColor: colors.card,
      padding: '1rem 2rem',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      boxShadow: '0 2px 10px rgba(0,0,0,0.3)',
      borderBottom: `1px solid ${colors.accent}`,
    },
    logo: {
      fontSize: '1.5rem',
      fontWeight: 'bold',
      color: colors.accent,
    },
    select: {
      padding: '8px 12px',
      borderRadius: '4px',
      backgroundColor: colors.bg,
      color: colors.text,
      border: `1px solid ${colors.accent}`,
      outline: 'none',
      fontSize: '1rem',
      cursor: 'pointer',
    },
    content: {
      padding: '2rem',
      maxWidth: '1200px',
      margin: '0 auto',
    },
    grid: {
      display: 'grid',
      // Responsive grid: cards will be at least 280px wide
      gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
      gap: '2rem',
    },
    card: {
      backgroundColor: colors.card,
      borderRadius: '8px',
      overflow: 'hidden',
      display: 'flex',
      flexDirection: 'column',
      boxShadow: '0 4px 6px rgba(0,0,0,0.2)',
      transition: 'transform 0.2s',
    },
    poster: {
      width: '100%',
      height: '400px',
      objectFit: 'cover',
    },
    cardBody: {
      padding: '1.5rem',
      display: 'flex',
      flexDirection: 'column',
      flex: 1, // Push footer to bottom
    },
    movieTitle: {
      fontSize: '1.25rem',
      fontWeight: 'bold',
      marginBottom: '0.5rem',
      color: colors.text,
    },
    metadata: {
      fontSize: '0.9rem',
      color: colors.textSecondary,
      marginBottom: '1rem',
    },
    pillContainer: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: '0.5rem',
      marginBottom: '1rem',
    },
    pill: {
      backgroundColor: 'rgba(0, 173, 181, 0.15)', // Transparent accent
      color: colors.accent,
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '0.8rem',
      fontWeight: 'bold',
    },
    bookButton: {
      marginTop: 'auto', // Pushes button to bottom of flex container
      width: '100%',
      padding: '12px',
      backgroundColor: colors.accent,
      color: colors.text,
      border: 'none',
      borderRadius: '4px',
      fontSize: '1rem',
      fontWeight: 'bold',
      cursor: 'pointer',
    },
    loading: {
      textAlign: 'center',
      padding: '4rem',
      color: colors.textSecondary,
    }
  };

  return (
    <div style={styles.pageContainer}>
      {/* Navbar */}
      <nav style={styles.navBar}>
        <div style={styles.logo}>CineBook</div>
        <select 
          value={selectedCityId} 
          onChange={handleCityChange} 
          style={styles.select}
        >
          {cities.map(city => (
            <option key={city.id} value={city.id}>{city.name}</option>
          ))}
        </select>
      </nav>

      {/* Main Content */}
      <div style={styles.content}>
        {loading ? (
          <div style={styles.loading}>Loading movies...</div>
        ) : error ? (
          <div style={{...styles.loading, color: '#ff6b6b'}}>{error}</div>
        ) : (
          <div style={styles.grid}>
            {movies.map(movie => (
              <div key={movie.id} style={styles.card}>
                <img 
                  src={movie.poster_url} 
                  alt={movie.title} 
                  style={styles.poster}
                  // Fallback for broken images (optional)
                  onError={(e) => {
                    (e.target as HTMLImageElement).src = 'https://via.placeholder.com/300x450?text=No+Image';
                  }}
                />
                
                <div style={styles.cardBody}>
                  <h3 style={styles.movieTitle}>{movie.title}</h3>
                  
                  <div style={styles.metadata}>
                    {movie.duration_minutes} min • {movie.genres.join(', ')}
                  </div>

                  {/* Languages & Formats Pills */}
                  <div style={styles.pillContainer}>
                    {movie.available_languages.map(lang => (
                        <span key={lang} style={styles.pill}>{lang}</span>
                    ))}
                    {movie.available_formats.map(fmt => (
                        <span key={fmt} style={styles.pill}>{fmt}</span>
                    ))}
                  </div>

                  <button style={styles.bookButton}>
                    {movie.show_count} Shows Available
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MovieHomepage;