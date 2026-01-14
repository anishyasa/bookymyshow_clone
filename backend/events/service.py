"""
Unified service layer for movies - handles caching, DB queries, and business logic
"""

import json
import logging
from datetime import date, datetime, time, timedelta
from typing import List, Optional

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db.models import Q, QuerySet

from infrastructure.models import City, ShowFormat
from events.models import Event, EventType, Language
from shows.models import Show

logger = logging.getLogger(__name__)


def _get_cache_key(
    city_id: int,
    target_date: date,
    language_filter: Optional[str],
    format_filter: Optional[str],
) -> str:
    """Generate cache key for homepage"""
    prefix = getattr(settings, "HOMEPAGE_CACHE_PREFIX", "movies:homepage")
    lang = language_filter.lower().strip() if language_filter else "all"
    fmt = format_filter.lower().strip() if format_filter else "all"
    date_str = target_date.strftime("%Y-%m-%d")
    return f"{prefix}:city:{city_id}:date:{date_str}:lang:{lang}:format:{fmt}"


def _calculate_ttl(target_date: date) -> int:
    """Calculate intelligent TTL based on date"""
    today = date.today()
    now = datetime.now()

    if target_date < today:
        return getattr(settings, "HOMEPAGE_CACHE_PAST_DATE_TTL", 604800)

    if target_date == today:
        midnight = datetime.combine(today + timedelta(days=1), time.min)
        seconds_until_midnight = int((midnight - now).total_seconds())
        return max(seconds_until_midnight, 60)

    midnight = datetime.combine(target_date + timedelta(days=1), time.min)
    seconds_until_midnight = int((midnight - now).total_seconds())
    return max(seconds_until_midnight, 60)


# ============================================================================
# DATABASE QUERIES
# ============================================================================


def _get_movies_with_shows(city_id: int, target_date: date) -> QuerySet:
    """Get all movies with active shows in city on date"""
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())

    queryset = (
        Event.objects.filter(
            event_type__name__iexact="Movie",
            shows__venue__city_id=city_id,
            shows__show_datetime__gte=start_datetime,
            shows__show_datetime__lte=end_datetime,
            is_active=True,
            shows__is_active=True,
        )
        .distinct()
        .select_related("event_type")
        .prefetch_related("languages")
    )

    return queryset


def _filter_by_language(
    movies_qs: QuerySet, language: str, city_id: int, target_date: date
) -> QuerySet:
    """Filter movies by language"""
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())

    return movies_qs.filter(
        shows__language__name__iexact=language,
        shows__venue__city_id=city_id,
        shows__show_datetime__gte=start_datetime,
        shows__show_datetime__lte=end_datetime,
        shows__is_active=True,
    ).distinct()


def _filter_by_format(
    movies_qs: QuerySet, format_name: str, city_id: int, target_date: date
) -> QuerySet:
    """Filter movies by format"""
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())

    return movies_qs.filter(
        shows__show_format__name__iexact=format_name,
        shows__venue__city_id=city_id,
        shows__show_datetime__gte=start_datetime,
        shows__show_datetime__lte=end_datetime,
        shows__is_active=True,
    ).distinct()


def _get_movie_languages(event_id: int, city_id: int, target_date: date) -> List[str]:
    """Get distinct languages for a movie in city"""
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())

    languages = (
        Show.objects.filter(
            event_id=event_id,
            venue__city_id=city_id,
            show_datetime__gte=start_datetime,
            show_datetime__lte=end_datetime,
            is_active=True,
            language__isnull=False,
        )
        .select_related("language")
        .values_list("language__name", flat=True)
        .distinct()
        .order_by("language__name")
    )

    return list(languages)


def _get_movie_formats(event_id: int, city_id: int, target_date: date) -> List[str]:
    """Get distinct formats for a movie in city"""
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())

    formats = (
        Show.objects.filter(
            event_id=event_id,
            venue__city_id=city_id,
            show_datetime__gte=start_datetime,
            show_datetime__lte=end_datetime,
            is_active=True,
            show_format__isnull=False,
        )
        .select_related("show_format")
        .values_list("show_format__name", flat=True)
        .distinct()
        .order_by("show_format__name")
    )

    return list(formats)


