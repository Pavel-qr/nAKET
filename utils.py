import datetime
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Final

PASS_REAL_VALUES: Final[bool] = True

number_to_str_time = {
    '1': '(9:30 – 11:00)',
    '2': '(11:10 – 12:40)',
    '3': '(13:00 – 14:30)',
    '4': '(15:00 - 16:30)',
    '5': '(16:40 - 18:10)',
    '6': '(18:30 - 20:00)',
    '7': '(21:10 - 21:40)',
}

number_to_time = {
    '1': (datetime.time(9, 30), datetime.time(11)),
    '2': (datetime.time(11, 10), datetime.time(12, 40)),
    '3': (datetime.time(13), datetime.time(14, 30)),
    '4': (datetime.time(15), datetime.time(16, 30)),
    '5': (datetime.time(16, 40), datetime.time(18, 10)),
    '6': (datetime.time(18, 30), datetime.time(20)),
    '7': (datetime.time(21, 10), datetime.time(21, 40)),
}


class WeekDay(Enum):
    monday = 'Понедельник'
    tuesday = 'Вторник'
    wednesday = 'Среда'
    thursday = 'Четверг'
    friday = 'Пятница'
    saturday = 'Суббота'
    sunday = 'Воскресенье'


week_days = {
    WeekDay.monday: 0,
    WeekDay.tuesday: 1,
    WeekDay.wednesday: 2,
    WeekDay.thursday: 3,
    WeekDay.friday: 4,
    WeekDay.saturday: 5,
    WeekDay.sunday: 6,
}


class Week(Enum):
    all = '🔶'
    up = 'верхняя (нечетная) ▲🔺'
    dn = 'нижняя (четная) ▼🔻'
    # out = 'вне сетки расписания (—)'


@dataclass
class Auditorium:
    address: str
    number: str

    def __str__(self):
        return f'{self.address}, ауд. {self.number}'


@dataclass
class Lesson:
    name: str
    type: str
    day: WeekDay
    number: str
    auditorium: Auditorium
    teachers: Optional[list[str]]
    groups: Optional[list[str]]
    week: Week


# class Shift(Enum):
#     first = '1 смена'
#     second = '2 смена'
#

month_to_int = {
    'июня': 6
}


@dataclass
class Session:
    name: str
    date: datetime.date
    number: str
    # shift: Shift
    auditorium: Auditorium
    teacher: str


def date_with_time(weekday: int, time: datetime.time):
    date = datetime.datetime.today().replace(hour=time.hour, minute=time.minute, second=time.second, microsecond=0)
    date += datetime.timedelta(days=(weekday - date.weekday()))
    return date
