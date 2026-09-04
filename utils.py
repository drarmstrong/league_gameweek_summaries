import requests
from collections import defaultdict

BASE_URL = "https://fantasy.premierleague.com/api"

FORM_WINDOW = 5

def get_h2h_league_standings(league_id):
    url = f"{BASE_URL}/leagues-h2h/{league_id}/standings/"
    return requests.get(url).json()

def get_h2h_league_matches(league_id):
    """
    Fetch all paginated match pages for a head-to-head league and return a single
    dict with an aggregated 'results' list.
    """
    matches_url = f"{BASE_URL}/leagues-h2h-matches/league/{league_id}"
    all_results = []
    page = 1

    while True:
        resp = requests.get(matches_url, params={"page": page})
        resp.raise_for_status()
        data = resp.json()

        page_results = data.get("results", [])
        all_results.extend(page_results)

        # Stop when API indicates no next page
        if not data.get("has_next", False):
            break

        page += 1

    return {"results": all_results}

def get_manager_history(manager_id):
    url = f"{BASE_URL}/entry/{manager_id}/history/"
    return requests.get(url).json()

def get_manager_latest_transfers(manager_id):
    url = f"{BASE_URL}/entry/{manager_id}/transfers-latest/"
    return requests.get(url).json()

def get_gameweek_picks(manager_id, gw):
    url = f"{BASE_URL}/entry/{manager_id}/event/{gw}/picks/"
    return requests.get(url).json()

def get_player_data():
    url = f"{BASE_URL}/bootstrap-static/"
    return requests.get(url).json()

def get_recent_form(fixtures, gameweek, window=FORM_WINDOW):
    """Build a lookup of recent head-to-head form for every team in the league.

    Looks back over the ``window`` gameweeks immediately before ``gameweek``
    (fewer if the season hasn't reached that many yet) and records a W, D or L
    for each completed match.

    Returns a dict keyed by manager entry id — or the string ``"AVERAGE"`` for
    the league's average team, which has no entry id — mapping to a form string
    ordered from earliest to latest, e.g. ``"WDLLW"``. Teams with no completed
    matches in the window are absent from the lookup.
    """
    first_gameweek = max(1, gameweek - window)
    results_by_team = defaultdict(list)

    for match in fixtures:
        event = match["event"]
        if event < first_gameweek or event >= gameweek:
            continue

        for side in ("entry_1", "entry_2"):
            if match[f"{side}_win"]:
                result = "W"
            elif match[f"{side}_draw"]:
                result = "D"
            elif match[f"{side}_loss"]:
                result = "L"
            else:
                # Fixture not played (or void), so it contributes no form
                continue
            # The AVERAGE team has no entry id, so fall back to its name
            team_key = match[f"{side}_entry"] or match[f"{side}_name"]
            results_by_team[team_key].append((event, result))

    return {
        team_key: "".join(result for _, result in sorted(results, key=lambda r: r[0]))
        for team_key, results in results_by_team.items()
    }


def get_latest_gameweek():
    """Return the most recent gameweek whose scores are final.

    The ``is_previous`` flag can't be used for this: it means "the gameweek
    before ``is_current``", and ``is_current`` only moves on once the next
    deadline passes — so between a gameweek finishing and the following
    deadline, ``is_previous`` lags a week behind. Instead take the highest
    event that is both ``finished`` and ``data_checked``; the latter is only
    set once bonus points and any corrections have been applied, so we never
    report on provisional scores. Falls back to gameweek 1 before any
    gameweek has completed.
    """
    url = f"{BASE_URL}/bootstrap-static/"
    data = requests.get(url).json()
    completed = [
        event["id"] for event in data.get("events", [])
        if event.get("finished") and event.get("data_checked")
    ]
    return max(completed) if completed else 1
