from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# Import your models exactly as before
from infrastructure.models import City, Venue, Screen, ShowFormat, SeatType, Seat
from events.models import Event, Language
from shows.models import Show, ShowSeatTypePrice
from bookings.models import ShowSeat

class Command(BaseCommand):
    help = 'Add Mumbai specific data to the database'

    def handle(self, *args, **kwargs):
        self.stdout.write('Fetching existing metadata...')
        
        # 1. Fetch existing objects (Assuming previous script ran)
        try:
            mumbai = City.objects.get(name='Mumbai')
            pushpa = Event.objects.get(title__icontains='Pushpa')
            
            # Formats & Types
            format_2d = ShowFormat.objects.get(name='2D')
            hindi = Language.objects.get(name='Hindi')
            seat_recliner = SeatType.objects.get(name='Recliner')
            seat_premium = SeatType.objects.get(name='Premium')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: Could not find base data. Did you run the main script? {str(e)}'))
            return

        # 2. Create Mumbai Venue
        self.stdout.write('Creating Mumbai Venue...')
        pvr_mumbai, created = Venue.objects.get_or_create(
            name='PVR Icon: Infinity Mall',
            city=mumbai,
            defaults={
                'address': 'Andheri West, Mumbai',
                'pincode': '400053'
            }
        )

        # 3. Create Mumbai Screen
        self.stdout.write('Creating Mumbai Screen...')
        mumbai_screen, created = Screen.objects.get_or_create(
            venue=pvr_mumbai,
            name='Gold Class 1',
            defaults={
                'total_capacity': 40,
                'seating_layout_template': {
                    'rows': [
                        {'row_code': 'A', 'seat_type_id': seat_recliner.id, 'seats': list(range(1, 11))},
                        {'row_code': 'B', 'seat_type_id': seat_recliner.id, 'seats': list(range(1, 11))},
                        {'row_code': 'C', 'seat_type_id': seat_premium.id, 'seats': list(range(1, 11))},
                        {'row_code': 'D', 'seat_type_id': seat_premium.id, 'seats': list(range(1, 11))},
                    ]
                }
            }
        )
        mumbai_screen.supported_formats.add(format_2d)

        # 4. Create Physical Seats
        self.stdout.write('Creating Physical Seats for Mumbai...')
        # Check if seats exist to avoid duplication if run twice
        if not Seat.objects.filter(screen=mumbai_screen).exists():
            for row_data in mumbai_screen.seating_layout_template['rows']:
                for seat_num in row_data['seats']:
                    Seat.objects.create(
                        screen=mumbai_screen,
                        seat_type_id=row_data['seat_type_id'],
                        row=row_data['row_code'],
                        seat_number=seat_num,
                        is_active=True
                    )

        # 5. Create Shows for next 5 days
        self.stdout.write('Creating Shows in Mumbai...')
        base_time = timezone.now().replace(hour=19, minute=0, second=0, microsecond=0)
        
        new_shows = []
        for i in range(5):
            show_time = base_time + timedelta(days=i)
            
            # Check duplication
            if Show.objects.filter(screen=mumbai_screen, show_datetime=show_time).exists():
                continue

            show = Show.objects.create(
                event=pushpa,
                venue=pvr_mumbai,
                screen=mumbai_screen,
                show_format=format_2d,
                language=hindi,
                show_datetime=show_time,
                end_datetime=show_time + timedelta(minutes=pushpa.duration_minutes),
                is_active=True
            )
            new_shows.append(show)

            # Pricing
            ShowSeatTypePrice.objects.create(show=show, seat_type=seat_recliner, price=Decimal('800.00'))
            ShowSeatTypePrice.objects.create(show=show, seat_type=seat_premium, price=Decimal('500.00'))

        # 6. Generate ShowSeats (Inventory)
        self.stdout.write('Generating Inventory (ShowSeats)...')
        physical_seats = Seat.objects.filter(screen=mumbai_screen)
        
        for show in new_shows:
            seat_count = 0
            for p_seat in physical_seats:
                # Find price
                try:
                    price = show.price_config.get(seat_type=p_seat.seat_type).price
                except:
                    price = Decimal('400.00')

                ShowSeat.objects.create(
                    show=show,
                    seat=p_seat,
                    price=price,
                    status='available',
                    version=0
                )
                seat_count += 1
            print(f" > Created {seat_count} seats for show on {show.show_datetime.date()}")

        self.stdout.write(self.style.SUCCESS('Mumbai data populated successfully!'))