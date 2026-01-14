from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from infrastructure.models import Screen, ShowFormat, SeatType, Venue, Seat
from events.models import Event, Language

class Show(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name='shows')
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name='shows')
    
    # Screen is optional: Movies use screens, concerts/sports use the venue broadly
    screen = models.ForeignKey(
        Screen, 
        on_delete=models.PROTECT, 
        related_name='shows',
        null=True,
        blank=True
    )
    show_format = models.ForeignKey(
        ShowFormat, 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True
    )
    language = models.ForeignKey(
        Language,
        on_delete=models.PROTECT,
        related_name='shows',
        null=True,
        blank=True
    )
    
    show_datetime = models.DateTimeField(db_index=True)
    end_datetime = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['venue', 'show_datetime']),
        ]

    def clean(self):
        """
        Complex Validation Logic:
        1. If Event is a MOVIE, show_format is REQUIRED.
        2. If Event is NOT a MOVIE, show_format should be NULL.
        3. If show_format exists, the Screen must support it.
        4. Language must be one of the Event's available languages.
        """
        # Ensure relationships exist before validating (handles form partial data)
        if not (hasattr(self, 'event') and hasattr(self, 'screen')):
            return

        is_movie = (self.event.event_type.name.lower() == 'movie')

        # Rule 1: Movies require a format (2D, IMAX, etc.)
        if is_movie and not self.show_format:
            raise ValidationError({
                'show_format': _("Movies must have a specific projection format (e.g., 2D, IMAX).")
            })

        # Rule 2: Non-movies should not have a format (Optional strictness)
        if not is_movie and self.show_format:
             raise ValidationError({
                'show_format': _(f"Events of type '{self.event.event_type.name}' should not have a projection format.")
            })

        # Rule 3: Hardware Capability Check (Only if format is assigned)
        if self.show_format:
            if not self.screen.supported_formats.filter(id=self.show_format.id).exists():
                raise ValidationError({
                    'show_format': _(f"Screen '{self.screen.name}' does not support format '{self.show_format.name}'.")
                })
        
        # Rule 4: Language validation
        if self.language:
            if not self.event.languages.filter(id=self.language.id).exists():
                raise ValidationError({
                    'language': _(f"Language '{self.language.name}' is not available for event '{self.event.title}'.")
                })
                
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class ShowSeatTypePrice(models.Model):
    """
    Dynamic Pricing: Assigns a price to a specific SeatType for a specific Show.
    """
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='price_config')
    seat_type = models.ForeignKey(SeatType, on_delete=models.PROTECT)
    
    price = models.DecimalField(max_digits=8, decimal_places=2)
    
    class Meta:
        # Constraint: You cannot have two prices for "Gold" in the same show.
        unique_together = ['show', 'seat_type']
        indexes = [
            models.Index(fields=['show', 'seat_type']),
        ]
    
    def __str__(self):
        return f"{self.show} - {self.seat_type.name}: {self.price}"
    
class ShowSeat(models.Model):
    """Per-show availability and pricing - EPHEMERAL"""
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('booked', 'Booked'),
        ('blocked', 'Blocked'),
    ]
    
    show = models.ForeignKey(Show, on_delete=models.CASCADE, related_name='show_seats')
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT)
    
    price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available', 
        db_index=True
    )
    version = models.IntegerField(default=0)  # Optimistic locking
    modified_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['show', 'seat'], name='unique_show_seat')
        ]
        indexes = [
            models.Index(fields=['show', 'status']),
        ]

    def __str__(self):
        return f"{self.show} - {self.seat}"