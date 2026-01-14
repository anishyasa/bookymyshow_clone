from django.db import models
from django.db.models import JSONField, UniqueConstraint

# see this for why textfield over varchar https://stackoverflow.com/questions/4848964/difference-between-text-and-varchar-character-varying

class City(models.Model):
    """
    Represents the geographical location.
    """
    name = models.TextField(unique=True, db_index=True)
    state = models.TextField()
    
    class Meta:
        verbose_name_plural = "Cities"

    def __str__(self):
        return self.name

class ShowFormat(models.Model):
    """
    Defines the physical capability of a screen (e.g., IMAX, 2D, 4DX, Dolby Atmos).
    """
    name = models.TextField(unique=True) # e.g., "IMAX 3D"
    
    def __str__(self):
        return self.name

class Venue(models.Model):
    """
    The physical building (e.g., PVR Nexus Koramangala).
    """
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='venues')
    name = models.TextField(db_index=True)
    address = models.TextField()
    pincode = models.CharField(max_length=6)
    
    class Meta:
        # Frequent query "Venues in City X"
        indexes = [
            models.Index(fields=['city', 'name']),
        ]

    def __str__(self):
        return f"{self.name} ({self.city.name})"
    

class SeatType(models.Model):
    """
    Master data for seat categories (e.g., "VIP", "Recliner", "Balcony").
    Can be global or specific to a venue.
    """
    venue = models.ForeignKey(
        Venue, 
        on_delete=models.CASCADE, 
        related_name='seat_types',
        null=True, 
        blank=True
    ) 
    # If venue is NULL, it's a "Global Standard" type (e.g., generic "Standard").
    # If venue is SET, it's a custom type for that specific theatre.

    name = models.TextField() # e.g., "Royal Recliner"
    description = models.TextField(blank=True)

    class Meta:
        # Prevent duplicate seat names within the same venue
        unique_together = [['venue', 'name']]
        verbose_name = "Seat Type"
        verbose_name_plural = "Seat Types"

    def __str__(self):
        if self.venue:
            return f"{self.name} ({self.venue.name})"
        return self.name

class Screen(models.Model):
    """
    A specific auditorium inside a Venue.
    Contains the physical seat layout and hardware capabilities.
    """
    venue = models.ForeignKey(Venue, on_delete=models.PROTECT, related_name='screens')
    name = models.TextField() # e.g., "Audi 1", "Gold Class Screen"
    supported_formats = models.ManyToManyField(ShowFormat, related_name='capable_screens')
    
    # The Template: Defines the rows, columns, and gaps.
    # example: {
        # "rows": [
        #     {"row_code": "A", "seat_type_id": 5, "seats": [1, 2, 3]}, 
        #     {"row_code": "B", "seat_type_id": 2, "seats": [1, 2, 3]}
        # ]
        # }
    seating_layout_template = JSONField() 
    total_capacity = models.IntegerField()
    
    class Meta:
        # Constraint: You can't have two "Screen 1"s in the same Venue
        unique_together = [['venue', 'name']]

    def __str__(self):
        return f"{self.name} - {self.venue.name}"
    
class Seat(models.Model):
    """Physical seat in a screen"""
    screen = models.ForeignKey(Screen, on_delete=models.CASCADE, related_name='seats')
    seat_type = models.ForeignKey(SeatType, on_delete=models.PROTECT)
    
    row = models.TextField()
    seat_number = models.IntegerField()
    is_active = models.BooleanField(default=True)  # For maintenance blocking
    
    class Meta:
        constraints = [
            UniqueConstraint(fields=['screen', 'row', 'seat_number'], name='unique_seat_per_screen')
        ]
