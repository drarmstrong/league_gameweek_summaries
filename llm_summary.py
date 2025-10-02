import requests

def query_ollama(prompt: str, model: str = "llama3"):
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    response.raise_for_status()
    return response.json()["response"]

def save_output(text: str, filename: str = "gameweek_summary.md"):
    with open(filename, "w") as f:
        f.write(text)