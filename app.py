import json
import streamlit as st
from pathlib import Path
from pprint import pprint
from utils import (
    get_h2h_league_standings,
    get_h2h_league_matches,
    get_manager_history,
    get_gameweek_picks,
    get_player_data
)
from llm_summary import query_ollama, save_output

# Page configuration
st.set_page_config(page_title="FPL League Match Reports", layout="wide")
st.title("⚽ FPL League Match Reports Generator")

# Initialize session state for configs
if "config" not in st.session_state:
    with open("fpl_data/config.json") as f:
        st.session_state.config = json.load(f)

if "bios" not in st.session_state:
    with open("fpl_data/bios.json") as f:
        st.session_state.bios = json.load(f)

if "prompt_task" not in st.session_state:
    with open("prompt_task.md") as f:
        st.session_state.prompt_task = f.read()

if "prompt_detail" not in st.session_state:
    with open("prompt_detail.md") as f:
        st.session_state.prompt_detail = f.read()


# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Config settings
    st.subheader("League Settings")
    h2h_league_id = st.number_input(
        "H2H League ID",
        value=int(st.session_state.config.get("h2h_league_id", 588094)),
        help="The ID of your head-to-head fantasy league"
    )
    latest_gameweek = st.number_input(
        "Latest Gameweek",
        value=int(st.session_state.config.get("latest_gameweek", 23)),
        min_value=1,
        max_value=38,
        help="The gameweek to generate reports for"
    )

    # Brutality slider
    st.subheader("Tone Settings")
    brutality_level = st.slider(
        "Brutality Level",
        min_value=1,
        max_value=5,
        value=3,
        step=1,
        help="Select how harsh/critical the tone of the report should be (1 = mild, 5 = savage)."
    )
    st.session_state.brutality_level = int(brutality_level)
    
    # Bios editor
    st.subheader("Team Bios")
    bios_json_str = st.text_area(
        "Edit team bios (JSON format)",
        value=json.dumps(st.session_state.bios, indent=2),
        height=300,
        help="Edit the team bios configuration. Must be valid JSON."
    )
    
    try:
        st.session_state.bios = json.loads(bios_json_str)
        st.success("✓ Bios JSON is valid")
    except json.JSONDecodeError as e:
        st.error(f"❌ Invalid JSON in bios: {e}")
    
    # Prompt editors
    st.subheader("Report Prompts")
    
    # Task prompt editor
    prompt_task_str = st.text_area(
        "Edit task prompt (Markdown)",
        value=st.session_state.prompt_task,
        height=200,
        help="Edit the task description that sets up the prompt for the LLM."
    )
    st.session_state.prompt_task = prompt_task_str
    
    # Detail prompt editor
    prompt_detail_str = st.text_area(
        "Edit detail prompt (Markdown)",
        value=st.session_state.prompt_detail,
        height=400,
        help="Edit the detailed instructions including brutality level guidance for the LLM."
    )
    st.session_state.prompt_detail = prompt_detail_str


# Main content area
st.subheader("Generate Match Reports")

col1, col2 = st.columns([1, 1])

with col1:
    st.info(
        f"""
        **Current Settings:**
        - League ID: {h2h_league_id}
        - Gameweek: {latest_gameweek}
        - Teams configured: {len(st.session_state.bios)}
        """
    )

with col2:
    st.write("Edit the configuration in the sidebar, then run the pipeline.")


def get_average_standings(standings, match):
    """Extract average standings from league standings"""
    for position in standings:
        if position["entry_name"] == "AVERAGE":
            rank = position["rank"]
            previous_rank = position["last_rank"]
            league_points = position["total"]
            total_points = position["points_for"]
            break
    return {
        "name": st.session_state.bios.get(str(1000001), {}).get("team_name", "Unknown"),
        "manager_points": match["entry_1_points"],
        "league_rank": rank,
        "previous_league_rank": previous_rank,
        "overall_league_points": league_points,
        "overall_fpl_points": total_points,
        "background": st.session_state.bios.get(str(1000001), "No bio available.")
    }


