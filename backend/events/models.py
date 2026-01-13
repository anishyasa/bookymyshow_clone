from django.db import models

from django.db import models
from django.db.models import JSONField

class Language(models.Model):
    name = models.TextField(unique=True)
    
    def __str__(self):
        return self.name

class EventType(models.Model):
    # e.g., Movie, Concert, Sports
    name = models.TextField(unique=True) 
    
    def __str__(self):
        return self.name

class Event(models.Model):
    title = models.TextField(db_index=True)
    event_type = models.ForeignKey(EventType, on_delete=models.PROTECT)
    languages = models.ManyToManyField(Language, related_name='events')
    description = models.TextField(blank=True)
    
    # Metadata
    duration_minutes = models.IntegerField()
    poster_url = models.TextField()
    
    trailers = JSONField(default=dict, blank=True)
    genre = JSONField(default=list, blank=True)
    cast = JSONField(default=list, blank=True)
    crew = JSONField(default=list, blank=True)
    
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
