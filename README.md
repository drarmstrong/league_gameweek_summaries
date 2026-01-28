# FPL Head-to-Head League Summary Pipeline

This repository contains Python scripts to extract data from the FPL API for head-to-head leagues, generating prompts for LLM-based match reports.

---

# Installation instructions

You will need a Python installation and use of a terminal.

## Clone the repository

Navigate to the folder you wish to store the repository and run the following commands:

```
git clone https://github.com/drarmstrong/league_gameweek_summaries.git
cd league_gameweek_summaries
```

---

## Create and activate a Virtual Environment (optional)

This step ensures a clean, isolated environment for the project.

### For macOS/Linux:

Create the environment named 'venv' (or whatever you like):

```
python3 -m venv venv
```

Activate the environment:

```
source venv/bin/activate
```

### For Windows (Command Prompt):

Create the environment named 'venv':

```
python -m venv venv
```

Activate the environment:

```
venv\Scripts\activate
```

---

## Install the Dependencies:

Use pip and the -r flag (for "requirement file") to install all packages listed in requirements.txt:

```
pip install -r requirements.txt
```

---

## Run the Script(s):

### Option 1: Run as a Streamlit App (Recommended)

The project now includes a web-based interface powered by Streamlit. To run the app:

```
streamlit run app.py
```

This will open a local web interface where you can:
- Adjust the league ID and gameweek settings
- Edit team bios and configuration in real-time
- Run the pipeline with a single click
- View the generated match reports

### Option 2: Run the CLI Pipeline

To run the original command-line pipeline:

```
python pipeline.py
```

### Note: you will need to create the config.json and bios.json files from the templates before the code will function (see below for more info)

---

## Deployment

### Deploy on Streamlit Cloud

1. Push your repository to GitHub
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
3. Connect your GitHub account and select this repository
4. Streamlit Cloud will automatically detect and deploy `app.py`

### Deploy Locally with Docker

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t fpl-reports .
docker run -p 8501:8501 fpl-reports
```

---

## More info about the scripts and data

### `pipeline.py`

This is the main script that needs to be run.  
It runs API calls and organises the data, generating match data as a prompt in JSON format.  
There is an optional set of commands to run the prompt with a local LLM using Ollama.

---

### `utils.py`

Contains helper scripts to do the FPL API calls.

---

### `prompts.json`

Contains additional prompts that help to better inform the LLM of the task and context.  
These can be optimised for each personal user's preferences.

---

### `llm_summary.py`

This optional script runs the local LLMs using Ollama (needs a separate installation).

---

### `fpl_data/bios_template.json`

Gives the template for providing the team information (FPL managers IDs, team names, manager names, extra info).  
For the script to run, this needs to be renamed to `bios.json`.  
If your league contains an odd number of teams with an AVERAGE team, then the first block of the template needs to be retained.

---

### `fpl_data/config_template.json`

Gives the template for providing the league ID and relevant gameweek (this will need updating for each new gameweek).  
For the script to run, this needs to be renamed to `config.json`.
