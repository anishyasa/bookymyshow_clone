from django.shortcuts import render
from django.utils import timezone
from django.db.models import QuerySet

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, serializers

from typing import List, Dict
import datetime
from collections import defaultdict
from typing import List, Dict, Any, Tuple, Optional

from shows.models import Show, ShowSeat
from infrastructure.models import Venue

class ScheduleFilterSerializer(serializers.Serializer):
    """
    Validates query parameters for the schedule API.
    """

    city_id = serializers.IntegerField(
        required=True, help_text="The ID of the city to filter shows."
    )
    date = serializers.DateField(
        required=False,
        format="%Y-%m-%d",
        help_text="Start date (YYYY-MM-DD). Defaults to today if omitted.",
    )


class MovieScheduleView(APIView):
    """
    GET /api/movies/{event_id}/schedule/?city_id=1&date=2023-11-01
    """

    def get(self, request, event_id):
        serializer = ScheduleFilterSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        city_id = serializer.validated_data["city_id"]
        start_date_obj = serializer.validated_data.get("date")
        start_date_str = str(start_date_obj) if start_date_obj else None
        schedule_data = get_weekly_schedule(
            event_id=event_id, city_id=city_id, start_date_str=start_date_str
        )

        return Response(
            {
                "status": "success",
                "event_id": event_id,
                "city_id": city_id,
                "schedule": schedule_data,
            },
            status=status.HTTP_200_OK,
        )


def get_weekly_schedule(
    event_id: int, city_id: int, start_date_str: Optional[str] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Orchestrator: Fetches and groups the weekly schedule for a movie in a city.

    Returns structure:
    {
        "2023-11-01": [
            {
                "venue_id": 101,
                "name": "PVR Nexus",
                "shows": [
                    {"id": 505, "start_time": "14:30", "end_time": "17:15", ...},
                    ...
                ]
            },
            ...
        ]
    }
    """
    # 1. Validate and calculate timeframe
    start_dt, end_dt = _calculate_date_range(start_date_str)

    # 2. Optimized DB Fetch
    raw_shows = _fetch_raw_shows(event_id, city_id, start_dt, end_dt)

    # 3. Transform / Grouping
    schedule_data = _group_shows_by_date_and_venue(raw_shows)

    return schedule_data


def _calculate_date_range(
    start_date_str: Optional[str],
) -> Tuple[datetime.datetime, datetime.datetime]:
    """
    Parses input date or defaults to now. Returns range for 7 days.
    """
    if start_date_str:
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            # Fallback could be raised as error, but defaulting to today is robust
            start_date = timezone.localdate()
    else:
        start_date = timezone.localdate()

    # Calculate 7-day window
    end_date = start_date + datetime.timedelta(days=7)

    # Convert to aware datetimes for DB filtering
    # Using min/max time to cover the full days
    start_dt = timezone.make_aware(
        datetime.datetime.combine(start_date, datetime.time.min)
    )
    end_dt = timezone.make_aware(datetime.datetime.combine(end_date, datetime.time.max))

    return start_dt, end_dt


def _fetch_raw_shows(
    event_id: int, city_id: int, start_dt: datetime.datetime, end_dt: datetime.datetime
) -> QuerySet:
    """
    Fetches flat list of shows with all related FKs needed for display.
    """
    return (
        Show.objects.filter(
            event_id=event_id,
            venue__city_id=city_id,
            is_active=True,
            show_datetime__gte=start_dt,
            show_datetime__lte=end_dt,
        )
        .select_related("venue", "show_format", "language")
        .order_by("show_datetime", "venue__name")
    )


def _group_shows_by_date_and_venue(shows: QuerySet) -> Dict[str, List[Dict[str, Any]]]:
    """
    Transforms flat DB rows into: Date -> List[VenueDict].
    """
    # Temporary storage: Date -> VenueID -> {'venue': Data, 'shows': [List]}
    grouped_map = defaultdict(dict)

    for show in shows:
        # Group Key 1: Date String
        # Using local date for display grouping
        date_key = timezone.localtime(show.show_datetime).strftime("%Y-%m-%d")

        venue_id = show.venue_id

        # Initialize Venue bucket if not exists for this date
        if venue_id not in grouped_map[date_key]:
            grouped_map[date_key][venue_id] = _serialize_venue_structure(show.venue)

        # Append serialized show
        grouped_map[date_key][venue_id]["shows"].append(_serialize_show(show))

    # Final formatting: Convert inner dict values to list
    # Result: {'2023-10-01': [ {VenueData...}, {VenueData...} ] }
    final_output = {}
    for date_key, venue_dict in grouped_map.items():
        final_output[date_key] = list(venue_dict.values())

    return final_output


def _serialize_venue_structure(venue: Venue) -> Dict[str, Any]:
    """
    Creates the container structure for a venue.
    """
    return {
        "venue_id": venue.id,
        "name": venue.name,
        "address": venue.address,
        "shows": [],
    }


def _serialize_show(show: Show) -> Dict[str, Any]:
    """
    Format specific show attributes including start and end times.
    """

    # Helper to format HH:MM safely
    def format_time(dt):
        return timezone.localtime(dt).strftime("%H:%M")

    return {
        "id": show.id,
        "start_time": format_time(show.show_datetime),
        "end_time": format_time(show.end_datetime),
        "format": show.show_format.name if show.show_format else None,
        "language": show.language.name if show.language else None,
    }


def get_show_seat_map(show_id: int) -> List[Dict]:
    """
    Returns the public seat map for a show.
    Relying purely on ShowSeat.status for availability.
    
    Status Mapping:
    - 'available' -> is_available: True
    - 'booked'    -> is_available: False
    - 'blocked'   -> is_available: False (Assumes bg worker cleans these up)
    """
    seats = _fetch_seats_from_db(show_id)
    return [
        _serialize_seat(seat) 
        for seat in seats
    ]

def _fetch_seats_from_db(show_id: int) -> QuerySet[ShowSeat]:
    """
    Fetches all seats for the show, joining relevant Seat and SeatType data.
    """
    return (
        ShowSeat.objects
        .filter(show_id=show_id)
        .select_related('seat', 'seat__seat_type')
        .order_by('seat__row', 'seat__seat_number')
    )

def _serialize_seat(show_seat: ShowSeat) -> Dict:
    """
    Transforms a ShowSeat model instance into a clean dictionary.
    """
    return {
        'id': show_seat.id,
        'row': show_seat.seat.row,
        'number': show_seat.seat.seat_number,
        'type': show_seat.seat.seat_type.name,
        'price': str(show_seat.price), 
        'is_available': show_seat.status == 'available'
    }


class ShowSeatListView(APIView):
    def get(self, request, show_id):
        data = get_show_seat_map(show_id=show_id)
        return Response(data)