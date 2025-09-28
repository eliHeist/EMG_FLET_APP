import flet as ft
import matplotlib.pyplot as plt
import asyncio, random, requests
import base64
import time

from io import BytesIO
from settings import create_settings_content
from vars import APP_VARS, SetInterval

active_stream = []

time_stamps = []

# --- EMG Fetch ---
async def getEMGValue():
    if APP_VARS.debug:
        value = random.randint(0, 4050)
    else:
        try:
            response = requests.get(APP_VARS.url)
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
    ax.set_ylim(0, 4200)
    fig.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    img_bytes = buf.read()
    return base64.b64encode(img_bytes).decode()

# --- Flet UI ---
async def main(page: ft.Page):
    page.title = "EMG Streamer"
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- Main Page Components ---
    header = ft.Text("LIVE EMG DATA", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)
    chart_image = ft.Image(src="assets/chart.png", height=500, width=600)
    
    # Traffic light radio buttons
    critical_radio = ft.Radio(value="critical", label="Critical", fill_color=ft.Colors.RED)
    normal_radio = ft.Radio(value="normal", label="Normal", fill_color=ft.Colors.TEAL)
    low_radio = ft.Radio(value="low", label="Low", fill_color=ft.Colors.YELLOW_800)
    radio_group = ft.RadioGroup(
        value="none",
        content=ft.Column([
            critical_radio,
            normal_radio,
            low_radio
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
    )

    main_content = ft.Column([
        header,
        chart_image,
        radio_group
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True, spacing=20)

    # --- Settings Page Components ---
    settings_content = create_settings_content(page)

    # --- Navigation ---
    content_container = ft.Container(content=main_content, expand=True)

    def update_ui():
        if active_stream and APP_VARS.running:
            chart_image.src_base64 = render_chart()

            last_val = active_stream[-1] if len(active_stream) >= 1 else 0
            
            if last_val > APP_VARS.HIGH_THRESHOLD:
                radio_group.value = "critical"
            elif last_val < APP_VARS.LOW_THRESHOLD:
                radio_group.value = "low"
            else:
                radio_group.value = "normal"
            page.update()

            current_time_stamp = time.time()
            time_stamps.append(current_time_stamp)
            if len(time_stamps) >= 2:
                delay = time_stamps[-1] - time_stamps[-2]
                print(f"The delay was {delay:.3f} seconds")
            

    async def refresh_loop():
        while True:
            update_ui()
            await asyncio.sleep(1 / APP_VARS.update_rate_hz)

    def start_stream(_):
        active_stream.clear()
        APP_VARS.interval = SetInterval(getEMGValue, 1 / APP_VARS.update_rate_hz)
        APP_VARS.interval.start(page)
        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.STOP, on_click=stop_stream, bgcolor=ft.Colors.RED_500
        )
        page.update()
        APP_VARS.running = True

    def stop_stream(_):
        if APP_VARS.interval:
            APP_VARS.interval.stop()
        radio_group.value = "none"
        page.floating_action_button = ft.FloatingActionButton(
            icon=ft.Icons.PLAY_ARROW, on_click=start_stream, bgcolor=ft.Colors.TEAL_500
        )
        page.update()
        APP_VARS.running = False

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.PLAY_ARROW, on_click=start_stream, bgcolor=ft.Colors.TEAL_500
    )

    def change_page(e):
        if e.control.selected_index == 0:
            content_container.content = main_content
            page.floating_action_button = ft.FloatingActionButton(
                icon=ft.Icons.PLAY_ARROW if not APP_VARS.interval or APP_VARS.interval._stop_event.is_set() else ft.Icons.STOP,

                on_click=start_stream if not APP_VARS.interval or APP_VARS.interval._stop_event.is_set() else stop_stream,

                bgcolor=ft.Colors.TEAL_500 if not APP_VARS.interval or APP_VARS.interval._stop_event.is_set() else ft.Colors.RED_500
            )
        else:
            content_container.content = settings_content
            page.floating_action_button = None
        page.update()

    nav_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationBarDestination(icon=ft.Icons.SHOW_CHART, label="EMG Streamer"),
            ft.NavigationBarDestination(icon=ft.Icons.SETTINGS, label="Settings")
        ],
        on_change=change_page
    )

    page.add(
        ft.Column([
            content_container,
            nav_bar
        ], expand=True)
    )

    # Start the refresh loop
    page.run_task(refresh_loop)

ft.app(target=main)