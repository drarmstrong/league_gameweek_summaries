import json
from utils import (
    get_h2h_league_standings,
    get_h2h_league_matches,
    get_manager_history,
    get_gameweek_picks,
    get_player_data
)
from llm_summary import query_ollama, save_output
from pprint import pprint

print("Loading data from API...")

# Load config, bios and prompts data
with open("fpl_data/config.json") as f:
    config = json.load(f)

with open("fpl_data/bios.json") as f:
    bios = json.load(f)

with open("prompts.json") as f:
    prompts = json.load(f)

h2h_league_id = config["h2h_league_id"]
gameweek = config["latest_gameweek"]

# Load player data for name lookups
player_data = get_player_data()
players = player_data["elements"]
player_name_lookup = {p["id"]: p["web_name"] for p in players}
player_points_lookup = {p["id"]: p["event_points"] for p in players}

def extract_match_summary(manager_id, opponent_id, gameweek):
    picks_data = get_gameweek_picks(manager_id, gameweek)  # Get data from API
    picks = picks_data["picks"]
    manager_points = picks_data["entry_history"]["points"]
    bench_points = picks_data["entry_history"]["points_on_bench"]
    transfers_made = picks_data["entry_history"]["event_transfers"]
    chip = picks_data.get("active_chip") or "None"

    for position in standings:
        if position["entry"] == manager_id:
            rank = position["rank"]
            previous_rank = position["last_rank"]
            break

    player_points = []
    bench_player_points = []

    for pick in picks:
        name = player_name_lookup[pick["element"]]
        points = player_points_lookup[pick["element"]]
        player_gameweek = {
            "name": name,
            "points": points
        }
        if pick["is_captain"]:
            player_captain = player_name_lookup[pick["element"]]
        # Skip bench players unless Bench Boost chip is active
        if pick["position"] > 11 and chip != "bboost":
            bench_player_points.append(player_gameweek)
            continue
        else:
            player_points.append(player_gameweek)

    top_players = sorted(player_points, key=lambda x: x['points'], reverse=True)[:3]
    bottom_players = sorted(player_points, key=lambda x: x["points"])[:3]

    team_bio = bios.get(str(manager_id), "No bio available.")

    return {
        "manager_id": manager_id,
        "manager_points": manager_points,
        "bench_points": bench_points,
        "league_rank": rank,
        "previous_league_rank": previous_rank,
        "chip_used": chip,
        "number_of_transfers": transfers_made,
        "top_scoring_players": top_players,
        "lowest_scoring_players": bottom_players,
        "bench_player_points": bench_player_points,
        "captain": player_captain if 'player_captain' in locals() else "None",
        "team_name": team_bio['team_name'],
        "manager": team_bio['manager'],
        "number_of_league_titles": team_bio['league_wins'],
        "background": team_bio['bio']
    }

# Fetch league data
standings_data = get_h2h_league_standings(h2h_league_id)  # Get data from API
standings = standings_data["standings"]["results"]
matches_data = get_h2h_league_matches(h2h_league_id)  # Get data from API
fixtures = matches_data["results"]

print("Finished loading data from API.")

match_reports = []
match_num = 0


for match in fixtures:
    if match["event"] != gameweek:
        continue
    
    match_num += 1
    print(f"Running process for Match {match_num}...")
    team_1_id = match["entry_1_entry"]
    team_2_id = match["entry_2_entry"]

    team_1_name = match["entry_1_name"]
    team_2_name = match["entry_2_name"]

    if team_1_name != "AVERAGE" and team_2_name != "AVERAGE":
        print(f"Processing match between {team_1_name} and {team_2_name}...")

        team_1 = extract_match_summary(team_1_id, team_2_id, gameweek=gameweek)
        team_2 = extract_match_summary(team_2_id, team_1_id, gameweek=gameweek)

        match_reports.append({
            "match": match_num,
            "team_1": {**team_1, "name": team_1_name},
            "team_2": {**team_2, "name": team_2_name},
            "score": f"{team_1['manager_points']} - {team_2['manager_points']}",
        })
        print("Finished processing match report for Match", match_num)
    elif team_1_name == "AVERAGE":
        print(f"Processing match between Average and {team_2_name}...")
        team_2 = extract_match_summary(team_2_id, team_1_id, gameweek=gameweek)

        match_reports.append({
            "match": match_num,
            "team_1": {"name": bios.get(str(1000001), {}).get("team_name", "Unknown"), 
                       "manager_points": match["entry_1_points"], 
                       "bio": bios.get(str(1000001), "No bio available.")},
            "team_2": {**team_2, "name": team_2_name},
            "score": f"{match['entry_1_points']} - {team_2['manager_points']}",
        })
        print("Finished processing match report for Match", match_num)
    elif team_2_name == "AVERAGE":
        print(f"Processing match between {team_1_name} and Average...")
        team_1 = extract_match_summary(team_1_id, team_2_id, gameweek=gameweek)

        match_reports.append({
            "match": match_num,
            "team_1": {**team_1, "name": team_1_name},
            "team_2": {"name": bios.get(str(1000001), {}).get("team_name", "Unknown"), 
                       "manager_points": match["entry_1_points"], 
                       "bio": bios.get(str(1000001), "No bio available.")},
            "score": f"{team_1['manager_points']} - {match['entry_2_points']}",
        })
        print("Finished processing match report for Match", match_num)
    else:
        print(f"Skipping match {match_num} as it doesn't match.")
                
        

print("All match reports processed. Generating summary...")

# Create prompt for LLM from templates and match reports
full_prompt = (prompts["intro"])
full_prompt += f'\n{match_reports}\n'
full_prompt += prompts["outro"]

print("Full prompt generated.")
pprint(full_prompt)

#######################################
# Local LLM query via Ollama - can be removed if using external LLM
#print("Querying LLM for summary...")
#
#model = "phi4"  # or "mistral" or whatever you've pulled via Ollama
#summary = query_ollama(full_prompt, model=model)
#
#print("LLM summary generated. Saving to file...")
#
# Save to file
#save_output(summary, filename=f"reports/GW{gameweek}_Match_Report.md")
#print(f"LLM summary saved as GW{gameweek}_Match_Report.md")
#######################################