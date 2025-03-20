from .models import db, User, Hotel, Floor, Room, Booking, FAQ, YesNo, Locations, RoomType, Availability, Saved

def add_floor(number_floors, hid, base_floor_number):
    floors = []
    for i in range(number_floors):
        floor = Floor(hid=hid, floor_number=base_floor_number+i)
        floors.append(floor)
    db.session.add_all(floors)
    db.session.commit()

def add_room(num_rooms, fid, hid, base_room_number, img, room_type, number_beds, rate,balcony,city_view,ocean_view,smoking,available,max_guests,wheelchair_accessible):
    rooms = []
    for i in range(num_rooms):
        room = Room(
            fid=fid,
            hid=hid,
            room_number = base_room_number + i,
            img = img, 
            room_type = room_type,
            number_beds = number_beds,
            rate = rate,
            balcony = balcony,
            city_view = city_view, 
            ocean_view = ocean_view,
            smoking = smoking, 
            available = available,
            max_guests = max_guests, 
            wheelchair_accessible = wheelchair_accessible
        )     
        rooms.append(room)
    db.session.add_all(rooms)
    db.session.commit()

def add_layout(hid, base_floor_number, num_floors):
    add_floor(num_floors, hid, base_floor_number)
    for i in range(num_floors):
        fid = Floor.query.filter_by(hid=hid, floor_number=base_floor_number+i).first().id
        #standard 1-20, base: 150
        add_room(num_rooms=7, fid=fid, hid=hid, base_room_number=1, img="../static/images/inside.jpeg",room_type=RoomType.STRD, number_beds=1, rate=150, balcony=YesNo.N, city_view=YesNo.N, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N)
        add_room(num_rooms=2, fid=fid, hid=hid, base_room_number=8, img="../static/images/inside.jpeg",room_type=RoomType.STRD, number_beds=1, rate=150, balcony=YesNo.N, city_view=YesNo.N, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.Y)
        add_room(num_rooms=3, fid=fid, hid=hid, base_room_number=10, img="../static/images/inside.jpeg",room_type=RoomType.STRD, number_beds=1, rate=175, balcony=YesNo.N, city_view=YesNo.N, ocean_view=YesNo.N, smoking=YesNo.Y, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N) # +25 for smoking

        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=13, img="../static/images/inside.jpeg",room_type=RoomType.STRD, number_beds=1, rate=250, balcony=YesNo.Y, city_view=YesNo.N, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N) # +100 for balcony
        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=14, img="../static/images/inside.jpeg",room_type=RoomType.STRD, number_beds=1, rate=300, balcony=YesNo.Y, city_view=YesNo.Y, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N) # +50 for city view
        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=15, img="../static/images/inside.jpeg",room_type=RoomType.STRD, number_beds=1, rate=350, balcony=YesNo.Y, city_view=YesNo.N, ocean_view=YesNo.Y, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N) # +100 for ocean view
        
        add_room(num_rooms=2, fid=fid, hid=hid, base_room_number=16, img="../static/images/inside.jpeg",room_type=RoomType.STRD, number_beds=2, rate=225, balcony=YesNo.N, city_view=YesNo.N, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N) # +75 for 2 beds
        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=18, img="../static/images/inside.jpeg",room_type=RoomType.STRD, number_beds=2, rate=225, balcony=YesNo.N, city_view=YesNo.N, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.Y)
        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=19, img="../static/images/inside.jpeg",room_type=RoomType.STRD, number_beds=2, rate=325, balcony=YesNo.N, city_view=YesNo.N, ocean_view=YesNo.Y, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N)
        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=20, img="../static/images/inside.jpeg",room_type=RoomType.STRD, number_beds=2, rate=425, balcony=YesNo.Y, city_view=YesNo.N, ocean_view=YesNo.Y, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N)

        #suite 21-30, base: 350
        add_room(num_rooms=3, fid=fid, hid=hid, base_room_number=21, img="../static/images/inside.jpeg",room_type=RoomType.ST, number_beds=1, rate=350, balcony=YesNo.N, city_view=YesNo.N, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N)
        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=24, img="../static/images/inside.jpeg",room_type=RoomType.ST, number_beds=1, rate=500, balcony=YesNo.Y, city_view=YesNo.Y, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N)
        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=25, img="../static/images/inside.jpeg",room_type=RoomType.ST, number_beds=1, rate=550, balcony=YesNo.N, city_view=YesNo.Y, ocean_view=YesNo.Y, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N)
        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=26, img="../static/images/inside.jpeg",room_type=RoomType.ST, number_beds=1, rate=350, balcony=YesNo.N, city_view=YesNo.N, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.Y)

        add_room(num_rooms=2, fid=fid, hid=hid, base_room_number=27, img="../static/images/inside.jpegg",room_type=RoomType.ST, number_beds=2, rate=425, balcony=YesNo.N, city_view=YesNo.N, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N)
        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=29, img="../static/images/inside.jpeg",room_type=RoomType.ST, number_beds=2, rate=500, balcony=YesNo.N, city_view=YesNo.Y, ocean_view=YesNo.N, smoking=YesNo.Y, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N)
        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=30, img="../static/images/inside.jpeg",room_type=RoomType.ST, number_beds=2, rate=625, balcony=YesNo.Y, city_view=YesNo.N, ocean_view=YesNo.Y, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.Y)

        #deluxe 31 - 40, base: 500
        add_room(num_rooms=2, fid=fid, hid=hid, base_room_number=31, img="../static/images/inside.jpeg",room_type=RoomType.DLX, number_beds=1, rate=500, balcony=YesNo.N, city_view=YesNo.N, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N)
        add_room(num_rooms=2, fid=fid, hid=hid, base_room_number=33, img="../static/images/inside.jpeg",room_type=RoomType.DLX, number_beds=1, rate=650, balcony=YesNo.Y, city_view=YesNo.Y, ocean_view=YesNo.N, smoking=YesNo.Y, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.Y)
        add_room(num_rooms=2, fid=fid, hid=hid, base_room_number=35, img="../static/images/inside.jpeg",room_type=RoomType.DLX, number_beds=1, rate=700, balcony=YesNo.Y, city_view=YesNo.N, ocean_view=YesNo.Y, smoking=YesNo.Y, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.Y)

        add_room(num_rooms=2, fid=fid, hid=hid, base_room_number=37, img="../static/images/inside.jpeg",room_type=RoomType.DLX, number_beds=2, rate=575, balcony=YesNo.N, city_view=YesNo.N, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N)
        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=39, img="../static/images/inside.jpeg",room_type=RoomType.DLX, number_beds=2, rate=725, balcony=YesNo.Y, city_view=YesNo.Y, ocean_view=YesNo.N, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N)
        add_room(num_rooms=1, fid=fid, hid=hid, base_room_number=40, img="../static/images/inside.jpeg",room_type=RoomType.DLX, number_beds=2, rate=775, balcony=YesNo.Y, city_view=YesNo.N, ocean_view=YesNo.Y, smoking=YesNo.N, available=Availability.A, max_guests=4, wheelchair_accessible=YesNo.N)


def add_booking(uid, rid, check_in, check_out, fees):
    booking = Booking(uid=uid, rid=rid, check_in=check_in, check_out=check_out, fees=fees)
    db.session.add(booking)
    db.session.commit()

def add_faq(f):
    faqs = []
    for question, answer, subject in f:
        faq = FAQ(question=question, answer=answer, subject=subject)
        faqs.append(faq)
    db.session.add_all(faqs)
    db.session.commit()
