import datetime
from pprint import pprint

import googleapiclient
from google.oauth2 import service_account
from googleapiclient.discovery import build


class GoogleCalendar:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = 'credentials.json'

    def __init__(self, calendar_id='79516747741p@gmail.com'):
        self.calendarId = calendar_id
        credentials = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE,
                                                                            scopes=self.SCOPES)
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    # создание словаря с информацией о событии
    @staticmethod
    def create_event_dict(name, description, start, end, day, color_id):
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
                'overrides': [{'method': 'popup', 'minutes': 15}]
            },
            'recurrence': [f'RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY={day};UNTIL=20220131']
        }
        return event

    # создание события в календаре
    def create_event(self, event: dict):
        e = self.service.events().insert(calendarId=self.calendarId,
                                         body=event).execute()
        return 'Event created: %s' % (e.get('id'))

    # вывод списка из десяти предстоящих событий
    def get_events_list(self, max_results=250):
        now = datetime.datetime.utcnow()
        print(now)
        start = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + '+03:00'
        print(start)
        end = now.replace(hour=23, minute=59, second=59, microsecond=0).isoformat() + '+03:00'
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

    # вывод списка из десяти предстоящих событий
    def test(self):
        colors = self.service.colors().get().execute()
        pprint(colors)

        # cals_result = self.service.calendarList().list().execute()
        # cals = cals_result.get('items', [])
        # return cals if cals else 'No upcoming cals found.'


calendar = GoogleCalendar()
if __name__ == '__main__':
    calendar.test()
