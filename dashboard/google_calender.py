import datetime
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def create_google_calendar_event(appointment):
    print("INSIDE CALENDAR FUNCTION")
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(current_dir, "token.json")
    creds = None
    
    if os.path.exists(json_path):
        print("TOKEN EXISTS")
        creds = Credentials.from_authorized_user_file(json_path, SCOPES)
    else:
        print("token.json not found in current directory")

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=8080)
        
        # Save the credentials for the next run
        with open(json_path, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Prepare event details
        event = {
            'summary': f'Appointment with Dr. {appointment.get("doctor").user.username}',
            'start': {
                'dateTime': appointment.get('startdatetime'),
                'timeZone': 'Asia/Kolkata',  # Update timezone as per your requirements
            },
            'end': {
                'dateTime': appointment.get('enddatetime'),
                'timeZone': 'Asia/Kolkata',  # Update timezone as per your requirements
            },
            'attendees': [
                {'email': appointment.get('patient').user.email},
                {'email': appointment.get('doctor').user.email},
            ],
        }

        # Insert event to Google Calendar
        event = service.events().insert(calendarId='primary', body=event).execute()
        print(f'Event created: {event.get("htmlLink")}')
        
        # Delete token.json after successful event creation
        if os.path.exists(json_path):
            os.remove(json_path)
            print("Deleted token.json")

        return event

    except HttpError as error:
        print(f"An error occurred: {error}")
