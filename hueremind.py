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
import sys

#phue python wrapper
from phue import Bridge
import logging
import random
logging.basicConfig()

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
        
        prev_on = b.get_light(1, 'on')
        prev_colour = b.get_light(1, 'xy')
        current_on = b.get_light(1, 'on')
        current_colour = b.get_light(1, 'xy')
        status = 'off'
        upcoming_count = 0
        ongoing_count = 0
        off_count = 0
        err_count = 0
        
        
        while True:
                try:
                    #Get current light status
                    current_on = b.get_light(1, 'on')
                    current_colour = b.get_light(1, 'xy')
                    
                    # Get current time + time 2 min
                    now = datetime.datetime.utcnow()
                    then = now + datetime.timedelta(minutes=2)
                    
                    # Get first event occuring in next 2 min
                    print('Getting events in the next 2 mins')
                    events_result = service.events().list(calendarId='primary', timeMin=now.isoformat() + 'Z', timeMax=then.isoformat() + 'Z',
                                                        maxResults=1, singleEvents=True,
                                                        orderBy='startTime').execute()
                    events = events_result.get('items', [])
                    
                    # if no event exists, return lights back to previous
                    if not events:
                        if status == 'ongoing' or status == 'upcoming':
                            if prev_on:
                                b.set_light(1, 'on', True)
                                b.set_light(1, 'xy', prev_colour)
                            else:
                                b.set_light(1, 'on', False)
                            status = 'off'
                        
                        ongoing_count = 0
                        upcoming_count = 0
                        off_count = off_count + 1
                        
                        print('-----')
                        print('No upcoming events found.')
                        print('status: ', status)
                        print('prev on: ', prev_on)
                        print('prev colour: ', prev_colour)
                        print('current on: ', current_on)
                        print('current colour: ', current_colour)
                        print('opcoming count: ', upcoming_count)
                        print('ongoing count: ', ongoing_count)
                        print('off count: ', off_count)
                        print('error count: ', err_count)
                        print('-----')
                            
                    
                    #if event exists, get the start date/time of the event
                    for event in events:
                        
                        start = event['start'].get('dateTime', event['start'].get('date'))
                        
                        #First parse into format that python will let us compare
                        
                        event_start = parser.parse(start)
                        current_time   = pytz.utc.localize(datetime.datetime.utcnow())
                            
                        # compare start time vs current time. if event is upcoming, get current light details, & set light orange
                        if current_time < event_start:
                            if upcoming_count == 0:
                                prev_on = current_on
                                prev_colour = current_colour
                                                      
                            upcoming_count = upcoming_count + 1
                            ongoing_count = 0
                            off_count = 0
                            status = 'upcoming'
                            
                            print('-----')
                            print('Event: ',start, event['summary'])
                            print('status: ', status)
                            print('prev on: ', prev_on)
                            print('prev colour: ', prev_colour)
                            print('current on: ', current_on)
                            print('current colour: ', current_colour)
                            print('opcoming count: ', upcoming_count)
                            print('ongoing count: ', ongoing_count)
                            print('off count: ', off_count)
                            print('error count: ', err_count)
                            print('-----')
                                
                                
                                
                            b.set_light(1, 'on', True)
                            b.set_light(1, 'xy', [0.6142, 0.3785])
                            b.set_light(1, 'bri', 127)
                            
                        #if event is ongoing, set light red
                        else:
                            status = 'ongoing'
                            upcoming_count = 0
                            ongoing_count += 1
                            off_count = 0
                            
                            print('-----')
                            print('Event: ',start, event['summary'])
                            print('status: ', status)
                            print('prev on: ', prev_on)
                            print('prev colour: ', prev_colour)
                            print('current on: ', current_on)
                            print('current colour: ', current_colour)
                            print('opcoming count: ', upcoming_count)
                            print('ongoing count: ', ongoing_count)
                            print('off count: ', off_count)
                            print('error count: ', err_count)
                            print('-----')
                                
                            b.set_light(1, 'on', True)
                            b.set_light(1, 'xy', [0.6915, 0.3083])
                            
                    #call api every 5 seconds
                    time.sleep(10)
                    err_count = 0 
                except KeyboardInterrupt:
                    print('Programme Stopped')
                    break
                except Exception as e:
                    print('There was an error: ', e)
                    err_count = err_count + 1
                    print('error count: ', err_count)
                    time.sleep(10)
                    if err_count < 10:
                        continue
                    else:
                        break
                        
                   
if __name__ == '__main__':
    main()
 