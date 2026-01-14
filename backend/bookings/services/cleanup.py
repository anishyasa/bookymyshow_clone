from django.utils import timezone
from django.db import transaction
from bookings.models import SeatReservation
from shows.models import ShowSeat

def release_expired_seats() -> int:
    """
    Releases locks on seats where the reservation timer has expired.
    Returns the number of seats released.
    """
    now = timezone.now()
    
    with transaction.atomic():
        # 1. Find the Expired Reservations
        # We verify is_active=True to avoid processing already cleaned rows
        expired_reservations = SeatReservation.objects.filter(
            is_active=True,
            expires_at__lt=now
        ).select_for_update() # Lock these rows to prevent race conditions
        
        if not expired_reservations.exists():
            return 0
        
        # 2. Extract the ShowSeat IDs that need to be freed
        # We use list() to force evaluation before we update the reservations
        seat_ids_to_free = list(
            expired_reservations.values_list('show_seat_id', flat=True)
        )
        
        # 3. Mark Reservations as Inactive (Batch Update)
        # This effectively "kills" the temporary hold
        expired_reservations.update(is_active=False)
        
        # 4. Release the ShowSeats (Batch Update)
        # CRITICAL: We only update seats that are currently 'blocked'. 
        # If a seat became 'booked' (confirmed) in the split second between 
        # checks (rare but possible), we MUST NOT flip it back to available.
        updated_count = ShowSeat.objects.filter(
            id__in=seat_ids_to_free,
            status='blocked'
        ).update(status='available')
        
    return updated_count