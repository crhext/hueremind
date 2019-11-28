from __future__ import print_function
import time
import datetime 
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from dateutil import parser
import pytz

#phue python wrapper
from phue import Bridge
import logging
import random
logging.basicConfig

b = Bridge('192.168.0.5')

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def main():
    
        """Shows basic usage of the Google Calendar API.

        """
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('calendar', 'v3', credentials=creds)

        while 1:
            
                # Call the Calendar API
                now = datetime.datetime.utcnow()
                then = now + datetime.timedelta(minutes=2)
                
                # Get first event occuring in next 2 min
                print('Getting events in the next 2 mins')
                events_result = service.events().list(calendarId='primary', timeMin=now.isoformat() + 'Z', timeMax=then.isoformat() + 'Z',
                                                    maxResults=1, singleEvents=True,
                                                    orderBy='startTime').execute()
                events = events_result.get('items', [])
                
                # if no event exists, turn light off
                if not events:
                    print('No upcoming events found.')
                    
                    b.set_light(1, 'on', False)
                 
                #if event exists, get the start date/time of the event 
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    print(start, event['summary'])
                    
                    #compare start time vs current time. First parsing into format that python will let us compare
                    if start:
                        event_start = parser.parse(start)
                        current_time = pytz.utc.localize(datetime.datetime.utcnow())
                        
                        #if event is upcoming, set light orange
                        if current_time < event_start:
                            b.set_light(1, 'on', True)
                            b.set_light(1, 'xy', [0.6142, 0.3785])
                            b.set_light(1, 'bri', 127)
                        
                        #if event is upcoming, set light red
                        else:
                            b.set_light(1, 'on', True)
                            b.set_light(1, 'xy', [0.6915, 0.3083])
                        
                #call api every 5 seconds
                time.sleep(5)

if __name__ == '__main__':
    main()
 