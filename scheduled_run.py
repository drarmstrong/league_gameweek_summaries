"""Email the gameweek prompt automatically once a gameweek's scores are final.

Meant to be triggered on a frequent schedule by
``.github/workflows/gameweek_report.yml``, where most runs do nothing:

- ``gate`` decides from the cached schedule in ``fpl_data/schedule.json``
  alone (no network, no third-party packages) whether a check is worthwhile.
  It is only due from 05:00 UTC the day after the next unreported
  gameweek's last kickoff, or when the cached schedule is old enough to need refreshing.
- ``run`` refreshes the cached schedule, and if the gameweek is final builds
  the match reports, emails the prompt and records the gameweek as reported
  so each one is only sent once.
"""
import argparse
import json
import os
import smtplib
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from pathlib import Path

STATE_FILE = Path("fpl_data/schedule.json")
REPORTS_DIR = Path("reports")

# FPL confirms scores (data_checked) the day after the last match, so start
# polling at this UTC hour on the following day
CHECK_START_HOUR = 5
# Fallback for a gameweek with no confirmed kickoff times
NO_KICKOFF_GRACE = timedelta(days=3)
# Kickoff times move (TV picks, postponements), so refresh at least this often
SCHEDULE_MAX_AGE = timedelta(days=3)


def now():
    return datetime.now(timezone.utc)


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_state():
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text())


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def check_opens_at(state):
    """Return (gameweek, time) from which the next unreported gameweek could be final.

    The time is None when no gameweek is pending, i.e. the season is over.
    """
    gameweek = state["last_reported_gameweek"] + 1
    info = state["gameweeks"].get(str(gameweek))
    if info is None:
        return gameweek, None
    if info["last_kickoff"]:
        day_after = parse_time(info["last_kickoff"]) + timedelta(days=1)
        return gameweek, day_after.replace(hour=CHECK_START_HOUR, minute=0, second=0)
    return gameweek, parse_time(info["deadline"]) + NO_KICKOFF_GRACE


def is_due(state):
    """Return (due, reason) using only the cached schedule."""
    if not state:
        return True, "no cached schedule yet"
    if now() - parse_time(state["refreshed_at"]) > SCHEDULE_MAX_AGE:
        return True, "cached schedule needs refreshing"
    gameweek, opens = check_opens_at(state)
    if opens is None:
        return False, f"no GW{gameweek} in the schedule, season is over"
    if now() < opens:
        return False, f"GW{gameweek} can't be final before {opens:%Y-%m-%d %H:%M} UTC"
    return True, f"GW{gameweek} may be final"


def fetch_schedule():
    """Return (schedule, events): each gameweek's deadline and last kickoff, plus the raw events."""
    from utils import get_fixtures, get_player_data

    events = get_player_data()["events"]
    kickoffs = defaultdict(list)
    for fixture in get_fixtures():
        # Postponed fixtures have no gameweek or kickoff time until rearranged
        if fixture["event"] and fixture["kickoff_time"]:
            kickoffs[fixture["event"]].append(fixture["kickoff_time"])

    schedule = {
        str(event["id"]): {
            "deadline": event["deadline_time"],
            # ISO 8601 UTC strings sort chronologically
            "last_kickoff": max(kickoffs[event["id"]], default=None),
        }
        for event in events
    }
    return schedule, events


def refresh_state(state, schedule, events):
    """Update the cached schedule, starting afresh on the first run or a new season."""
    season_start = schedule["1"]["deadline"]
    if state.get("season_start") != season_start:
        # Don't email gameweeks that finished before the automation existed
        completed = [e["id"] for e in events if e["finished"] and e["data_checked"]]
        state = {
            "season_start": season_start,
            "last_reported_gameweek": max(completed, default=0),
            "gameweeks": {},
            "refreshed_at": None,
        }
        print(f"Starting a new schedule from GW{state['last_reported_gameweek'] + 1}.")

    # Only touch refreshed_at when needed so hourly checks don't churn the file
    if (schedule != state["gameweeks"] or state["refreshed_at"] is None
            or now() - parse_time(state["refreshed_at"]) > SCHEDULE_MAX_AGE):
        state["gameweeks"] = schedule
        state["refreshed_at"] = now().isoformat(timespec="seconds")
    return state


