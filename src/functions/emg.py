import requests, random
from settings import DEBUG, DATA_ENDPOINT, TESTING_ENDPOINT, toggleDebug


async def fetch_emg_value():
    if DEBUG:
        return random.uniform(2000, 4020)
    try:
        response = requests.get(DATA_ENDPOINT, timeout=5)
        response.raise_for_status()
        return float(response.text.strip())
    except Exception:
        return None

async def test_connection():
    try:
        response = requests.get(TESTING_ENDPOINT, timeout=5)
        response.raise_for_status()
        return toggleDebug(True)
    except Exception:
        return toggleDebug(False)
