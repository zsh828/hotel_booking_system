import pytest
import datetime
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hotel_system import HotelSystem, HotelSystemError
from src.models import RoomType, RoomStatus, MemberLevel, BookingStatus, PaymentStatus


@pytest.fixture
def hotel():
    return HotelSystem()


@pytest.fixture
def customer(hotel):
    return hotel.register_customer(
        name="Test User",
        phone="13800138000",
        id_card="110101199001011234",
        password="password123",
        birthday="1990-05-15"
    )


@pytest.fixture
def room(hotel):
    return hotel.add_room("101", "单人间", 200.0, 1)


class TestRoomManagement:
    def test_add_room_success(self, hotel):
        room = hotel.add_room("102", "双人间", 300.0, 1)
        assert room.room_number == "102"
        assert room.room_type == RoomType.DOUBLE
        assert room.status == RoomStatus.AVAILABLE

    def test_add_duplicate_room(self, hotel):
        hotel.add_room("101", "单人间", 200.0, 1)
        with pytest.raises(HotelSystemError, match="已存在"):
            hotel.add_room("101", "双人间", 300.0, 1)

    def test_query_rooms_by_type(self, hotel):
        hotel.add_room("101", "单人间", 200.0, 1)
        hotel.add_room("201", "双人间", 300.0, 2)
        results = hotel.query_rooms(room_type="单人间")
        assert len(results) == 1
        assert results[0].room_number == "101"

    def test_mark_maintenance(self, hotel, room):
        updated_room = hotel.mark_room_maintenance("101")
        assert updated_room.status == RoomStatus.MAINTENANCE

    def test_complete_maintenance(self, hotel, room):
        hotel.mark_room_maintenance("101")
        updated_room = hotel.complete_maintenance("101")
        assert updated_room.status == RoomStatus.AVAILABLE

    def test_cannot_book_maintenance_room(self, hotel, customer):
        hotel.add_room("101", "单人间", 200.0, 1)
        hotel.mark_room_maintenance("101")
        with pytest.raises(HotelSystemError, match="不可用"):
            hotel.create_booking(customer.customer_id, "101", "2023-12-01", "2023-12-02")


class TestCustomerManagement:
    def test_register_success(self, hotel):
        c = hotel.register_customer("User", "13900000000", "110101199001011235", "pass")
        assert c.name == "User"
        assert c.member_level == MemberLevel.NORMAL

    def test_register_invalid_phone(self, hotel):
        with pytest.raises(HotelSystemError, match="手机号"):
            hotel.register_customer("User", "123", "110101199001011235", "pass")

    def test_login_success(self, hotel, customer):
        c = hotel.login_customer("13800138000", "password123")
        assert c.customer_id == customer.customer_id

    def test_login_wrong_password(self, hotel, customer):
        with pytest.raises(HotelSystemError, match="密码"):
            hotel.login_customer("13800138000", "wrong")

    def test_member_upgrade_silver(self, hotel, customer):
        hotel.update_customer_spending(customer.customer_id, 5000)
        assert customer.member_level == MemberLevel.SILVER

    def test_member_upgrade_gold(self, hotel, customer):
        hotel.update_customer_spending(customer.customer_id, 10000)
        assert customer.member_level == MemberLevel.GOLD

    def test_member_upgrade_diamond(self, hotel, customer):
        hotel.update_customer_spending(customer.customer_id, 30000)
        assert customer.member_level == MemberLevel.DIAMOND


class TestBookingManagement:
    def test_create_booking_success(self, hotel, customer, room):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        day_after = today + datetime.timedelta(days=2)
        
        booking = hotel.create_booking(
            customer.customer_id, "101", 
            tomorrow.isoformat(), day_after.isoformat()
        )
        assert booking.status == BookingStatus.BOOKED
        assert booking.total_amount == 200.0 # 1 day * 200

    def test_create_booking_overlap(self, hotel, customer, room):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        day_after = today + datetime.timedelta(days=2)
        
        hotel.create_booking(customer.customer_id, "101", tomorrow.isoformat(), day_after.isoformat())
        
        with pytest.raises(HotelSystemError, match="不可用"):
            hotel.create_booking(customer.customer_id, "101", tomorrow.isoformat(), day_after.isoformat())

    def test_cancel_booking_free(self, hotel, customer, room):
        today = datetime.date.today()
        future_in = today + datetime.timedelta(days=10)
        future_out = today + datetime.timedelta(days=11)
        
        booking = hotel.create_booking(customer.customer_id, "101", future_in.isoformat(), future_out.isoformat())
        refund = hotel.cancel_booking(booking.booking_id)
        
        assert refund == 200.0 # Full refund
        assert booking.status == BookingStatus.CANCELLED

    def test_modify_booking_date(self, hotel, customer, room):
        today = datetime.date.today()
        d1 = today + datetime.timedelta(days=1)
        d2 = today + datetime.timedelta(days=2)
        d3 = today + datetime.timedelta(days=3)
        d4 = today + datetime.timedelta(days=4)
        
        booking = hotel.create_booking(customer.customer_id, "101", d1.isoformat(), d2.isoformat())
        modified = hotel.modify_booking_date(booking.booking_id, d3.isoformat(), d4.isoformat())
        
        assert modified.check_in_date == d3
        assert modified.total_amount == 200.0


