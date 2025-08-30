import re
import sys
from datetime import datetime
from ics import Calendar
import requests
from dateutil import tz
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
# from pytz import timezone  # alternative if using older Python

ITALY_TZ = ZoneInfo("Europe/Rome")  # CET/CEST automatic
readme_path = Path(__file__).resolve().parents[2] / "README.md"

# 🔗 Your ICS link
ICS_URL = "https://calendar.google.com/calendar/ical/1c512861d9ca4686edd8ffdf6bece495b11a4a764ed045b1f809c9ef0f1903f5%40group.calendar.google.com/public/basic.ics"

# Read start/end dates from command line
if len(sys.argv) < 3:
    print("Usage: update_calendar.py START_DATE END_DATE (YYYY-MM-DD)")
    sys.exit(1)

start_str, end_str = sys.argv[1], sys.argv[2]
start = datetime.strptime(start_str, "%Y-%m-%d").replace(tzinfo=tz.UTC)
end = datetime.strptime(end_str, "%Y-%m-%d").replace(tzinfo=tz.UTC)

# Fetch and parse calendar
r = requests.get(ICS_URL)
c = Calendar(r.text)

# Filter events
events = [
    e for e in c.events
    if e.begin and start <= e.begin <= end
]

# Sort events by date
events.sort(key=lambda e: e.begin)

# Format as Markdown
if events:

    md_lines = []

    for e in events:
        start = e.begin.astimezone(ITALY_TZ)
        end = e.end.astimezone(ITALY_TZ) if e.end else None

        # Format: 2025, Nov 17, 09:30am - 11:30am
        start_str = start.strftime("%Y, %b %d, %I:%M%p")
        end_str = end.strftime("%I:%M%p") if end else ""
        # Fix AM/PM to lowercase
        start_str = start_str.replace("AM", "am").replace("PM", "pm")
        end_str = end_str.replace("AM", "am").replace("PM", "pm")

        time_range = f"**{start_str} - {end_str}**" if end_str else f"**{start_str}**"

        if e.location:
            md_lines.append(f"- {time_range}. {e.location}")
        else:
            md_lines.append(f"- {time_range}")
        md_output = "\n".join(md_lines)
else:
    md_output = f"_No events between {start_str} and {end_str}._"

# Update README
with open(readme_path, "r") as f:
    readme = f.read()

new_readme = re.sub(
    r"(<!-- CALENDAR:START -->)(.*?)(<!-- CALENDAR:END -->)",
    f"<!-- CALENDAR:START -->\n{md_output}\n<!-- CALENDAR:END -->",
    readme,
    flags=re.DOTALL
)

with open(readme_path, "w") as f:
    f.write(new_readme)