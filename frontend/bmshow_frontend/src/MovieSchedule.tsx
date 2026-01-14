import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';

// --- Interfaces ---
interface Show {
  id: number;
  start_time: string;
  end_time: string;
  format: string;
  language: string;
}

interface VenueSchedule {
  venue_id: number;
  name: string;
  address: string;
  shows: Show[];
}

interface ScheduleData {
  [date: string]: VenueSchedule[]; // Key is date string "YYYY-MM-DD"
}

const MovieSchedule: React.FC = () => {
  // Get data from route
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Extract movie title from route state
  const movieTitle = (location.state as any)?.movieTitle || 'Movie Details';
  
  // Extract cityId from query params
  const searchParams = new URLSearchParams(location.search);
  const cityId = Number(searchParams.get('city_id')) || 1;
  
  const movieId = Number(id);

  const [schedule, setSchedule] = useState<ScheduleData | null>(null);
  const [dates, setDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  // --- Palette ---
  const colors = {
    bg: '#222831',
    card: '#393E46',
    accent: '#00ADB5',
    text: '#EEEEEE',
    textSecondary: '#B0B0B0',
    border: '#2D333B'
  };

  useEffect(() => {
    fetchSchedule();
  }, [movieId, cityId]);

  const fetchSchedule = async () => {
    setLoading(true);
    const token = localStorage.getItem('access_token');
    
    try {
      const response = await fetch(`http://localhost:8000/api/shows/movies/${movieId}/schedule/?city_id=${cityId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to load schedule');

      const data = await response.json();
      
      // Extract dates and sort them
      const availableDates = Object.keys(data.schedule).sort();
      
      setSchedule(data.schedule);
      setDates(availableDates);
      
      // Default to the first available date
      if (availableDates.length > 0) {
        setSelectedDate(availableDates[0]);
      }
    } catch (err) {
      setError('Could not fetch showtimes.');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    navigate('/');
  };

  // Helper to format date (e.g., "2026-01-14" -> "Wed, 14 Jan")
  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = { weekday: 'short', day: 'numeric', month: 'short' };
    return new Date(dateString).toLocaleDateString('en-US', options);
  };

  // Helper to format time (e.g., "14:00" -> "02:00 PM")
  const formatTime = (timeString: string) => {
    const [hours, minutes] = timeString.split(':');
    const date = new Date();
    date.setHours(parseInt(hours), parseInt(minutes));
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  // --- Styles ---
  const styles: { [key: string]: React.CSSProperties } = {
    container: {
      padding: '2rem',
      maxWidth: '1000px',
      margin: '0 auto',
      color: colors.text,
      minHeight: '100vh',
      backgroundColor: colors.bg,
    },
    header: {
      display: 'flex',
      alignItems: 'center',
      gap: '1rem',
      marginBottom: '2rem',
    },
    backButton: {
      background: 'none',
      border: 'none',
      color: colors.accent,
      fontSize: '1.5rem',
      cursor: 'pointer',
      padding: '0 10px',
    },
    title: {
      fontSize: '2rem',
      margin: 0,
    },
    dateScroll: {
      display: 'flex',
      gap: '1rem',
      overflowX: 'auto',
      paddingBottom: '1rem',
      marginBottom: '2rem',
      borderBottom: `1px solid ${colors.border}`,
    },
    dateTab: {
      padding: '10px 20px',
      borderRadius: '20px',
      cursor: 'pointer',
      whiteSpace: 'nowrap',
      transition: 'all 0.2s',
      fontWeight: 'bold',
      border: 'none',
    },
    venueCard: {
      backgroundColor: colors.card,
      borderRadius: '8px',
      padding: '1.5rem',
      marginBottom: '1.5rem',
      boxShadow: '0 4px 6px rgba(0,0,0,0.2)',
    },
    venueHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'baseline',
      marginBottom: '1rem',
      borderBottom: `1px solid ${colors.border}`,
      paddingBottom: '0.5rem',
    },
    venueName: {
      fontSize: '1.2rem',
      fontWeight: 'bold',
      color: colors.accent,
    },
    venueAddress: {
      fontSize: '0.9rem',
      color: colors.textSecondary,
    },
    showGrid: {
      display: 'flex',
      flexWrap: 'wrap',
      gap: '1rem',
    },
    timeButton: {
      backgroundColor: 'transparent',
      border: `1px solid ${colors.accent}`,
      color: colors.text,
      padding: '10px 16px',
      borderRadius: '4px',
      cursor: 'pointer',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      minWidth: '100px',
      transition: 'background 0.2s',
    },
    timeText: {
      fontSize: '1rem',
      fontWeight: 'bold',
    },
    formatText: {
      fontSize: '0.75rem',
      color: colors.textSecondary,
      marginTop: '4px',
    },
    loading: { textAlign: 'center', padding: '2rem', color: colors.textSecondary },
  };

  if (loading) return <div style={styles.container}><div style={styles.loading}>Loading Showtimes...</div></div>;
  if (error) return <div style={styles.container}><div style={styles.loading}>{error}</div></div>;

  const currentVenues = schedule && selectedDate ? schedule[selectedDate] : [];

  return (
    <div style={styles.container}>
      {/* Header with Back Button */}
      <div style={styles.header}>
        <button onClick={handleBack} style={styles.backButton}>←</button>
        <h1 style={styles.title}>{movieTitle}</h1>
      </div>

      {/* Date Selectors */}
      <div style={styles.dateScroll}>
        {dates.map(date => (
          <button
            key={date}
            onClick={() => setSelectedDate(date)}
            style={{
              ...styles.dateTab,
              backgroundColor: selectedDate === date ? colors.accent : 'transparent',
              color: selectedDate === date ? colors.bg : colors.text,
              border: selectedDate === date ? 'none' : `1px solid ${colors.textSecondary}`,
            }}
          >
            {formatDate(date)}
          </button>
        ))}
      </div>

      {/* Venues List */}
      <div>
        {currentVenues.length === 0 ? (
          <p style={{textAlign: 'center', color: colors.textSecondary}}>No shows available for this date.</p>
        ) : (
          currentVenues.map(venue => (
            <div key={venue.venue_id} style={styles.venueCard}>
              <div style={styles.venueHeader}>
                <span style={styles.venueName}>{venue.name}</span>
                <span style={styles.venueAddress}>Info: {venue.address}</span>
              </div>
              
              <div style={styles.showGrid}>
                {venue.shows.map(show => (
                  <button 
                    key={show.id} 
                    style={styles.timeButton}
                    onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'rgba(0, 173, 181, 0.1)'}
                    onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                    onClick={() => alert(`Selected Show ID: ${show.id}`)}
                  >
                    <span style={styles.timeText}>{formatTime(show.start_time)}</span>
                    <span style={styles.formatText}>{show.format} • {show.language}</span>
                  </button>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MovieSchedule;