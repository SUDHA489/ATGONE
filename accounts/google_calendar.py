import os
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from django.conf import settings

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
CALENDAR_ID = "primary"  # Use "primary" for the default calendar

def create_google_calendar_event(appointment):
    credentials = service_account.Credentials.from_service_account_file(
        settings.GOOGLE_CREDENTIALS_PATH, scopes=SCOPES
    )

    service = build("calendar", "v3", credentials=credentials)

    start_time = datetime.datetime.combine(appointment.date, appointment.start_time)
    end_time = datetime.datetime.combine(appointment.date, appointment.end_time)

    event = {
        "summary": f"Appointment with {appointment.doctor.get_full_name()}",
        "description": f"Specialty: {appointment.specialty}",
        "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Kolkata"},
        # "attendees": [{"email": appointment.doctor.email}, {"email": appointment.patient.email}],
        # "reminders": {"useDefault": True},
    }

    event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()

    return event.get("htmlLink")  # Return event link for reference
