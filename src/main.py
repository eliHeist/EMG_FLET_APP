import math, io, base64
import threading
import time
import flet as ft
import flet.canvas as cv

import matplotlib.pyplot as plt

from functions.emg import fetch_emg_value
from settings import UPDATE_FREQUENCY


all_values: list[int] = []

streaming = False

def main(page: ft.Page):
    page.title = "EMG Graph Live"
    counter = ft.Text("0", size=50, data=0)

    title = ft.Text("EMG Live Graph", size=20, text_align=ft.TextAlign.CENTER)

    chart_img = ft.Image(width=600, height=400)

    def update_chart(e=None):

        # Get last 30 values for chart
        chart_values = all_values[-30:]

        # Plot
        fig, ax = plt.subplots()
        ax.plot(chart_values, marker="o")
        ax.set_title("Last 30 values")
        ax.set_xlabel("Sample")
        ax.set_ylabel("Value")

        # Save to buffer
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)

        # Convert to base64 string
        chart_img.src_base64 = base64.b64encode(buf.read()).decode("utf-8")
        page.update()
    
    def repeat_task(e=None):
        if streaming:
            print("Running at", UPDATE_FREQUENCY, "Hz")

            # Add new value to full history
            new_val = fetch_emg_value()
            all_values.append(new_val)

    interval = 1/UPDATE_FREQUENCY
    timer = threading.Timer(interval, repeat_task)
    
    def fetchToggle(e=None):
        global streaming
        streaming = not streaming

        if not streaming:
            timer.cancel()
            return
        timer.start()
        

    page.floating_action_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD, on_click=fetchToggle, bgcolor=ft.Colors.LIME_300
    )

    while streaming:
        print("Updating")
        update_chart()
        time.sleep(100)

    page.add(
        ft.SafeArea(
            title,
            chart_img,
        )
    )


ft.app(main)
