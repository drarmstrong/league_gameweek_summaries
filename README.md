This repository contains Python scripts to extract data from the FPL API for head-to-head leagues, generating prompts for LLM-based match reports.

pipeline.py
    This is the main script that needs to be run.
    This runs API calls and organises the data, generating match data as a prompt in json format.
    There is an optional set of commands to run the prompt with a local LLM using Ollama.

utils.py
    This contains helper scripts to do the FPL API calls

prompts.json
    This contains additional prompts that help to better inform the LLM of the task and context.
    These can be optimised for each personal users preferences.

llm_summary.py
    This optional scripts runs the local LLMs using Ollama (needs a separate installation)

fpl_data/bios_template.json
    Gives the template for providing the team information (FPL managers IDs, team names, manager names, extra info)
    For the script to run, this needs to be renamed to bios.json

fpl_data/config_template.json
    Gives the template for providing the league ID and relevant gameweek (this will need updating for each new gameweek)

