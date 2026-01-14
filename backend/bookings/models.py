from django.db import models
from users.models import User
from shows.models import Show, ShowSeat

class SeatReservation(models.Model):
    """Temporary lock on a ShowSeat while user is paying"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    show_seat = models.ForeignKey(ShowSeat, on_delete=models.CASCADE)
    
    reserved_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['expires_at', 'is_active']),
            models.Index(fields=['show_seat', 'is_active']),
        ]

    def __str__(self):
        return f"Reservation: {self.user} - {self.show_seat}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bookings')
    show = models.ForeignKey(Show, on_delete=models.PROTECT, related_name='bookings')
    
    # ManyToMany: A booking has multiple ShowSeats
    # A ShowSeat can appear in multiple bookings (failed/cancelled history)
    # But application logic ensures only ONE confirmed booking per ShowSeat
    show_seats = models.ManyToManyField(ShowSeat, related_name='bookings')
    
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    booking_code = models.CharField(max_length=20, unique=True, db_index=True)
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending', 
        db_index=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['show', 'status']),
        ]

    def __str__(self):
        return f"Booking {self.booking_code} ({self.status})"


class Transaction(models.Model):
    STATUS_CHOICES = [
        ('success', 'Success'), 
        ('failed', 'Failed'), 
        ('pending', 'Pending')
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('upi', 'UPI'),
        ('card', 'Credit/Debit Card'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]
    
    booking = models.ForeignKey(Booking, on_delete=models.PROTECT, related_name='transactions')
    
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    
    gateway_transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['booking', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Txn {self.gateway_transaction_id} for {self.booking.booking_code}"