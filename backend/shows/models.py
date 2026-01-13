from django.db import models

from django.db import models
from django.core.exceptions import ValidationError

from infrastructure.models import Screen, ShowFormat, SeatType, Venue
from events.models import Event

class Show(models.Model):
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name='shows')
    screen = models.ForeignKey(Screen, on_delete=models.PROTECT, related_name='shows')
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name='shows')
    
    show_format = models.ForeignKey(
        ShowFormat, 
        on_delete=models.PROTECT, 
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