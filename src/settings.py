import flet as ft
from vars import APP_VARS

def create_settings_content(page: ft.Page):
    update_rate_field = ft.TextField(
        label="Update Rate (Hz)", 
        value=str(APP_VARS.update_rate_hz), 
        keyboard_type=ft.KeyboardType.NUMBER
    )

    url_field = ft.TextField(
        label="URL", 
        value=APP_VARS.url
    )

    debug_checkbox = ft.Checkbox(
        label="Debug Mode", 
        value=APP_VARS.debug
    )

    def save_settings(e):
        try:
            # get new rate
            new_rate = float(update_rate_field.value)
            if new_rate <= 0:
                raise ValueError("Update rate must be positive")
            # set new rate
            APP_VARS.update_rate_hz = new_rate
        except ValueError:
            update_rate_field.error_text = "Enter a valid positive number"
            page.update()
            return

        # set url
        APP_VARS.url = url_field.value.strip()
        # set debug
        APP_VARS.toggleDebug(debug_checkbox.value)
        # update the UI
        page.update()

    return ft.Column([
            ft.Text(
                "Settings", 
                size=24, 
                weight=ft.FontWeight.BOLD, 
                text_align=ft.TextAlign.CENTER
            ),

            update_rate_field,
            url_field,
            debug_checkbox,
            ft.ElevatedButton(
                "Save Settings", 
                on_click=save_settings
            )
        ], 
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
        spacing=20
    )