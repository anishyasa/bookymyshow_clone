from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from faker import Faker

from infrastructure.models import City, Venue, Screen, ShowFormat, SeatType
from events.models import EventType, Language, Event
from shows.models import Show, ShowSeatTypePrice
from bookings.models import Seat, ShowSeat
from users.models import User

fake = Faker()

class Command(BaseCommand):
    help = 'Populate database with test data for movie booking'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data population...')
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        self.stdout.write('Clearing existing data...')
        ShowSeat.objects.all().delete()
        Seat.objects.all().delete()
        Show.objects.all().delete()
        Event.objects.all().delete()
        Screen.objects.all().delete()
        Venue.objects.all().delete()
        City.objects.all().delete()
        ShowFormat.objects.all().delete()
        SeatType.objects.all().delete()
        Language.objects.all().delete()
        EventType.objects.all().delete()
        
        # 1. Create Cities
        self.stdout.write('Creating cities...')
        bangalore = City.objects.create(name='Bangalore', state='Karnataka')
        mumbai = City.objects.create(name='Mumbai', state='Maharashtra')
        
        # 2. Create Show Formats
        self.stdout.write('Creating show formats...')
        format_2d = ShowFormat.objects.create(name='2D')
        format_3d = ShowFormat.objects.create(name='3D')
        format_imax = ShowFormat.objects.create(name='IMAX')
        format_4dx = ShowFormat.objects.create(name='4DX')
        
        # 3. Create Global Seat Types
        self.stdout.write('Creating seat types...')
        seat_type_standard = SeatType.objects.create(
            name='Standard',
            description='Regular seating'
        )
        seat_type_premium = SeatType.objects.create(
            name='Premium',
            description='Premium seating with extra legroom'
        )
        seat_type_recliner = SeatType.objects.create(
            name='Recliner',
            description='Luxury recliner seats'
        )
        
        # 4. Create Venues
        self.stdout.write('Creating venues...')
        pvr_koramangala = Venue.objects.create(
            city=bangalore,
            name='PVR Nexus Koramangala',
            address='Koramangala 4th Block',
            pincode='560034'
        )
        
        inox_garuda = Venue.objects.create(
            city=bangalore,
            name='INOX Garuda Mall',
            address='Magrath Road',
            pincode='560025'
        )
        
        # 5. Create Screens
        self.stdout.write('Creating screens...')
        # PVR Screen 1 - IMAX capable
        pvr_screen1 = Screen.objects.create(
            venue=pvr_koramangala,
            name='Audi 1',
            total_capacity=150,
            seating_layout_template={
                'rows': [
                    {'row_code': 'A', 'seat_type_id': seat_type_recliner.id, 'seats': list(range(1, 11))},
                    {'row_code': 'B', 'seat_type_id': seat_type_recliner.id, 'seats': list(range(1, 11))},
                    {'row_code': 'C', 'seat_type_id': seat_type_premium.id, 'seats': list(range(1, 16))},
                    {'row_code': 'D', 'seat_type_id': seat_type_premium.id, 'seats': list(range(1, 16))},
                    {'row_code': 'E', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 16))},
                    {'row_code': 'F', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 16))},
                    {'row_code': 'G', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 16))},
                    {'row_code': 'H', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 16))},
                ]
            }
        )
        pvr_screen1.supported_formats.add(format_2d, format_3d, format_imax)
        
        # PVR Screen 2 - Regular
        pvr_screen2 = Screen.objects.create(
            venue=pvr_koramangala,
            name='Audi 2',
            total_capacity=120,
            seating_layout_template={
                'rows': [
                    {'row_code': 'A', 'seat_type_id': seat_type_premium.id, 'seats': list(range(1, 13))},
                    {'row_code': 'B', 'seat_type_id': seat_type_premium.id, 'seats': list(range(1, 13))},
                    {'row_code': 'C', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 13))},
                    {'row_code': 'D', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 13))},
                    {'row_code': 'E', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 13))},
                    {'row_code': 'F', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 13))},
                    {'row_code': 'G', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 13))},
                    {'row_code': 'H', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 13))},
                ]
            }
        )
        pvr_screen2.supported_formats.add(format_2d, format_3d)
        
        # INOX Screen
        inox_screen1 = Screen.objects.create(
            venue=inox_garuda,
            name='Screen 1',
            total_capacity=100,
            seating_layout_template={
                'rows': [
                    {'row_code': 'A', 'seat_type_id': seat_type_premium.id, 'seats': list(range(1, 11))},
                    {'row_code': 'B', 'seat_type_id': seat_type_premium.id, 'seats': list(range(1, 11))},
                    {'row_code': 'C', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 11))},
                    {'row_code': 'D', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 11))},
                    {'row_code': 'E', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 11))},
                    {'row_code': 'F', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 11))},
                    {'row_code': 'G', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 11))},
                    {'row_code': 'H', 'seat_type_id': seat_type_standard.id, 'seats': list(range(1, 11))},
                ]
            }
        )
        inox_screen1.supported_formats.add(format_2d, format_4dx)
        
        # 6. Create Physical Seats for each Screen
        self.stdout.write('Creating physical seats...')
        for screen in [pvr_screen1, pvr_screen2, inox_screen1]:
            for row_data in screen.seating_layout_template['rows']:
                row_code = row_data['row_code']
                seat_type_id = row_data['seat_type_id']
                seat_numbers = row_data['seats']
                
                for seat_num in seat_numbers:
                    Seat.objects.create(
                        screen=screen,
                        seat_type_id=seat_type_id,
                        row=row_code,
                        seat_number=seat_num,
                        is_active=True
                    )
        
        # 7. Create Languages
        self.stdout.write('Creating languages...')
        hindi = Language.objects.create(name='Hindi')
        english = Language.objects.create(name='English')
        kannada = Language.objects.create(name='Kannada')
        tamil = Language.objects.create(name='Tamil')
        
        # 8. Create Event Type
        self.stdout.write('Creating event type...')
        movie_type = EventType.objects.create(name='Movie')
        
        # 9. Create Movies (Events)
        self.stdout.write('Creating movies...')
        movie1 = Event.objects.create(
            title='Pushpa 2: The Rule',
            event_type=movie_type,
            description='Action-packed sequel',
            duration_minutes=180,
            poster_url='https://example.com/pushpa2.jpg',
            genre=['Action', 'Drama'],
            is_active=True
        )
        movie1.languages.add(hindi, english, kannada, tamil)
        
        movie2 = Event.objects.create(
            title='Inception',
            event_type=movie_type,
            description='Mind-bending thriller',
            duration_minutes=148,
            poster_url='https://example.com/inception.jpg',
            genre=['Sci-Fi', 'Thriller'],
            is_active=True
        )
        movie2.languages.add(english)
        
        movie3 = Event.objects.create(
            title='3 Idiots',
            event_type=movie_type,
            description='Comedy-drama about engineering students',
            duration_minutes=170,
            poster_url='https://example.com/3idiots.jpg',
            genre=['Comedy', 'Drama'],
            is_active=True
        )
        movie3.languages.add(hindi, english)
        
        # 10. Create Shows for next 7 days
        self.stdout.write('Creating shows...')
        base_time = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        shows_created = []
        
        # Create shows for Pushpa 2
        for day_offset in range(7):
            show_date = base_time + timedelta(days=day_offset)
            
            # PVR Screen 1 - 3 shows per day
            for hour in [10, 14, 18]:
                show_time = show_date.replace(hour=hour)
                show = Show.objects.create(
                    event=movie1,
                    venue=pvr_koramangala,
                    screen=pvr_screen1,
                    show_format=format_3d,
                    language=hindi,
                    show_datetime=show_time,
                    end_datetime=show_time + timedelta(minutes=movie1.duration_minutes),
                    is_active=True
                )
                shows_created.append(show)
                
                # Create pricing
                ShowSeatTypePrice.objects.create(show=show, seat_type=seat_type_recliner, price=Decimal('500.00'))
                ShowSeatTypePrice.objects.create(show=show, seat_type=seat_type_premium, price=Decimal('300.00'))
                ShowSeatTypePrice.objects.create(show=show, seat_type=seat_type_standard, price=Decimal('200.00'))
        
        # Create shows for Inception
        for day_offset in range(5):
            show_date = base_time + timedelta(days=day_offset)
            
            # INOX Screen 1 - 2 shows per day
            for hour in [11, 15]:
                show_time = show_date.replace(hour=hour)
                show = Show.objects.create(
                    event=movie2,
                    venue=inox_garuda,
                    screen=inox_screen1,
                    show_format=format_2d,
                    language=english,
                    show_datetime=show_time,
                    end_datetime=show_time + timedelta(minutes=movie2.duration_minutes),
                    is_active=True
                )
                shows_created.append(show)
                
                ShowSeatTypePrice.objects.create(show=show, seat_type=seat_type_premium, price=Decimal('350.00'))
                ShowSeatTypePrice.objects.create(show=show, seat_type=seat_type_standard, price=Decimal('250.00'))
        
        # Create shows for 3 Idiots
        for day_offset in range(3):
            show_date = base_time + timedelta(days=day_offset)
            
            show_time = show_date.replace(hour=20)
            show = Show.objects.create(
                event=movie3,
                venue=pvr_koramangala,
                screen=pvr_screen2,
                show_format=format_2d,
                language=hindi,
                show_datetime=show_time,
                end_datetime=show_time + timedelta(minutes=movie3.duration_minutes),
                is_active=True
            )
            shows_created.append(show)
            
            ShowSeatTypePrice.objects.create(show=show, seat_type=seat_type_premium, price=Decimal('280.00'))
            ShowSeatTypePrice.objects.create(show=show, seat_type=seat_type_standard, price=Decimal('180.00'))
        
        # 11. Create ShowSeats for each show
        self.stdout.write('Creating show seats...')
        for show in shows_created:
            screen = show.screen
            physical_seats = Seat.objects.filter(screen=screen, is_active=True)
            
            for physical_seat in physical_seats:
                # Get price for this seat type
                try:
                    price_config = show.price_config.get(seat_type=physical_seat.seat_type)
                    price = price_config.price
                except:
                    price = Decimal('200.00')  # Default price
                
                ShowSeat.objects.create(
                    show=show,
                    seat=physical_seat,
                    price=price,
                    status='available',
                    version=0
                )
        
        # 12. Create a test user
        self.stdout.write('Creating test user...')
        User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated test data!'))
        self.stdout.write(f'Created:')
        self.stdout.write(f'  - {City.objects.count()} cities')
        self.stdout.write(f'  - {Venue.objects.count()} venues')
        self.stdout.write(f'  - {Screen.objects.count()} screens')
        self.stdout.write(f'  - {Seat.objects.count()} physical seats')
        self.stdout.write(f'  - {Event.objects.count()} movies')
        self.stdout.write(f'  - {Show.objects.count()} shows')
        self.stdout.write(f'  - {ShowSeat.objects.count()} show seats')