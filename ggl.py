import datetime
from pprint import pprint
from typing import List

import googleapiclient
from google.oauth2 import service_account
from googleapiclient.discovery import build

import config
from utils import Lesson, week_days, number_to_time, Week, date_with_time

colors = {
    '1': {'background': '#a4bdfc', 'foreground': '#1d1d1d'},  # lavender
    '2': {'background': '#7ae7bf', 'foreground': '#1d1d1d'},  # sage
    '3': {'background': '#dbadff', 'foreground': '#1d1d1d'},  # grape
    '4': {'background': '#ff887c', 'foreground': '#1d1d1d'},  # flamingo
    '5': {'background': '#fbd75b', 'foreground': '#1d1d1d'},  # banana
    '6': {'background': '#ffb878', 'foreground': '#1d1d1d'},  # tangerine
    '7': {'background': '#46d6db', 'foreground': '#1d1d1d'},  # peacock
    '8': {'background': '#e1e1e1', 'foreground': '#1d1d1d'},  # graphite
    '9': {'background': '#5484ed', 'foreground': '#1d1d1d'},  # blueberry
    '10': {'background': '#51b749', 'foreground': '#1d1d1d'},  # basil
    '11': {'background': '#dc2127', 'foreground': '#1d1d1d'},  # tomato
}

type_to_color = {
    'Л': '3',
    'ПР': '6',
    'ЛР': '7',
    'КР': '5',
    'КП': '10',
}


class GoogleCalendar:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = 'credentials.json'

    def __init__(self, calendar_id):
        self.calendarId = calendar_id
        credentials = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE,
                                                                            scopes=self.SCOPES)
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    # создание словаря с информацией о событии
    @staticmethod
    def create_event_dict(name, description, start, end, interval, color_id):
        event = {
            'summary': name,
            'description': description,
            'start': {
                'dateTime': start,
                'timeZone': 'Europe/Moscow',
            },
            'end': {
                'dateTime': end,
                'timeZone': 'Europe/Moscow',
            },
            'colorId': color_id,
            'reminders': {
                'useDefault': False,
                'overrides': [
                    # {'method': 'email', 'minutes': 24 * 60},
                    {'method': 'popup', 'minutes': 15},
                ],
            },
            'recurrence': [f'RRULE:FREQ=WEEKLY;INTERVAL={interval};UNTIL=20230101T170000Z']
        }
        return event

    # создание события в календаре
    def create_event(self, event: dict):
        e = self.service.events().insert(calendarId=self.calendarId, sendNotifications=True,
                                         body=event).execute()
        return e

    # создание события в календаре
    def create_calendar(self, name: str):
        calendar = {
            'summary': name,
            'timeZone': 'Europe/Moscow',
        }
        c = self.service.calendars().insert(body=calendar).execute()
        return c

    # вывод списка из десяти предстоящих событий
    def get_events_list(self, max_results=250):
        now = datetime.datetime.utcnow()
        print(now)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        print(start)
        end = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()
        print(end)
        end = None
        print(now)
        events_result = self.service.events().list(calendarId=self.calendarId,
                                                   timeMin=start,
                                                   timeMax=end,
                                                   maxResults=max_results, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events if events else 'No upcoming events found.'
        # start = event['start'].get('dateTime', event['start'].get('date'))
        # return start, event['summary']

    def upload_events(self, lessons: List[Lesson]):
        is_this_week_up = datetime.datetime.today().isocalendar().week % 2 != 0
        c = self.create_calendar('SUAI')
        for lesson in lessons:
            start = date_with_time(week_days[lesson.day], number_to_time[lesson.number][0])
            end = date_with_time(week_days[lesson.day], number_to_time[lesson.number][1])
            interval = 2
            if lesson.week is Week.all:
                interval = 1
            elif is_this_week_up == (lesson.week is Week.dn):
                start += datetime.timedelta(7)
                end += datetime.timedelta(7)
            e = self.create_event(self.create_event_dict(
                lesson.name, str(lesson.auditorium), start.isoformat(), end.isoformat(), interval,
                type_to_color.get(lesson.type, '9'))
            )
            print(f'Event created: {e.get("id")}')
            print(e)

    def test(self):
        page_token = None
        while True:
            calendar_list = self.service.calendarList().list(pageToken=page_token).execute()
            for calendar_list_entry in calendar_list['items']:
                print(calendar_list_entry['summary'])
            page_token = calendar_list.get('nextPageToken')
            if not page_token:
                break
        # return

        # c = self.create_calendar('SUAI22')
        # pprint(c)
        calendarId = '3pgm8ivioavagnovofjv2am6qk@group.calendar.google.com'
        acl = self.service.acl().list(calendarId=calendarId).execute()

        for rule in acl['items']:
            print('%s: %s' % (rule['id'], rule['role']))

        rule = {
            'scope': {
                'type': 'user',
                'value': '79516747741p@gmail.com',
            },
            'role': 'owner'
        }

        # created_rule = self.service.acl().insert(calendarId=calendarId, body=rule).execute()
        # pprint(created_rule)


if __name__ == '__main__':
    'ajsmbuus80alnr8rsvcvucpv50@group.calendar.google.com'
    GoogleCalendar(None).test()
    # GoogleCalendar(config.calendar_id).test()
