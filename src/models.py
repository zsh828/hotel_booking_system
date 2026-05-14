import hashlib
import datetime
import re
from enum import Enum
from typing import Optional, List, Dict, Any


class RoomType(Enum):
    SINGLE = "单人间"
    DOUBLE = "双人间"
    SUITE = "套房"


class RoomStatus(Enum):
    AVAILABLE = "空闲"
    BOOKED = "已预订"
    MAINTENANCE = "维修中"
    OCCUPIED = "已入住"


class MemberLevel(Enum):
    NORMAL = "普通"
    SILVER = "银卡"
    GOLD = "金卡"
    DIAMOND = "钻石"


class BookingStatus(Enum):
    BOOKED = "已预订"
    CHECKED_IN = "已入住"
    CHECKED_OUT = "已退房"
    CANCELLED = "已取消"


class PaymentStatus(Enum):
    UNPAID = "未支付"
    PAID = "已支付"


class Room:
    def __init__(self, room_number: str, room_type: RoomType, price_per_day: float, floor: int, status: RoomStatus = RoomStatus.AVAILABLE):
        self.room_number = room_number
        self.room_type = room_type
        self.price_per_day = price_per_day
        self.status = status
        self.floor = floor

    def to_dict(self) -> Dict[str, Any]:
        return {
            "room_number": self.room_number,
            "room_type": self.room_type.value,
            "price_per_day": self.price_per_day,
            "status": self.status.value,
            "floor": self.floor
        }


class Customer:
    def __init__(self, customer_id: str, name: str, phone: str, id_card: str, 
                 member_level: MemberLevel = MemberLevel.NORMAL, 
                 total_spent: float = 0.0, points: int = 0, password_hash: str = "", birthday: Optional[datetime.date] = None):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.id_card = id_card
        self.member_level = member_level
        self.total_spent = total_spent
        self.points = points
        self.password_hash = password_hash
        self.birthday = birthday

    def upgrade_member_level(self):
        if self.total_spent >= 30000:
            self.member_level = MemberLevel.DIAMOND
        elif self.total_spent >= 10000:
            self.member_level = MemberLevel.GOLD
        elif self.total_spent >= 5000:
            self.member_level = MemberLevel.SILVER

    def add_points(self, amount: float):
        # 每消费1元=1积分，取整
        self.points += int(amount)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "phone": self.phone,
            "id_card": self.id_card,
            "member_level": self.member_level.value,
            "total_spent": self.total_spent,
            "points": self.points,
            "birthday": self.birthday.isoformat() if self.birthday else None
        }


class Booking:
    def __init__(self, booking_id: str, customer_id: str, room_number: str, 
                 check_in_date: datetime.date, check_out_date: datetime.date,
                 status: BookingStatus = BookingStatus.BOOKED,
                 actual_check_in: Optional[datetime.datetime] = None,
                 actual_check_out: Optional[datetime.datetime] = None,
                 total_amount: float = 0.0):
        self.booking_id = booking_id
        self.customer_id = customer_id
        self.room_number = room_number
        self.check_in_date = check_in_date
        self.check_out_date = check_out_date
        self.status = status
        self.actual_check_in = actual_check_in
        self.actual_check_out = actual_check_out
        self.total_amount = total_amount

    def to_dict(self) -> Dict[str, Any]:
        return {
            "booking_id": self.booking_id,
            "customer_id": self.customer_id,
            "room_number": self.room_number,
            "check_in_date": self.check_in_date.isoformat(),
            "check_out_date": self.check_out_date.isoformat(),
            "status": self.status.value,
            "actual_check_in": self.actual_check_in.isoformat() if self.actual_check_in else None,
            "actual_check_out": self.actual_check_out.isoformat() if self.actual_check_out else None,
            "total_amount": self.total_amount
        }


class Bill:
    def __init__(self, bill_id: str, booking_id: str, room_fee: float, other_fee: float = 0.0, 
                 discount_amount: float = 0.0, paid_amount: float = 0.0,
                 payment_status: PaymentStatus = PaymentStatus.UNPAID,
                 payment_time: Optional[datetime.datetime] = None):
        self.bill_id = bill_id
        self.booking_id = booking_id
        self.room_fee = room_fee
        self.other_fee = other_fee
        self.discount_amount = discount_amount
        self.paid_amount = paid_amount
        self.payment_status = payment_status
        self.payment_time = payment_time

    def to_dict(self) -> Dict[str, Any]:
        return {
            "bill_id": self.bill_id,
            "booking_id": self.booking_id,
            "room_fee": self.room_fee,
            "other_fee": self.other_fee,
            "discount_amount": self.discount_amount,
            "paid_amount": self.paid_amount,
            "payment_status": self.payment_status.value,
            "payment_time": self.payment_time.isoformat() if self.payment_time else None
        }