def is_final(gameweek, events, h2h_league_id):
    """Whether FPL has confirmed the scores and the head-to-head results are in."""
    from utils import get_h2h_league_matches

    event = next((e for e in events if e["id"] == gameweek), None)
    if not (event and event["finished"] and event["data_checked"]):
        print(f"GW{gameweek} scores are not confirmed yet.")
        return False

    matches = [m for m in get_h2h_league_matches(h2h_league_id)["results"] if m["event"] == gameweek]
    if not matches or not all(
        m["entry_1_win"] or m["entry_1_draw"] or m["entry_1_loss"] for m in matches
    ):
        print(f"GW{gameweek} head-to-head results are not in yet.")
        return False
    return True


def build_prompt(match_reports, brutality_level):
    """Assemble the prompt in the same way as the Streamlit app."""
    full_prompt = Path("prompt_task.md").read_text()
    full_prompt += f"\nBrutality Level: {brutality_level}\n"
    full_prompt += Path("prompt_detail.md").read_text()
    full_prompt += f"\n{json.dumps(match_reports, indent=2)}\n"
    return full_prompt


def send_email(subject, body, attachments):
    """Send via SMTP over SSL; the defaults suit Gmail with an app password."""
    username = os.environ["SMTP_USERNAME"]
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = username
    message["To"] = os.environ.get("EMAIL_TO") or username
    message.set_content(body)
    for path in attachments:
        message.add_attachment(path.read_bytes(), maintype="text", subtype="plain", filename=path.name)

    host = os.environ.get("SMTP_HOST") or "smtp.gmail.com"
    port = int(os.environ.get("SMTP_PORT") or 465)
    with smtplib.SMTP_SSL(host, port) as server:
        server.login(username, os.environ["SMTP_PASSWORD"])
        server.send_message(message)


def report(gameweek, config, dry_run):
    """Build the gameweek's prompt, save it under reports/ and email it."""
    from pipeline import build_match_reports

    with open("fpl_data/bios.json") as f:
        bios = json.load(f)

    match_reports = build_match_reports(config["h2h_league_id"], gameweek, bios)
    full_prompt = build_prompt(match_reports, config.get("brutality_level", 3))

    REPORTS_DIR.mkdir(exist_ok=True)
    prompt_path = REPORTS_DIR / f"GW{gameweek}_prompt.md"
    data_path = REPORTS_DIR / f"GW{gameweek}_match_reports.json"
    prompt_path.write_text(full_prompt)
    data_path.write_text(json.dumps(match_reports, indent=2))
    print(f"Saved {prompt_path} and {data_path}.")

    if dry_run:
        print("Dry run, so no email sent.")
        return
    send_email(
        subject=f"FPL GW{gameweek} match reports are ready",
        body=f"GW{gameweek} is final. Paste the prompt below into your LLM of choice.\n\n{full_prompt}",
        attachments=[prompt_path, data_path],
    )
    print(f"Emailed GW{gameweek} report.")


def gate():
    due, reason = is_due(load_state())
    print(f"{'Due' if due else 'Not due'}: {reason}.")
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"due={str(due).lower()}\n")


def run(force_gameweek=None, dry_run=False):
    with open("fpl_data/config.json") as f:
        config = json.load(f)

    schedule, events = fetch_schedule()
    state = refresh_state(load_state(), schedule, events)

    if force_gameweek:
        gameweek = force_gameweek
    else:
        gameweek, opens = check_opens_at(state)
        if opens is None or now() < opens or not is_final(gameweek, events, config["h2h_league_id"]):
            if not dry_run:
                save_state(state)
            return

    report(gameweek, config, dry_run)
    if not dry_run:
        state["last_reported_gameweek"] = max(state["last_reported_gameweek"], gameweek)
        save_state(state)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("gate", help="Decide from the cached schedule whether a check is due")
    run_parser = subparsers.add_parser("run", help="Check the gameweek and email the report if final")
    run_parser.add_argument("--gameweek", type=int, help="Report this gameweek now, skipping the checks")
    run_parser.add_argument("--dry-run", action="store_true", help="Save the report locally without emailing or updating the schedule")
    args = parser.parse_args()

    if args.command == "gate":
        gate()
    else:
        run(args.gameweek, args.dry_run)
