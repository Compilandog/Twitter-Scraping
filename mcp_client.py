import json
import uuid
import requests
import time

MCP_URL = "http://localhost:8123/mcp"


def run_playwright_flow(user_handle, n=10):
    """Retorna n tweets mais recentes do perfil usando fluxograma MCP."""
    flow = {
        "id": str(uuid.uuid4()),
        "steps": [
            {"action": "open", "url": f"https://x.com/{user_handle}"},
            {"action": "wait", "seconds": 5},
            {"action": "scroll", "direction": "down", "pixels": 4000},
            {"action": "extract", "selector": "article div[lang]", "limit": n},
        ],
    }
    resp = requests.post(MCP_URL, json=flow, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    return [t["text"] for t in data["steps"][-1]["result"]]

