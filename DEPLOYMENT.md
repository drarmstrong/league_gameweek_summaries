# Streamlit App Deployment Guide

This guide helps you deploy the FPL League Match Reports Generator as a Streamlit application.

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

3. Open your browser to `http://localhost:8501`

## Features

The Streamlit app provides:

- **Web Interface**: User-friendly UI instead of CLI
- **Configuration Panel**: Adjust league ID, gameweek, and team bios without editing files
- **Live Pipeline Execution**: Run the pipeline directly from the web interface
- **Real-time Progress**: See status updates as the pipeline processes matches
- **Results Visualization**: View match reports and generated prompts in the browser

## Cloud Deployment

### Option 1: Streamlit Cloud (Easiest)

Free hosting directly from GitHub:

1. Push your repository to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Connect your GitHub repo, select branch and main file (`app.py`)
5. Click "Deploy"

**Pros**: Free, automatic updates from GitHub, built for Streamlit  
**Cons**: Limited to free tier resources

### Option 2: Heroku

1. Create `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

2. Create `setup.sh`:
```bash
mkdir -p ~/.streamlit/
echo "[browser]
headless = true
[server]
port = $PORT
enableCORS = false
" > ~/.streamlit/config.toml
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
```

### Option 3: Docker (Self-Hosted)

1. Build the image:
```bash
docker build -t fpl-reports .
```

2. Run locally:
```bash
docker run -p 8501:8501 fpl-reports
```

3. Deploy to cloud (AWS, GCP, Azure, DigitalOcean, etc.):
```bash
docker push your-registry/fpl-reports:latest
# Then deploy using your cloud provider's container service
```

### Option 4: Traditional VPS (AWS EC2, DigitalOcean, Linode)

1. SSH into your server
2. Clone the repository
3. Install Python and dependencies
4. Run Streamlit with a process manager (systemd, supervisord)
5. Set up Nginx as a reverse proxy

Example systemd service file:
```ini
[Unit]
Description=FPL Reports Streamlit App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/ubuntu/league_gameweek_summaries
ExecStart=/usr/bin/python3 -m streamlit run app.py --server.port=8501 --logger.level=info
Restart=always

[Install]
WantedBy=multi-user.target
```

## Environment Variables

For production deployments, you may want to:

1. Create a `.env` file (not committed to git):
```
FPL_LEAGUE_ID=588094
FPL_GAMEWEEK=23
```

2. Update `app.py` to read from environment if needed:
```python
import os
h2h_league_id = int(os.getenv("FPL_LEAGUE_ID", 588094))
latest_gameweek = int(os.getenv("FPL_GAMEWEEK", 23))
```

## Troubleshooting

**Issue**: "ModuleNotFoundError" when deploying
- **Solution**: Ensure `requirements.txt` is up to date and all dependencies are listed

**Issue**: API rate limiting
- **Solution**: FPL API is generally stable but consider adding retry logic if needed

**Issue**: Large dataset causing slowness
- **Solution**: Consider caching data in session state (already implemented)

## Maintenance

### Regular Updates

- Keep Streamlit updated: `pip install --upgrade streamlit`
- Monitor FPL API changes
- Test new gameweeks before deploying

### Monitoring

For production deployments, consider:
- Streamlit's built-in error reporting
- Application Performance Monitoring (APM) tools
- Log aggregation services

## File Structure for Deployment

```
league_gameweek_summaries/
├── app.py                    # Main Streamlit app
├── pipeline.py              # Original CLI pipeline
├── llm_summary.py           # LLM integration
├── utils.py                 # Utility functions
├── prompts.json             # LLM prompts
├── requirements.txt         # Python dependencies
├── Dockerfile              # For Docker deployment
├── .streamlit/
│   └── config.toml         # Streamlit configuration
├── fpl_data/
│   ├── config.json         # League configuration
│   └── bios.json           # Team bios
└── reports/                # Generated match reports
```

## Support

For issues:
1. Check Streamlit documentation: https://docs.streamlit.io
2. Review FPL API docs: https://fantasy.premierleague.com/api/
3. Check repository issues on GitHub
