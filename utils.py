import requests

BASE_URL = "https://fantasy.premierleague.com/api"

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
