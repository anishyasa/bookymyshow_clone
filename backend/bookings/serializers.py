from rest_framework import serializers

class BookingRequestSerializer(serializers.Serializer):
    show_id = serializers.IntegerField()
    seat_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False
    )

class BookingResponseSerializer(serializers.Serializer):
    booking_code = serializers.CharField()
    status = serializers.CharField()
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    seats = serializers.SerializerMethodField()

    def get_seats(self, obj):
        return [str(seat) for seat in obj.show_seats.all()]