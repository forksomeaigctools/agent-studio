import json
from pathlib import Path

from desktop_env.eval.envs.gspace.gservice import GoogleService


class GoogleCalendarService(GoogleService):
    def __init__(self, token_path: str) -> None:
        scopes = ["https://www.googleapis.com/auth/calendar"]
        super().__init__(
            scopes=scopes,
            token_path=token_path,
            service_name="calendar",
            service_version="v3",
        )

    def list_calendars(self) -> list[dict]:
        page_token = None
        calendar_entry_list = []
        while True:
            calendar_list = (
                self.service.calendarList().list(pageToken=page_token).execute()
            )
            for calendar_entry in calendar_list["items"]:
                calendar_entry_list.append(calendar_entry)

            page_token = calendar_list.get("nextPageToken")
            if not page_token:
                break
        return calendar_entry_list

    def create_event(
        self,
        summary: str | None,
        location: str | None,
        description: str | None,
        start_time: str,
        end_time: str,
        attendees: list[str] | None = None,
        calendar_id: str | None = "primary",
        time_zone: str | None = "UTC",
    ) -> dict[str, str]:
        event_info = {
            "summary": summary,
            "location": location,
            "description": description,
            "start": {
                "dateTime": start_time,
                "timeZone": time_zone,
            },
            "end": {
                "dateTime": end_time,
                "timeZone": time_zone,
            },
            "attendees": [{"email": attendee} for attendee in attendees]
            if attendees
            else [],
        }
        event = (
            self.service.events()
            .insert(calendarId=calendar_id, body=event_info)
            .execute()
        )
        return event

    def delete_event(self, event_id: str, calendar_id: str = "primary") -> bool:
        try:
            self.service.events().delete(
                calendarId=calendar_id, eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f"An error occurred: {e}")
            return False

    def get_event(self, event_id: str, calendar_id: str = "primary") -> dict[str, str]:
        event = (
            self.service.events()
            .get(calendarId=calendar_id, eventId=event_id)
            .execute()
        )
        return event

    def update_event(
        self, event_id: str, updated_event: dict[str, str], calendar_id: str = "primary"
    ) -> dict[str, str]:
        event = (
            self.service.events()
            .update(calendarId=calendar_id, eventId=event_id, body=updated_event)
            .execute()
        )
        return event

    def search_events(
        self, start_time: str, end_time: str, calendar_id: str = "primary"
    ) -> list[dict[str, str]]:
        events_result = (
            self.service.events()
            .list(
                calendarId=calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])


class GoogleCalendarEnv:
    def __init__(self, token_path: str, config_file: Path | str) -> None:
        self.service = GoogleCalendarService(token_path=token_path)
        with open(config_file, "r") as f:
            config = json.load(f)
        self.config = config

    def reset(self) -> bool:
        return True