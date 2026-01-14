import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';

interface Seat {
  id: number;
  row: string;
  number: number;
  type: string;
  price: string;
  is_available: boolean;
}

interface SeatType {
  type: string;
  price: string;
}

const SeatSelection: React.FC = () => {
  const { showId } = useParams<{ showId: string }>();
  const navigate = useNavigate();
  const location = useLocation();

  const movieTitle = (location.state as any)?.movieTitle || 'Movie';
  const venueName = (location.state as any)?.venueName || 'Venue';

  const [seats, setSeats] = useState<Seat[]>([]);
  const [selectedSeatIds, setSelectedSeatIds] = useState<number[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [booking, setBooking] = useState<boolean>(false);
  const [bookingError, setBookingError] = useState<string>('');
  const [bookingSuccess, setBookingSuccess] = useState<boolean>(false);

  const colors = {
    bg: '#222831',
    card: '#393E46',
    accent: '#00ADB5',
    text: '#EEEEEE',
    textSecondary: '#B0B0B0',
    border: '#2D333B',
    unavailable: '#4A4A4A',
    available: '#5A5A5A',
  };

  useEffect(() => {
    fetchSeats();
  }, [showId]);

  const fetchSeats = async () => {
    setLoading(true);
    const token = localStorage.getItem('access_token');

    try {
      const response = await fetch(`http://localhost:8000/api/shows/show-seats/${showId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) throw new Error('Failed to load seats');

      const data: Seat[] = await response.json();
      setSeats(data);
    } catch (err) {
      setError('Could not fetch seats.');
    } finally {
      setLoading(false);
    }
  };

  const handleSeatClick = (seat: Seat) => {
    if (!seat.is_available) return;

    if (selectedSeatIds.includes(seat.id)) {
      setSelectedSeatIds(selectedSeatIds.filter(id => id !== seat.id));
    } else {
      setSelectedSeatIds([...selectedSeatIds, seat.id]);
    }
  };

  const handleBooking = async () => {
    if (selectedSeatIds.length === 0) return;

    setBooking(true);
    setBookingError('');
    const token = localStorage.getItem('access_token');

    try {
      const response = await fetch('http://localhost:8000/api/bookings/book/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          show_id: Number(showId),
          seat_ids: selectedSeatIds
        })
      });

      const data = await response.json(); // Parse response body first

      if (response.ok) {
        setBookingSuccess(true);
      } else {
        if (response.status === 409) {
          // SeatUnavailableException
          setBookingError(`Unavailable: ${data.detail || 'Some seats were just taken.'}`);
          fetchSeats();
          setSelectedSeatIds([]);
        } else if (response.status === 402) {
          // PaymentGatewayException
          setBookingError(`Payment Failed: ${data.detail || 'Please check your card.'}`);
        } else {
          setBookingError(data.detail || 'Booking failed. Please try again.');
        }
      }
    } catch (err) {
      setBookingError('Network error. Check your connection.');
    } finally {
      setBooking(false);
    }
  };

  const handleBackToSchedule = () => {
    navigate(-1);
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  const seatsByRow = seats.reduce((acc, seat) => {
    if (!acc[seat.row]) acc[seat.row] = [];
    acc[seat.row].push(seat);
    return acc;
  }, {} as { [key: string]: Seat[] });

  const rows = Object.keys(seatsByRow).sort();

  const seatTypes: SeatType[] = Array.from(
    new Map(seats.map(seat => [seat.type, { type: seat.type, price: seat.price }])).values()
  );

  const selectedSeats = seats.filter(seat => selectedSeatIds.includes(seat.id));
  const totalPrice = selectedSeats.reduce((sum, seat) => sum + parseFloat(seat.price), 0);

  const styles: { [key: string]: React.CSSProperties } = {
    container: {
      minHeight: '100vh',
      backgroundColor: colors.bg,
      color: colors.text,
      paddingBottom: '120px',
    },
    header: {
      display: 'flex',
      alignItems: 'center',
      gap: '1rem',
      padding: '1.5rem 2rem',
      borderBottom: `1px solid ${colors.border}`,
      backgroundColor: colors.card,
    },
    backButton: {
      background: 'none',
      border: 'none',
      color: colors.accent,
      fontSize: '1.5rem',
      cursor: 'pointer',
      padding: 0,
    },
    headerText: {
      fontSize: '1.5rem',
      fontWeight: 'bold',
      margin: 0,
    },
    content: {
      maxWidth: '900px',
      margin: '0 auto',
      padding: '2rem',
    },
    legendSection: {
      marginBottom: '2rem',
      padding: '1rem',
      backgroundColor: colors.card,
      borderRadius: '8px',
    },
    legendTitle: {
      fontSize: '0.9rem',
      color: colors.textSecondary,
      marginBottom: '1rem',
    },
    legendRow: {
      display: 'flex',
      gap: '2rem',
      flexWrap: 'wrap',
    },
    legendItem: {
      display: 'flex',
      alignItems: 'center',
      gap: '0.5rem',
    },
    legendBox: {
      width: '24px',
      height: '24px',
      borderRadius: '4px',
      border: `2px solid ${colors.accent}`,
    },
    screenSection: {
      textAlign: 'center',
      marginBottom: '2rem',
    },
    screenIndicator: {
      display: 'inline-block',
      padding: '0.5rem 3rem',
      backgroundColor: colors.card,
      borderRadius: '4px',
      fontSize: '0.9rem',
      color: colors.textSecondary,
      border: `1px solid ${colors.border}`,
    },
    seatsSection: {
      display: 'flex',
      flexDirection: 'column',
      gap: '1rem',
    },
    rowContainer: {
      display: 'flex',
      alignItems: 'center',
      gap: '1rem',
    },
    rowLabel: {
      width: '30px',
      fontSize: '1rem',
      fontWeight: 'bold',
      color: colors.textSecondary,
    },
    seatsRow: {
      display: 'flex',
      gap: '0.5rem',
      flexWrap: 'nowrap',
      overflowX: 'auto',
    },
    seat: {
      width: '50px',
      height: '50px',
      borderRadius: '4px',
      border: 'none',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '0.85rem',
      fontWeight: 'bold',
      cursor: 'pointer',
      transition: 'all 0.2s',
    },
    bottomBar: {
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      backgroundColor: colors.card,
      padding: '1.5rem 2rem',
      borderTop: `1px solid ${colors.border}`,
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
    },
    priceSection: {
      display: 'flex',
      flexDirection: 'column',
      gap: '0.25rem',
    },
    selectedCount: {
      fontSize: '0.9rem',
      color: colors.textSecondary,
    },
    totalPrice: {
      fontSize: '1.5rem',
      fontWeight: 'bold',
      color: colors.accent,
    },
    bookButton: {
      padding: '1rem 3rem',
      backgroundColor: colors.accent,
      color: colors.text,
      border: 'none',
      borderRadius: '4px',
      fontSize: '1.1rem',
      fontWeight: 'bold',
      cursor: 'pointer',
    },
    loading: {
      textAlign: 'center',
      padding: '4rem',
      color: colors.textSecondary,
    },
    successScreen: {
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      gap: '2rem',
      padding: '2rem',
    },
    successIcon: {
      fontSize: '4rem',
      color: colors.accent,
    },
    successTitle: {
      fontSize: '2rem',
      fontWeight: 'bold',
    },
    successMessage: {
      fontSize: '1.1rem',
      color: colors.textSecondary,
    },
    homeButton: {
      padding: '1rem 2rem',
      backgroundColor: colors.accent,
      color: colors.text,
      border: 'none',
      borderRadius: '4px',
      fontSize: '1rem',
      fontWeight: 'bold',
      cursor: 'pointer',
      marginTop: '1rem',
    },
  };

  if (bookingSuccess) {
    return (
      <div style={{ ...styles.container, ...styles.successScreen }}>
        <div style={styles.successIcon}>✓</div>
        <h1 style={styles.successTitle}>Booking Successful!</h1>
        <p style={styles.successMessage}>Your tickets have been booked.</p>
        <button onClick={handleBackToHome} style={styles.homeButton}>
          Back to Home
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>Loading seats...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={styles.container}>
        <div style={styles.loading}>{error}</div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <button onClick={handleBackToSchedule} style={styles.backButton}>←</button>
        <h1 style={styles.headerText}>{movieTitle} at {venueName}</h1>
      </div>

      <div style={styles.content}>
        <div style={styles.legendSection}>
          <div style={styles.legendTitle}>Seat Types & Prices</div>
          <div style={styles.legendRow}>
            {seatTypes.map(st => (
              <div key={st.type} style={styles.legendItem}>
                <div style={{ ...styles.legendBox, backgroundColor: colors.available }} />
                <span>{st.type} - Rs. {st.price}</span>
              </div>
            ))}
          </div>
          <div style={{ ...styles.legendRow, marginTop: '1rem' }}>
            <div style={styles.legendItem}>
              <div style={{ ...styles.legendBox, backgroundColor: colors.available }} />
              <span>Available</span>
            </div>
            <div style={styles.legendItem}>
              <div style={{ ...styles.legendBox, backgroundColor: colors.accent }} />
              <span>Selected</span>
            </div>
            <div style={styles.legendItem}>
              <div style={{ ...styles.legendBox, backgroundColor: colors.unavailable, borderColor: colors.unavailable }} />
              <span>Unavailable</span>
            </div>
          </div>
        </div>

        <div style={styles.screenSection}>
          <div style={styles.screenIndicator}>SCREEN</div>
        </div>

        <div style={styles.seatsSection}>
          {rows.map(row => (
            <div key={row} style={styles.rowContainer}>
              <div style={styles.rowLabel}>{row}</div>
              <div style={styles.seatsRow}>
                {seatsByRow[row].map(seat => {
                  const isSelected = selectedSeatIds.includes(seat.id);
                  const isAvailable = seat.is_available;

                  return (
                    <button
                      key={seat.id}
                      onClick={() => handleSeatClick(seat)}
                      style={{
                        ...styles.seat,
                        backgroundColor: !isAvailable 
                          ? colors.unavailable 
                          : isSelected 
                          ? colors.accent 
                          : colors.available,
                        cursor: !isAvailable ? 'not-allowed' : 'pointer',
                        border: isAvailable ? `2px solid ${colors.accent}` : `2px solid ${colors.unavailable}`,
                        color: isSelected ? colors.bg : colors.text,
                      }}
                      disabled={!isAvailable}
                    >
                      {row}{seat.number}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={styles.bottomBar}>
        <div style={styles.priceSection}>
          <div style={styles.selectedCount}>
            {selectedSeatIds.length} seat{selectedSeatIds.length !== 1 ? 's' : ''} selected
          </div>
          <div style={styles.totalPrice}>Total: Rs. {totalPrice.toFixed(2)}</div>
        </div>
        <div>
          {bookingError && (
            <div style={{ color: '#ff6b6b', marginBottom: '0.5rem', fontSize: '0.9rem' }}>
              {bookingError}
            </div>
          )}
          <button
            onClick={handleBooking}
            disabled={selectedSeatIds.length === 0 || booking}
            style={{
              ...styles.bookButton,
              opacity: selectedSeatIds.length === 0 || booking ? 0.5 : 1,
              cursor: selectedSeatIds.length === 0 || booking ? 'not-allowed' : 'pointer',
            }}
          >
            {booking ? 'Booking...' : 'Book Seats'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SeatSelection;