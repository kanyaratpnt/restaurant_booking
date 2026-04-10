import flet as ft
import requests

API_URL = "http://192.168.1.41:8000"

def show_otp(page: ft.Page, phone: str, on_success):
    page.clean()
    page.title = "กรอกรหัส OTP"

    otp_input  = ft.Ref[ft.TextField]()
    error_text = ft.Text("", color="red600", size=13)
    countdown  = ft.Text("รหัสหมดอายุใน 5:00", size=12, color="grey500")

    def on_verify(e):
        code = otp_input.current.value.strip()
        if len(code) != 6:
            error_text.value = "กรุณากรอก OTP 6 หลัก"
            page.update()
            return
        try:
            res = requests.post(
                f"{API_URL}/auth/verify-otp",
                json={"phone": phone, "otp_code": code}
            )
            if res.status_code == 200:
                data = res.json()
                on_success(page, data)   # ส่ง customer info ไปหน้าถัดไป
            else:
                error_text.value = res.json().get("detail", "OTP ไม่ถูกต้อง")
                page.update()
        except Exception as ex:
            error_text.value = f"Error: {ex}"
            page.update()

    def on_resend(e):
        requests.post(f"{API_URL}/auth/send-otp", json={"phone": phone})
        error_text.value = ""
        countdown.value = "ส่ง OTP ใหม่แล้ว"
        page.update()

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Container(height=80),
                ft.Icon(ft.Icons.LOCK_OUTLINE, size=48, color="deepyellow400"),
                ft.Container(height=12),
                ft.Text("กรอกรหัส OTP", size=24, weight="bold", color="deepyellow700"),
                ft.Text(f"ส่ง SMS ไปที่ {phone}", size=13, color="grey600"),
                ft.Container(height=32),

                ft.TextField(
                    ref=otp_input,
                    label="รหัส 6 หลัก",
                    keyboard_type=ft.KeyboardType.NUMBER,
                    max_length=6,
                    text_align=ft.TextAlign.CENTER,
                    width=220,
                    border_radius=12,
                    border_color="deepyellow200",
                    focused_border_color="deepyellow500",
                    text_style=ft.TextStyle(size=28, weight="bold", letter_spacing=8),
                ),
                ft.Container(height=8),
                countdown,
                error_text,
                ft.Container(height=12),

                ft.FilledButton(
                    "ยืนยัน OTP",
                    width=220, height=48,
                    on_click=on_verify,
                    style=ft.ButtonStyle(
                        bgcolor="#2A2403", color="white",
                        shape=ft.RoundedRectangleBorder(radius=12)
                    ),
                ),
                ft.Container(height=12),
                ft.TextButton("ส่งรหัสใหม่", on_click=on_resend),
                ft.TextButton(
                    "← กลับ",
                    on_click=lambda _: __import__('login').show_login(page, on_success)
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=30, expand=True,
        )
    )
    page.update()