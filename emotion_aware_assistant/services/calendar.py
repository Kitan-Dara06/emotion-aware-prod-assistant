
from emotion_aware_assistant.gloabal_import import *

from emotion_aware_assistant.database import SessionLocal
from emotion_aware_assistant.services.user_token import UserToken
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_calendar_service(email: str):
    db = SessionLocal()
    token = db.query(UserToken).filter_by(email=email).first()
    db.close()
    
    if not token:
        raise Exception("User not authorized")

    creds = Credentials(
        token=token.token,
        refresh_token=token.refresh_token,
        token_uri=token.token_uri,
        client_id=token.client_id,
        client_secret=token.client_secret,
        scopes=token.scopes.split(","),
    )
    return build("calendar", "v3", credentials=creds)



def create_event(event, time, repeat=None):
    service = get_calendar_service()

    # 1. Get current time in Lagos
    lagos_tz = pytz.timezone("Africa/Lagos")
    now = datetime.now(lagos_tz)

    # 2. Parse user-provided time, localized to Africa/Lagos
    start_time = dateparser.parse(
        time,
        settings={
            'PREFER_DATES_FROM': 'future',
            'TIMEZONE': 'Africa/Lagos',
            'RETURN_AS_TIMEZONE_AWARE': True
        }
    )

    if not start_time:
        raise ValueError(f"❌ Could not parse time: {time}")

    # 3. Ensure parsed time is in the future (shift by 7 days if not)
    if start_time < now:
        start_weekday = start_time.weekday()
        now_weekday = now.weekday()
        days_ahead = (start_weekday - now_weekday + 7) % 7 or 7
        start_time += timedelta(days=days_ahead)

    # 4. Compute end time
    end_time = start_time + timedelta(hours=1)

    # 5. Build the event body
    event_body = {
        'summary': event,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'Africa/Lagos',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'Africa/Lagos',
        },
    }

    # 6. Recurrence logic (optional)
    if repeat:
        rrule = None
        repeat = repeat.lower().strip()

        if "daily" in repeat:
            rrule = "RRULE:FREQ=DAILY"
        elif "weekly" in repeat or "every" in repeat:
            days_map = {
                "monday": "MO", "tuesday": "TU", "wednesday": "WE",
                "thursday": "TH", "friday": "FR", "saturday": "SA", "sunday": "SU"
            }
            for day, code in days_map.items():
                if day in repeat:
                    rrule = f"RRULE:FREQ=WEEKLY;BYDAY={code}"
                    break
            if "weekdays" in repeat:
                rrule = "RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR"

        if rrule:
            event_body['recurrence'] = [rrule]

    # 7. Create the event
    created_event = service.events().insert(
        calendarId="ololadeaaliyah@gmail.com",
        body=event_body
    ).execute()

    return f"🚀 Event created: {created_event.get('htmlLink')}"


def update_calendar_event(event: str, new_time: str) -> str:
    service = get_calendar_service()

    events_result = service.events().list(
        calendarId='ololadeaaliyah@gmail.com',
        q=event,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    events = events_result.get('items', [])

    if not events:
        return "No events found at all."

    event_titles = [ev.get("summary", "") for ev in events if ev.get("summary")]
    best_matches = get_close_matches(event, event_titles, n=3, cutoff=0.6)

    matching_event = None  # ✅ Safe default

    # 1️⃣ No close match — try soft substring match
    if not best_matches:
        for ev in events:
            if event.lower() in ev.get("summary", "").lower():
                matching_event = ev
                break
        if not matching_event:
            return f"No events matched or contained '{event}'."

    # 2️⃣ Multiple ambiguous matches
    elif len(set(best_matches)) > 1:
        event_descriptions = [
            f"{ev['summary']} @ {ev['start'].get('dateTime', 'Unknown')}"
            for ev in events
            if ev.get("summary") in best_matches
        ]
        return (
            f"🔁 Found multiple events matching '{event}':\n" +
            "\n".join(event_descriptions) +
            "\nPlease clarify."
        )

    # 3️⃣ One clear match
    else:
        matching_event = next(ev for ev in events if ev.get("summary") == best_matches[0])

    if not matching_event:
        return "No exact matching event found."

    # Parse new time
    lagos_tz = pytz.timezone("Africa/Lagos")
    new_start = dateparser.parse(
        new_time,
        settings={
            'PREFER_DATES_FROM': 'future',
            'TIMEZONE': 'Africa/Lagos',
            'RETURN_AS_TIMEZONE_AWARE': True
        }
    )

    if not new_start:
        raise ValueError(f"⚠️ Could not parse the new time: '{new_time}'.")

    # 🧠 Handle timezone correctly
    if new_start.tzinfo is None:
        new_start = lagos_tz.localize(new_start)
    else:
        new_start = new_start.astimezone(lagos_tz)

    # Optional: shift into future if it's behind now
    now = datetime.now(lagos_tz)
    if new_start < now:
        print("⏩ Adjusting to future date because parsed time was in the past.")
        new_start += timedelta(days=1)

    new_end = new_start + timedelta(hours=1)

    # ✅ Print original event
    print(f"🔍 Original: {matching_event['summary']} @ {matching_event['start']['dateTime']}")
    print(f"🕒 Parsed start: {new_start.isoformat()} → {new_end.isoformat()}")

    matching_event['start'] = {
        'dateTime': new_start.isoformat(),
        'timeZone': 'Africa/Lagos'
    }
    matching_event['end'] = {
        'dateTime': new_end.isoformat(),
        'timeZone': 'Africa/Lagos'
    }

    updated_event = service.events().update(
        calendarId="ololadeaaliyah@gmail.com",
        eventId=matching_event['id'],
        body=matching_event
    ).execute()

    return f"✅ Event rescheduled: {updated_event.get('htmlLink')}"

def fetch_upcoming_events_for_user(user_email: str, max_results=5):
    
    service = get_calendar_service(user_email)

    now = datetime.utcnow().isoformat() + 'Z'
    max_time = (datetime.utcnow() + timedelta(days=3)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary',  
        timeMin=now,
        timeMax=max_time,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    upcoming_events = []
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No Title')
        upcoming_events.append(f"📅 Event: {summary} at {start}")

    return upcoming_events

