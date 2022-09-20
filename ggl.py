from __future__ import print_function
import datetime
import googleapiclient
from google.oauth2 import service_account
from googleapiclient.discovery import build


class GoogleCalendar:
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    calendarId = '79516747741p@gmail.com'
    SERVICE_ACCOUNT_FILE = 'credentials.json'

    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE,
                                                                            scopes=self.SCOPES)
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    # создание словаря с информацией о событии
    def create_event_dict(self):
        event = {
            'summary': 'test event',
            'description': 'some info',
            'start': {
                'dateTime': '2022-01-25T03:00:00+03:00',
            },
            'end': {
                'dateTime': '2022-01-25T05:30:00+03:00',
            }
        }
        return event

    # создание события в календаре
    def create_event(self, event):
        e = self.service.events().insert(calendarId=self.calendarId,
                                         body=event).execute()
        return 'Event created: %s' % (e.get('id'))

    # вывод списка из десяти предстоящих событий
    def get_events_list(self, maxResults=250):
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
                                                   maxResults=maxResults, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        return events if events else 'No upcoming events found.'
        # start = event['start'].get('dateTime', event['start'].get('date'))
        # return start, event['summary']

    # вывод списка из десяти предстоящих событий
    def test(self):
        cals_result = self.service.calendarList().list().execute()
        cals = cals_result.get('items', [])
        return cals if cals else 'No upcoming cals found.'


calendar = GoogleCalendar()
if __name__ == '__main__':
    print(calendar.create_event(calendar.create_event_dict()))
    print(calendar.get_events_list())
