# Development Guide

This guide helps you set up the development environment and make modifications to the Streamlit app.

## Project Structure

```
league_gameweek_summaries/
├── app.py                      # Main Streamlit application
├── pipeline.py                 # Original CLI pipeline (still available)
├── llm_summary.py             # LLM integration utilities
├── utils.py                   # FPL API utilities
├── prompts.json               # LLM prompt templates
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker configuration
├── .streamlit/
│   └── config.toml           # Streamlit theming/config
├── fpl_data/
│   ├── config.json           # League settings
│   ├── config_template.json  # Template for config
│   ├── bios.json             # Team information
│   └── bios_template.json    # Template for bios
├── mock_fpl_data/            # Test data for development
│   └── pipeline_mock_data.py # Mock data generator
└── reports/                  # Generated match report outputs
```

## Local Development Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Your Local Setup

Ensure `fpl_data/config.json` and `fpl_data/bios.json` are set up (copy from templates if needed).

### 4. Run the App

```bash
streamlit run app.py
```

Visit `http://localhost:8501` in your browser.

## Development Workflow

### Adding New Features

1. Make changes to `app.py` or supporting files
2. Streamlit hot-reloads automatically on save
3. Test in the browser interface
4. Commit changes to git

### Testing with Mock Data

The project includes mock data for testing without hitting the live FPL API:

```bash
python mock_fpl_data/pipeline_mock_data.py
```

This generates test data that can be used for development.

### Code Style

- Follow PEP 8 guidelines
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and testable

## Key Application Sections

### Configuration Management

Located at the top of `app.py`:
- Loads `config.json` and `bios.json` on startup
- Stores in Streamlit session state for persistence
- User can edit these through the sidebar

### Data Processing Functions

- `get_average_standings()`: Extracts average team data
- `extract_match_summary()`: Processes individual match data

### Main Pipeline Execution

The "Run Pipeline" button triggers:
1. API data fetching
2. Match processing
3. Prompt generation
4. Results display

## Customizing the UI

### Sidebar Configuration

The sidebar allows users to edit:
- League ID
- Current gameweek
- Team bios (JSON)

To add more options, edit the sidebar section in `app.py`:

```python
with st.sidebar:
    st.header("⚙️ Configuration")
    # Add your new configuration options here
```

### Layout and Styling

Use Streamlit's built-in components:
- `st.columns()` for multi-column layouts
- `st.expander()` for collapsible sections
- `st.tabs()` for tabbed interfaces
- Theme configuration in `.streamlit/config.toml`

### Adding New Display Sections

Example of adding a new section:

```python
st.divider()
st.subheader("📊 Your New Section")

if st.button("Do Something"):
    with st.spinner("Processing..."):
        # Your code here
        st.success("Done!")
```

## Integration with LLM

The app currently displays:
- Match reports data
- Generated prompts for LLM input

To enable LLM summary generation:

1. Uncomment the LLM section in `pipeline.py`
2. Ensure Ollama is running (if using local LLM)
3. Update `app.py` to display LLM results

## Performance Optimization

### Caching API Calls

Streamlit's `@st.cache_data` decorator caches expensive operations:

```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_player_data():
    return requests.get(url).json()
```

### Session State

Use session state to persist data across reruns:

```python
if "key" not in st.session_state:
    st.session_state.key = initial_value
```

## Debugging

### Enable Debug Mode

Add to `.streamlit/config.toml`:
```ini
[logger]
level = "debug"
```

### Common Issues

**Issue**: App refreshes on every input
- **Solution**: Use `st.session_state` to persist values

**Issue**: API calls timeout
- **Solution**: Add error handling and retry logic in utils.py

**Issue**: Large datasets cause slowness
- **Solution**: Implement pagination or data filtering

## Dependencies

### Core Dependencies

- `streamlit>=1.28.0` - Web framework
- `requests` - HTTP client for API calls
- `json` - Data parsing (built-in)
- `pprint` - Pretty printing (built-in)

### Optional Dependencies

For future enhancements:
- `pandas` - Data manipulation
- `plotly` - Advanced visualizations
- `python-dotenv` - Environment variable management

Add to `requirements.txt` as needed.

## Testing

Consider adding tests for:
- `extract_match_summary()` function
- API error handling
- Data validation

Example test structure:

```bash
mkdir tests
touch tests/__init__.py
touch tests/test_utils.py
```

## Deployment Checklist

Before deploying:

- [ ] All dependencies listed in `requirements.txt`
- [ ] `.env` file created (not committed)
- [ ] Config files (`config.json`, `bios.json`) populated
- [ ] Tested with mock data
- [ ] Tested with live API
- [ ] Error handling covers edge cases
- [ ] Documentation updated
- [ ] Git commit history clean

## Resources

- Streamlit Docs: https://docs.streamlit.io
- FPL API: https://fantasy.premierleague.com/api/
- Python Best Practices: https://pep8.org/
- Git Guide: https://git-scm.com/doc

## Questions or Issues?

1. Check existing code comments
2. Review this guide
3. Test with mock data first
4. Check Streamlit/FPL documentation
5. Review git history for similar solutions