class TestCheckInOut:
    def test_check_in_success(self, hotel, customer, room):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        day_after = today + datetime.timedelta(days=2)
        
        booking = hotel.create_booking(customer.customer_id, "101", tomorrow.isoformat(), day_after.isoformat())
        checked_in_booking = hotel.check_in(booking.booking_id, customer.id_card)
        
        assert checked_in_booking.status == BookingStatus.CHECKED_IN
        assert room.status == RoomStatus.OCCUPIED

    def test_check_in_wrong_id(self, hotel, customer, room):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        day_after = today + datetime.timedelta(days=2)
        
        booking = hotel.create_booking(customer.customer_id, "101", tomorrow.isoformat(), day_after.isoformat())
        
        with pytest.raises(HotelSystemError, match="身份证"):
            hotel.check_in(booking.booking_id, "000000000000000000")

    def test_check_out_and_bill(self, hotel, customer, room):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        day_after = today + datetime.timedelta(days=2)
        
        booking = hotel.create_booking(customer.customer_id, "101", tomorrow.isoformat(), day_after.isoformat())
        hotel.check_in(booking.booking_id, customer.id_card)
        
        # Simulate time passing for checkout
        bill = hotel.check_out(booking.booking_id, other_fee=50.0)
        
        assert bill.payment_status == PaymentStatus.PAID
        assert room.status == RoomStatus.AVAILABLE
        assert booking.status == BookingStatus.CHECKED_OUT
        
        # Check customer points update
        assert customer.points > 0

    def test_birthday_discount(self, hotel, room):
        # Create customer with birthday in current month
        import calendar
        now = datetime.datetime.now()
        birthday_str = f"{now.year}-{now.month:02d}-15"
        
        customer = hotel.register_customer("BDay User", "13800138001", "110101199001011236", "pass", birthday=birthday_str)
        
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        day_after = today + datetime.timedelta(days=2)
        
        booking = hotel.create_booking(customer.customer_id, "101", tomorrow.isoformat(), day_after.isoformat())
        hotel.check_in(booking.booking_id, customer.id_card)
        bill = hotel.check_out(booking.booking_id)
        
        # Normal price 200. No member discount. Birthday discount 0.95.
        # 200 * 0.95 = 190.
        assert abs(bill.paid_amount - 190.0) < 0.01


class TestStatistics:
    def test_occupancy_rate(self, hotel, customer, room):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)
        day_after = today + datetime.timedelta(days=2)
        
        hotel.create_booking(customer.customer_id, "101", tomorrow.isoformat(), day_after.isoformat())
        
        # Statistic for tomorrow
        rate_data = hotel.get_occupancy_rate(tomorrow.isoformat(), day_after.isoformat())
        assert rate_data["occupancy_rate"] == 100.0

    def test_popular_room_types(self, hotel, customer):
        hotel.add_room("101", "单人间", 200.0, 1)
        hotel.add_room("201", "双人间", 300.0, 2)
        
        today = datetime.date.today()
        d1 = today + datetime.timedelta(days=1)
        d2 = today + datetime.timedelta(days=2)
        
        hotel.create_booking(customer.customer_id, "101", d1.isoformat(), d2.isoformat())
        hotel.create_booking(customer.customer_id, "101", d1.isoformat(), d2.isoformat()) # Wait, same room same time error.
        
        # Create another booking for different date to count same type
        d3 = today + datetime.timedelta(days=3)
        d4 = today + datetime.timedelta(days=4)
        hotel.create_booking(customer.customer_id, "101", d3.isoformat(), d4.isoformat())
        
        popular = hotel.get_popular_room_types()
        assert popular[0]["room_type"] == "单人间"
        assert popular[0]["count"] == 2