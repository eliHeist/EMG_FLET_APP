import requests, random
from settings import APP_VARS


async def fetch_emg_value():
    if APP_VARS.debug:
        return random.uniform(3300, 4020)
    try:
        response = requests.get(APP_VARS.url, timeout=5)
        response.raise_for_status()
        return float(response.text.strip())
    except Exception:
        return None

# async def test_connection():
#     try:
#         response = requests.get(TESTING_ENDPOINT, timeout=5)
#         response.raise_for_status()
#         DEBUG = True
#     except Exception:
#         DEBUG = False
