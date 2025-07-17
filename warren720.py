from flask import Flask, render_template, url_for
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone
import pytz


site = Flask(__name__)


@site.route("/")
def index():
    return render_template("index.html")


@site.route("/calendar")
def calendar():
    return render_template("calendar.html", title="Broadcasting Schedule")


@site.route("/broadcastingSystem")
def broadcasting_system():
    return render_template("broadcastingSystem.html", title="IP Radio")


@site.route("/radio-offline")
def radio_offline():
    # Load credentials
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    SERVICE_ACCOUNT_FILE = '/var/www/ip-radio-event-scheduling-c7d0cf199ba3.json'
    CALENDAR_ID = 'e0d44c68b16f5d4a80e8774fa001762ccb87abfe96523d71e36995db33fadaf5@group.calendar.google.com'

    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )

    service = build("calendar", "v3", credentials=creds)

    now = datetime.utcnow().isoformat() + 'Z'  # RFC3339 UTC timestamp

    events_result = service.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now,
        maxResults=1,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        return render_template("radio_offline.html", time_until=None)

    start_time_str = events[0]['start'].get('dateTime')
    start_time = datetime.fromisoformat(start_time_str).astimezone(pytz.UTC)
    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    delta = start_time - now_utc

    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    time_until = f"{hours}h {minutes}m {seconds}s"

    start_time_iso = start_time.isoformat()
    return render_template("radio_offline.html", time_until=time_until, start_time=start_time_iso)



if __name__ == "__main__":
    site.run(debug=True)