def _count_movie_shows(event_id: int, city_id: int, target_date: date) -> int:
    """Count shows for a movie in city"""
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())

    return Show.objects.filter(
        event_id=event_id,
        venue__city_id=city_id,
        show_datetime__gte=start_datetime,
        show_datetime__lte=end_datetime,
        is_active=True,
    ).count()


def _build_movie_dict(movie: Event, city_id: int, target_date: date) -> dict:
    """Build movie dict with aggregated show data"""
    languages = _get_movie_languages(movie.id, city_id, target_date)
    formats = _get_movie_formats(movie.id, city_id, target_date)
    show_count = _count_movie_shows(movie.id, city_id, target_date)

    return {
        "id": movie.id,
        "title": movie.title,
        "poster_url": movie.poster_url,
        "duration_minutes": movie.duration_minutes,
        "description": movie.description,
        "genres": movie.genre if isinstance(movie.genre, list) else [],
        "cast": movie.cast if isinstance(movie.cast, list) else [],
        "crew": movie.crew if isinstance(movie.crew, list) else [],
        "available_languages": languages,
        "available_formats": formats,
        "show_count": show_count,
    }


def _extract_filters(movies_data: List[dict]) -> dict:
    """Extract unique languages and formats for filter options"""
    all_languages = set()
    all_formats = set()

    for movie in movies_data:
        all_languages.update(movie.get("available_languages", []))
        all_formats.update(movie.get("available_formats", []))

    return {
        "available_languages": sorted(list(all_languages)),
        "available_formats": sorted(list(all_formats)),
    }


def get_homepage_movies(
    city_id: int,
    target_date: Optional[date] = None,
    language_filter: Optional[str] = None,
    format_filter: Optional[str] = None,
    use_cache: bool = True,
) -> dict:
    """
    Fetch all movies screening in a city with caching

    Args:
        city_id: ID of the city
        target_date: Date to check for shows (default: today)
        language_filter: Optional language name filter
        format_filter: Optional format name filter
        use_cache: Whether to use Redis cache (default: True)

    Returns:
        {
            'movies': List[dict],
            'filters': {'available_languages': [...], 'available_formats': [...]},
            'metadata': {'cached': bool, 'city_id': int, 'date': str, 'total_movies': int}
        }

    Raises:
        ValidationError: If city doesn't exist
    """
    if not City.objects.filter(id=city_id).exists():
        raise ValidationError(f"City with id {city_id} does not exist")

    if target_date is None:
        target_date = date.today()

    cache_key = _get_cache_key(city_id, target_date, language_filter, format_filter)

    if use_cache:
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                logger.info(f"Cache HIT for key: {cache_key}")
                cached_data["metadata"]["cached"] = True
                return cached_data
        except Exception as e:
            logger.error(f"Error fetching from cache: {e}", exc_info=True)

    logger.info(f"Cache MISS - Fetching from DB for city {city_id} on {target_date}")
    movies_qs = _get_movies_with_shows(city_id, target_date)

    if language_filter:
        movies_qs = _filter_by_language(
            movies_qs, language_filter, city_id, target_date
        )

    if format_filter:
        movies_qs = _filter_by_format(movies_qs, format_filter, city_id, target_date)

    movies_data = [
        _build_movie_dict(movie, city_id, target_date) for movie in movies_qs
    ]
    filter_options = _extract_filters(movies_data)

    response_data = {
        "movies": movies_data,
        "filters": filter_options,
        "metadata": {
            "cached": False,
            "city_id": city_id,
            "date": target_date.strftime("%Y-%m-%d"),
            "total_movies": len(movies_data),
        },
    }

    if use_cache:
        try:
            ttl = _calculate_ttl(target_date)
            cache.set(cache_key, response_data, ttl)
            logger.info(f"Cached data for key: {cache_key} with TTL: {ttl}s")
        except Exception as e:
            logger.error(f"Error setting cache: {e}", exc_info=True)

    return response_data
