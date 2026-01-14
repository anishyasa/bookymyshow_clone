import uuid
import time
from decimal import Decimal
from django.db import transaction, models
from django.utils import timezone
from datetime import timedelta

from .models import ShowSeat, Booking, SeatReservation, Transaction
from .exceptions import SeatUnavailableException, PaymentGatewayException

class BookingService:
    @staticmethod
    def process_booking_request(user, show_id, seat_ids):
        """
        Orchestrator function.
        1. Atomically reserves seats & creates pending booking.
        2. Calls external payment gateway (outside DB lock).
        3. Confirms or fails the booking based on payment result.
        """
        # Step 1: Reserve Seats & Create Booking (Atomic)
        try:
            booking = BookingService._reserve_seats_and_create_booking(user, show_id, seat_ids)
        except SeatUnavailableException as e:
            raise e

        # Step 2: Payment (External - No DB Lock)
        try:
            txn_id = BookingService._mock_payment_provider(booking.total_amount)
            return BookingService._confirm_booking_success(booking, txn_id)
            
        except PaymentGatewayException:
            BookingService._handle_booking_failure(booking)
            raise

    @staticmethod
    @transaction.atomic
    def _reserve_seats_and_create_booking(user, show_id, seat_ids):
        """
        Uses Optimistic Locking to reserve seats.
        If ANY seat fails to lock, the entire transaction rolls back.
        """
        seats = ShowSeat.objects.filter(id__in=seat_ids, show_id=show_id)
        if len(seats) != len(seat_ids):
            raise SeatUnavailableException("One or more invalid seats provided.")

        total_amount = Decimal('0.00')
        locked_seats = []

        for seat in seats:
            # Atomic Update: "Flip status only if version matches"
            rows_updated = ShowSeat.objects.filter(
                id=seat.id,
                version=seat.version,
                status='available'
            ).update(
                status='reserved',
                version=models.F('version') + 1
            )

            if rows_updated == 0:
                #"All-or-Nothing" booking: even if 1 seat is taken, roll back. 
                # Raising exception triggers rollback automatically via django's transaction.atomic wrapper
                raise SeatUnavailableException(f"Seat {seat.seat.number} is no longer available.")
            
            seat.refresh_from_db()
            locked_seats.append(seat)
            total_amount += seat.price

        expiry_time = timezone.now() + timedelta(minutes=10)
        reservations = [
            SeatReservation(
                user=user,
                show_seat=seat,
                expires_at=expiry_time
            ) for seat in locked_seats
        ]
        SeatReservation.objects.bulk_create(reservations)

        booking = Booking.objects.create(
            user=user,
            show_id=show_id,
            total_amount=total_amount,
            booking_code=str(uuid.uuid4()).replace('-', '').upper()[:8],
            status='pending'
        )
        booking.show_seats.set(locked_seats)
        
        return booking

    @staticmethod
    def _mock_payment_provider(amount):
        """Simulates external API call."""
        time.sleep(1)  # Simulate network latency
        
        # Simulate 90% success rate
        # In real world, this would be requests.post(...)
        if amount > 0:
            return f"TXN_{uuid.uuid4().hex[:12].upper()}"
        else:
            raise PaymentGatewayException("Payment declined.")

    @staticmethod
    @transaction.atomic
    def _confirm_booking_success(booking, gateway_txn_id):
        """Finalizes booking after successful payment."""
        booking.status = 'confirmed'
        booking.confirmed_at = timezone.now()
        booking.save()

        booking.show_seats.update(status='booked')

        Transaction.objects.create(
            booking=booking,
            amount=booking.total_amount,
            payment_method='card',
            gateway_transaction_id=gateway_txn_id,
            status='success'
        )
        
        SeatReservation.objects.filter(
            show_seat__in=booking.show_seats.all(),
            is_active=True
        ).update(is_active=False)

        return booking

    @staticmethod
    @transaction.atomic
    def _handle_booking_failure(booking):
        """Releases locks if payment fails."""
        booking.status = 'failed'
        booking.save()
        booking.show_seats.update(status='available')

        Transaction.objects.create(
            booking=booking,
            amount=booking.total_amount,
            payment_method='card',
            gateway_transaction_id=f"FAIL_{uuid.uuid4().hex[:8]}",
            status='failed'
        )
        SeatReservation.objects.filter(
            show_seat__in=booking.show_seats.all(),
            is_active=True
        ).update(is_active=False)