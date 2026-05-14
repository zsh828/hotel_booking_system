import re
import hashlib
import datetime
from typing import Optional


def validate_phone(phone: str) -> bool:
    """校验手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))


def validate_id_card(id_card: str) -> bool:
    """校验身份证号格式 (简单校验18位)"""
    pattern = r'^\d{17}[\dXx]$'
    if not re.match(pattern, id_card):
        return False
    # 这里可以添加更复杂的校验位算法，但为了简化，仅做格式校验
    return True


def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, hashed_password: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed_password


def calculate_days(start_date: datetime.date, end_date: datetime.date) -> int:
    """计算天数"""
    delta = end_date - start_date
    days = delta.days
    if days <= 0:
        raise ValueError("退房日期必须晚于入住日期")
    return days


def is_birthday_month(customer_birthday: Optional[datetime.date], current_date: datetime.date) -> bool:
    """检查当前月份是否为客户生日月"""
    if not customer_birthday:
        return False
    return customer_birthday.month == current_date.month