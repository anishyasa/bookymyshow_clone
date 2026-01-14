from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import BookingRequestSerializer, BookingResponseSerializer
from .services import BookingService
from .exceptions import SeatUnavailableException, PaymentGatewayException

class BookTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookingRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        show_id = serializer.validated_data['show_id']
        seat_ids = serializer.validated_data['seat_ids']

        try:
            booking = BookingService.process_booking_request(
                user=user, 
                show_id=show_id, 
                seat_ids=seat_ids
            )
            
            response_serializer = BookingResponseSerializer(booking)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except SeatUnavailableException as e:
            return Response(
                {"error": "Booking Failed", "detail": str(e)}, 
                status=status.HTTP_409_CONFLICT
            )
            
        except PaymentGatewayException as e:
            return Response(
                {"error": "Payment Failed", "detail": "Transaction declined by bank."}, 
                status=status.HTTP_402_PAYMENT_REQUIRED
            )
            
        except Exception as e:
            # Catch-all for unexpected logic errors
            return Response(
                {"error": "Server Error", "detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )