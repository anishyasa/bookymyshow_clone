from django.shortcuts import render

"""
API Views for movies
"""
import logging
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .service import get_homepage_movies

logger = logging.getLogger(__name__)


class MovieHomepageView(APIView):
    """
    API endpoint to fetch all movies currently screening in a city
    
    Query Parameters:
        - city_id (int, required): City ID
        - date (str, optional): Target date (YYYY-MM-DD, defaults to today)
        - language (str, optional): Filter by language
        - format (str, optional): Filter by show format
    """
    
    def get(self, request):
        """Handle GET request for movies homepage"""
        # Parse query parameters
        city_id = int(request.query_params['city_id'])
        date_str = request.query_params.get('date')
        language_filter = request.query_params.get('language')
        format_filter = request.query_params.get('format')
        
        # Parse date if provided
        target_date = None
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        
        # Call service and return response
        data = get_homepage_movies(
            city_id=city_id,
            target_date=target_date,
            language_filter=language_filter,
            format_filter=format_filter,
            use_cache=True
        )
        
        logger.info(
            f"Fetched {data['metadata']['total_movies']} movies "
            f"for city {city_id} (cached: {data['metadata']['cached']})"
        )
        
        return Response(data, status=status.HTTP_200_OK)
