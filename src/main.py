import flet as ft
import matplotlib.pyplot as plt
import asyncio, random, threading, time, requests
from io import BytesIO
import base64

# --- Config ---
update_rate_hz = 500
HIGH_THRESHOLD = 3276
LOW_THRESHOLD = 2000
active_stream = []
interval = None
url = "192.168.43.2:8000/data"
debug = True

# --- Interval Thread ---
class SetInterval:
    def __init__(self, func, interval_sec):
        self.func = func
        self.interval = interval_sec
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True

    def _run(self):
        while not self._stop_event.is_set():
            start = time.time()
            asyncio.run(self.func())
            elapsed = time.time() - start
            time.sleep(max(0, self.interval - elapsed))

    def start(self):
        self._stop_event.clear()
        self._thread.start()

    def stop(self):
        self._stop_event.set()
        self._thread.join()

# --- EMG Fetch ---
async def getEMGValue():
    if debug:
        value = random.randint(0, 4050)
    else:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.text  # or response.json() for JSON
                value = float(data)
            else:
                print(f"Failed to fetch: {response.status_code}")
        except Exception as ex:
            print("Failed to fetch")
            print(ex)
            return
    active_stream.append(value)

# --- Chart Renderer ---
def render_chart():
    fig, ax = plt.subplots(figsize=(6, 7))
    ax.plot(active_stream[-100:], color='green')
    # ax.set_title("EMG Signal")
    ax.set_ylim(0, 4200)
    # ax.set_xlabel("Ticks")
    # ax.set_ylabel("Amplitude")
    fig.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()
    return base64.b64encode(img_bytes).decode()

# --- Flet UI ---
def main(page: ft.Page):
    page.title = "EMG Streamer"
    page.theme_mode = ft.ThemeMode.LIGHT

    debug = False

    header = ft.Text("LIVE EMG DATA", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    chart_image = ft.Image(src="assets/chart.png", width=600, height=500, fit=ft.ImageFit.CONTAIN)
    status_text = ft.Text("Status: Idle", size=16)

    def update_ui():
        if active_stream:
            chart_image.src_base64 = render_chart()
            last_val = active_stream[-1]
            if last_val > HIGH_THRESHOLD:
                status_text.value = f"CRITICAL ({last_val})"
                status_text.color = ft.Colors.RED
            elif last_val < LOW_THRESHOLD:
                status_text.value = f"LOW ({last_val})"
                status_text.color = ft.Colors.YELLOW_800
            else:
                status_text.value = f"NORMAL ({last_val})"
                status_text.color = ft.Colors.TEAL
            page.update()

    def start_stream(_):
        global interval
        active_stream.clear()
        interval = SetInterval(getEMGValue, update_rate_hz / 1000)
        interval.start()
        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.STOP, on_click=stop_stream, bgcolor=ft.Colors.RED_500
        )

    def stop_stream(_):
        global interval
        if interval:
            interval.stop()
        status_text.value = "Status: Stream stopped"
        page.update()
        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.PLAY_ARROW, on_click=start_stream, bgcolor=ft.Colors.TEAL_500
        )

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.PLAY_ARROW, on_click=start_stream, bgcolor=ft.Colors.TEAL_500
    )

    page.add(
        ft.Column([
            header,
            chart_image,
            status_text,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    def refresh_loop():
        while True:
            update_ui()
            time.sleep(0.001)

    threading.Thread(target=refresh_loop, daemon=True).start()

ft.app(target=main)
