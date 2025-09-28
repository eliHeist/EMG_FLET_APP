import flet as ft
import asyncio, time



class AppVariables:
    def __init__(self):
        self.update_rate_hz = 500
        self.HIGH_THRESHOLD = 3276
        self.LOW_THRESHOLD = 2000
        self.interval = None
        self.url = "http://192.168.4.1/data"
        self.debug = False
        self.running = False

    def toggleDebug(self, value: bool = None):
        self.debug = value if value is not None else not self.debug
    
    def setUpdateRate(self, rate: float):
        if rate > 0:
            self.update_rate_hz = rate
        else:
            rate = 500
    
    def setURL(self, new_url: str):
        self.url = new_url.strip()
    
    def setThresholds(self, low: float, high: float):
        if low < high:
            self.LOW_THRESHOLD = low
            self.HIGH_THRESHOLD = high


# --- Interval Class ---
class SetInterval:
    def __init__(self, func, interval_sec):
        self.func = func
        self.interval = interval_sec
        self._stop_event = asyncio.Event()

    async def run(self):
        while not self._stop_event.is_set():
            start = time.time()
            await self.func()
            elapsed = time.time() - start
            await asyncio.sleep(max(0, self.interval - elapsed))

    def start(self, page: ft.Page):
        page.run_task(self.run)

    def stop(self):
        self._stop_event.set()


APP_VARS = AppVariables()
