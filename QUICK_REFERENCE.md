# Quick Reference

## Running the App

### macOS/Linux
```bash
# Quickest way
bash quickstart.sh

# Or manually
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

### Windows
```bash
# Quickest way
quickstart.bat

# Or manually
venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## URLs

- **Local Development**: http://localhost:8501
- **Streamlit Cloud**: https://share.streamlit.io
- **FPL API**: https://fantasy.premierleague.com/api

## Project Files

| File | Purpose |
|------|---------|
| `app.py` | Main Streamlit web application |
| `pipeline.py` | Original CLI pipeline (still works) |
| `utils.py` | FPL API utility functions |
| `llm_summary.py` | LLM integration code |
| `prompts.json` | LLM prompt templates |
| `Dockerfile` | Docker container configuration |
| `.streamlit/config.toml` | Streamlit theming & settings |

## Configuration Files

| File | Purpose | Note |
|------|---------|------|
| `fpl_data/config.json` | League settings | Edit with your league ID & gameweek |
| `fpl_data/bios.json` | Team information | Edit with your managers & teams |
| `prompts.json` | LLM prompts | Usually doesn't need changing |

## Key Features

- 🌐 Web interface (no CLI needed)
- ⚙️ Edit config in the browser
- ▶️ Run pipeline with one click
- 📊 View results instantly
- 🚀 Deploy to cloud easily

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run app.py

# Run CLI pipeline
python pipeline.py

# Build Docker image
docker build -t fpl-reports .

# Run Docker image
docker run -p 8501:8501 fpl-reports
```

## Deployment Options (Ranked by Ease)

1. **Streamlit Cloud** ⭐⭐⭐ - Connect GitHub, auto-deploy
2. **Docker + Cloud** ⭐⭐⭐ - Push image to cloud
3. **Heroku** ⭐⭐ - Traditional PaaS
4. **VPS** ⭐ - Full control, most setup

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| App won't start | Check `config.json` and `bios.json` exist |
| API errors | FPL API may be rate limited, try again later |
| Port in use | Run on different port: `streamlit run app.py --server.port 8502` |

## Documentation

- 📖 **[STREAMLIT_SETUP.md](STREAMLIT_SETUP.md)** - This conversion summary
- 🚀 **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed deployment guide
- 👨‍💻 **[DEVELOPMENT.md](DEVELOPMENT.md)** - Development customization
- 📋 **[README.md](README.md)** - Original project info

## Support Resources

- Streamlit Docs: https://docs.streamlit.io
- FPL API: https://fantasy.premierleague.com/api/
- GitHub Issues: Check your repo issues