def extract_match_summary(manager_id, gameweek, player_name_lookup, player_points_lookup, standings):
    """Extract summary for a single match"""
    picks_data = get_gameweek_picks(manager_id, gameweek)
    picks = picks_data["picks"]
    manager_points = picks_data["entry_history"]["points"] - picks_data["entry_history"]["event_transfers_cost"]
    bench_points = picks_data["entry_history"]["points_on_bench"]
    transfers_made = picks_data["entry_history"]["event_transfers"]
    chip = picks_data.get("active_chip") or "None"

    for position in standings:
        if position["entry"] == manager_id:
            rank = position["rank"]
            previous_rank = position["last_rank"]
            league_points = position["total"]
            total_points = position["points_for"]
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

    team_bio = st.session_state.bios.get(str(manager_id), "No bio available.")

    return {
        "manager_id": manager_id,
        "manager_points": manager_points,
        "bench_points": bench_points,
        "league_rank": rank,
        "previous_league_rank": previous_rank,
        "overall_league_points": league_points,
        "overall_fpl_points": total_points,
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


# Run pipeline button
if st.button("🚀 Run Pipeline", type="primary", use_container_width=True):
    with st.status("Running pipeline...", expanded=True) as status:
        try:
            st.write("Loading data from API...")
            
            # Load player data for name lookups
            player_data = get_player_data()
            if not player_data:
                st.error("Failed to load player data from API.")
                st.stop()
            
            st.write("✓ Player data loaded successfully")
            players = player_data["elements"]
            player_name_lookup = {p["id"]: p["web_name"] for p in players}
            player_points_lookup = {p["id"]: p["event_points"] for p in players}

            # Fetch league data
            st.write("Loading league standings...")
            standings_data = get_h2h_league_standings(h2h_league_id)
            if not standings_data:
                st.error("Failed to load league standings from API.")
                st.stop()
            
            st.write("✓ League standings loaded successfully")
            standings = standings_data["standings"]["results"]
            
            st.write("Loading league matches...")
            matches_data = get_h2h_league_matches(h2h_league_id)
            if not matches_data:
                st.error("Failed to load league matches from API.")
                st.stop()
            
            st.write("✓ League matches loaded successfully")
            fixtures = matches_data["results"]

            st.write("Finished loading data from API.\n")

            match_reports = []
            match_num = 0

            st.write("Processing matches...")
            progress_bar = st.progress(0)
            
            for match in fixtures:
                if match["event"] != latest_gameweek:
                    continue
                
                match_num += 1
                st.write(f"Processing Match {match_num}...")
                
                team_1_id = match["entry_1_entry"]
                team_2_id = match["entry_2_entry"]
                team_1_name = match["entry_1_name"]
                team_2_name = match["entry_2_name"]

                if team_1_name != "AVERAGE" and team_2_name != "AVERAGE":
                    st.write(f"  → {team_1_name} vs {team_2_name}")
                    team_1 = extract_match_summary(team_1_id, gameweek=latest_gameweek, 
                                                   player_name_lookup=player_name_lookup,
                                                   player_points_lookup=player_points_lookup,
                                                   standings=standings)
                    team_2 = extract_match_summary(team_2_id, gameweek=latest_gameweek,
                                                   player_name_lookup=player_name_lookup,
                                                   player_points_lookup=player_points_lookup,
                                                   standings=standings)

                    match_reports.append({
                        "match": match_num,
                        "team_1": {**team_1, "name": team_1_name},
                        "team_2": {**team_2, "name": team_2_name},
                        "score": f"{team_1['manager_points']} - {team_2['manager_points']}",
                    })
                    
                elif team_1_name == "AVERAGE":
                    st.write(f"  → AVERAGE vs {team_2_name}")
                    team_1 = get_average_standings(standings, match)
                    team_2 = extract_match_summary(team_2_id, gameweek=latest_gameweek,
                                                   player_name_lookup=player_name_lookup,
                                                   player_points_lookup=player_points_lookup,
                                                   standings=standings)

                    match_reports.append({
                        "match": match_num,
                        "team_1": {**team_1, "name": team_1['background']['team_name']},
                        "team_2": {**team_2, "name": team_2_name},
                        "score": f"{match['entry_1_points']} - {team_2['manager_points']}",
                    })
                    
                elif team_2_name == "AVERAGE":
                    st.write(f"  → {team_1_name} vs AVERAGE")
                    team_1 = extract_match_summary(team_1_id, gameweek=latest_gameweek,
                                                   player_name_lookup=player_name_lookup,
                                                   player_points_lookup=player_points_lookup,
                                                   standings=standings)
                    team_2 = get_average_standings(standings, match)

                    match_reports.append({
                        "match": match_num,
                        "team_1": {**team_1, "name": team_1_name},
                        "team_2": {**team_2, "name": team_2['background']['team_name']},
                        "score": f"{team_1['manager_points']} - {match['entry_2_points']}",
                    })
                    
                progress_bar.progress(match_num / max(1, len(fixtures)))

            st.write(f"\n✓ All match reports processed ({match_num} matches)")
            st.write("\nGenerating summary prompt...")

            # Create prompt for LLM from markdown template and match reports
            full_prompt = st.session_state.prompt_task
            # Insert brutality level selected in sidebar
            full_prompt += f"\nBrutality Level: {st.session_state.get('brutality_level', 3)}\n"
            full_prompt += st.session_state.prompt_detail
            full_prompt += f'\n{match_reports}\n'

            st.write("✓ Full prompt generated.")

            status.update(label="Pipeline completed!", state="complete")
            
            # Display results
            st.success(f"✅ Pipeline completed successfully for Gameweek {latest_gameweek}!")
            
            with st.expander("View Match Reports Summary"):
                st.json(match_reports)
            
            with st.expander("View Full Prompt", expanded=True):
                st.text(full_prompt)
            
            # Option to save
            st.info("""
            **Note:** The full LLM summary generation is currently commented out in the pipeline.
            To generate and save match reports, uncomment the LLM query section in the code.
            """)

        except Exception as e:
            status.update(label="Pipeline failed!", state="error")
            st.error(f"❌ Error running pipeline: {str(e)}")
            st.exception(e)


# Display current bios
st.divider()
st.subheader("📋 Current Team Configuration")

bios_col1, bios_col2 = st.columns(2)

with bios_col1:
    st.subheader("Teams in System")
    for manager_id, bio_data in st.session_state.bios.items():
        st.write(f"**{bio_data['team_name']}**")
        st.caption(f"Manager: {bio_data['manager']}")
        st.caption(f"Titles: {bio_data.get('league_wins', 0)}")

with bios_col2:
    st.subheader("League Configuration")
    config_display = {
        "H2H League ID": h2h_league_id,
        "Latest Gameweek": latest_gameweek,
    }
    for key, value in config_display.items():
        st.write(f"**{key}:** {value}")
