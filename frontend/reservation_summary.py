import flet as ft
import requests
from datetime import datetime

API_URL = "http://192.168.1.41:8000"

# ── Earth Tone Palette (ตรงกับ occasion.py) ──
CREAM      = "#FAF6F1"
WARM_WHITE = "#FDF9F5"
SAND       = "#E8DDD0"
SAND_MID   = "#D4C4B0"
CLAY       = "#B8956A"
CLAY_DARK  = "#8B6B47"
SOIL       = "#5C3D2E"
RUST       = "#C0614B"
GREEN_OK   = "#5C8B3E"
TEXT_PRI   = "#3C2A1E"
TEXT_SEC   = "#8A7060"
TEXT_DIM   = "#B8A898"

# Zone label mapping — "all" แสดงชื่อตามที่เลือกจริง
ZONE_LABELS = {
    "seaview": "ริมทะเล (Seaview)",
    "indoor":  "ในร่ม (Indoor)",
    "outdoor": "กลางแจ้ง (Outdoor)",
    "private": "ห้องส่วนตัว (Private)",
    "all":     "ทุกโซน",
}

OCCASION_LABELS = {
    "birthday":    "วันเกิด",
    "anniversary": "วันครบรอบ",
    "business":    "นัดธุรกิจ",
    "first_date":  "เดทแรก",
    "general":     "ทั่วไป",
}

OCCASION_ICONS = {
    "birthday":    ft.Icons.CAKE_OUTLINED,
    "anniversary": ft.Icons.FAVORITE_BORDER_ROUNDED,
    "business":    ft.Icons.BUSINESS_CENTER_OUTLINED,
    "first_date":  ft.Icons.LOCAL_FLORIST_OUTLINED,
    "general":     ft.Icons.RESTAURANT_OUTLINED,
}


def show_reservation_summary(page: ft.Page, booking_data: dict, back_func=None):
    page.clean()
    page.title  = "สรุปการจอง"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = CREAM

    # ── ดึงข้อมูลจาก booking_data ──
    table_num    = booking_data.get("table_number", "-")
    zone_key     = booking_data.get("zone", "indoor")
    zone_label   = ZONE_LABELS.get(zone_key, zone_key)
    res_date     = booking_data.get("reservation_date", "-")
    res_time     = booking_data.get("reservation_time", "-")
    guest_count  = booking_data.get("guest_count", 2)
    occasion_key = booking_data.get("occasion", "general") or "general"
    occasion_str = OCCASION_LABELS.get(occasion_key, "ทั่วไป")
    occasion_icon = OCCASION_ICONS.get(occasion_key, ft.Icons.RESTAURANT_OUTLINED)
    phone_val    = booking_data.get("phone", "")
    notes        = booking_data.get("special_requests", "") or ""

    # แปลงวันที่ให้อ่านง่าย
    try:
        dt_obj    = datetime.strptime(res_date, "%Y-%m-%d")
        date_disp = dt_obj.strftime("%A, %d %B %Y")
    except Exception:
        date_disp = res_date

    def rgba(hex6, opacity):
        return ft.Colors.with_opacity(opacity, hex6)

    # ── Submit ──
    submit_loading = ft.Ref[ft.Container]()
    submit_btn_ref = ft.Ref[ft.Container]()
    result_ref     = ft.Ref[ft.Text]()

    def do_confirm(e):
        if submit_btn_ref.current:
            submit_btn_ref.current.visible = False
        if submit_loading.current:
            submit_loading.current.visible = True
        page.update()

        try:
            res = requests.post(
                f"{API_URL}/reservations",
                json=booking_data,
                timeout=8,
            )
            if res.status_code == 200:
                show_success()
            else:
                detail = ""
                try:
                    detail = res.json().get("detail", "")
                except Exception:
                    pass
                show_error(detail or f"Error {res.status_code}")
        except Exception as ex:
            show_error(f"ไม่สามารถเชื่อมต่อ server: {ex}")

    def show_success():
        page.clean()
        page.bgcolor = CREAM
        page.add(
            ft.Column([
                ft.Container(expand=True),
                ft.Column([
                    ft.Container(
                        content=ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, size=72, color=GREEN_OK),
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(height=16),
                    ft.Text("จองสำเร็จแล้ว!", size=24, weight="bold",
                            color=SOIL, text_align=ft.TextAlign.CENTER),
                    ft.Text("ร้านจะติดต่อยืนยันอีกครั้ง", size=13,
                            color=TEXT_SEC, text_align=ft.TextAlign.CENTER),
                    ft.Container(height=32),
                    ft.Container(
                        content=ft.Text("กลับหน้าหลัก", size=14, weight="bold", color=WARM_WHITE),
                        bgcolor=SOIL,
                        border_radius=14,
                        padding=ft.Padding(0, 14, 0, 14),
                        width=220,
                        alignment=ft.Alignment(0, 0),
                        on_click=lambda _: go_home(),
                    ),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                ft.Container(expand=True),
            ], expand=True)
        )
        page.update()

    def show_error(msg):
        if submit_loading.current:
            submit_loading.current.visible = False
        if submit_btn_ref.current:
            submit_btn_ref.current.visible = True
        if result_ref.current:
            result_ref.current.value   = msg
            result_ref.current.visible = True
        page.update()

    def go_home():
        from home import show_home
        show_home(page, getattr(page, "user_info", {}))

    # ── Detail row helper ──
    def detail_row(icon, label, value, val_color=TEXT_PRI):
        return ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(icon, size=16, color=CLAY),
                    width=36, height=36,
                    bgcolor=ft.Colors.with_opacity(0.1, CLAY),
                    border_radius=10,
                    alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text(label, size=10, color=TEXT_SEC),
                    ft.Text(str(value) if value else "-", size=14,
                            weight="w600", color=val_color),
                ], spacing=1, tight=True),
            ], spacing=12),
            padding=ft.Padding(0, 6, 0, 6),
        )

    # ── Header ──
    header = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, color=SOIL, size=18),
                    width=40, height=40,
                    bgcolor=SAND,
                    border_radius=20,
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda _: back_func(page) if back_func else go_home(),
                ),
                ft.Container(
                    content=ft.Text("สรุปการจอง", size=18, weight="bold", color=SOIL),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                ),
                ft.Container(width=40),
            ]),
            ft.Container(height=1, bgcolor=SAND_MID, margin=ft.Margin(0, 8, 0, 0)),
        ]),
        padding=ft.Padding(16, 48, 16, 0),
        bgcolor=CREAM,
    )

    # ── Sub-header ──
    sub_header = ft.Container(
        content=ft.Column([
            ft.Container(
                content=ft.Icon(ft.Icons.RESTAURANT_ROUNDED, size=36, color=CLAY),
                width=64, height=64,
                bgcolor=ft.Colors.with_opacity(0.1, CLAY),
                border_radius=32,
                alignment=ft.Alignment(0, 0),
            ),
            ft.Container(height=8),
            ft.Text("รายละเอียดการจองของคุณ", size=16, weight="bold", color=SOIL),
            ft.Text("กรุณาตรวจสอบก่อนยืนยัน", size=12, color=TEXT_SEC),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        padding=ft.Padding(20, 16, 20, 4),
        alignment=ft.Alignment(0, 0),
    )

    # ── Summary card ──
    # Table chip + zone chip
    table_zone_row = ft.Row([
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.TABLE_RESTAURANT_OUTLINED, size=14, color=CLAY_DARK),
                ft.Text(f"# {table_num}", size=15, weight="bold", color=SOIL),
            ], spacing=5),
            bgcolor=SAND,
            padding=ft.Padding(14, 8, 14, 8),
            border_radius=20,
            border=ft.Border.all(1, SAND_MID),
        ),
        ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=13, color=TEXT_SEC),
                ft.Text(zone_label, size=12, color=TEXT_SEC),
            ], spacing=4),
            bgcolor=WARM_WHITE,
            padding=ft.Padding(10, 7, 12, 7),
            border_radius=20,
            border=ft.Border.all(1, SAND_MID),
        ),
    ], spacing=8)

    details_card = ft.Container(
        content=ft.Column([
            table_zone_row,
            ft.Container(height=12),
            ft.Container(
                content=ft.Column([
                    detail_row(ft.Icons.CALENDAR_TODAY_OUTLINED, "วันที่จอง", date_disp),
                    ft.Divider(height=1, color=SAND_MID),
                    detail_row(ft.Icons.ACCESS_TIME_ROUNDED, "เวลา", f"{res_time} น."),
                    ft.Divider(height=1, color=SAND_MID),
                    detail_row(ft.Icons.GROUP_OUTLINED, "จำนวนคน", f"{guest_count} ท่าน"),
                    ft.Divider(height=1, color=SAND_MID),
                    detail_row(occasion_icon, "โอกาสพิเศษ", occasion_str),
                    ft.Divider(height=1, color=SAND_MID),
                    detail_row(ft.Icons.PHONE_OUTLINED, "เบอร์ติดต่อ", phone_val or "-"),
                ], spacing=0),
                bgcolor=WARM_WHITE,
                border_radius=14,
                padding=ft.Padding(16, 8, 16, 8),
                border=ft.Border.all(1, SAND_MID),
            ),
        ], spacing=0),
        padding=ft.Padding(24, 12, 24, 0),
    )

    # ── Notes ──
    notes_section = ft.Container(
        content=ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, size=15, color=CLAY),
                    ft.Text("โน้ตพิเศษ", size=11, color=TEXT_SEC, weight="w600"),
                ], spacing=6),
                ft.Container(height=6),
                ft.Text(notes if notes else "-", size=13, color=TEXT_PRI, no_wrap=False),
            ]),
            bgcolor=ft.Colors.with_opacity(0.06, CLAY),
            padding=ft.Padding(14, 12, 14, 12),
            border_radius=12,
            border=ft.Border.all(1, ft.Colors.with_opacity(0.2, CLAY)),
        ),
        padding=ft.Padding(24, 12, 24, 0),
    )

    # ── Error text ──
    error_text = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ERROR_OUTLINE_ROUNDED, size=14, color=RUST),
            ft.Text(
                ref=result_ref,
                value="",
                size=12,
                color=RUST,
                visible=False,
                expand=True,
                no_wrap=False,
            ),
        ], spacing=6),
        padding=ft.Padding(24, 4, 24, 0),
        visible=True,
    )

    # ── Loading indicator ──
    loading_indicator = ft.Container(
        ref=submit_loading,
        content=ft.Row([
            ft.ProgressRing(width=18, height=18, stroke_width=2, color=SOIL),
            ft.Text("กำลังบันทึก...", size=13, color=TEXT_SEC),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        visible=False,
        padding=ft.Padding(0, 8, 0, 0),
    )

    # ── Confirm button ──
    confirm_button = ft.Container(
        ref=submit_btn_ref,
        content=ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, color=WARM_WHITE, size=20),
                ft.Container(width=8),
                ft.Text("ยืนยันการจอง", size=15, weight="bold", color=WARM_WHITE),
            ], alignment=ft.MainAxisAlignment.CENTER),
            on_click=do_confirm,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=[SOIL, CLAY_DARK],
            ),
            border_radius=16,
            padding=ft.Padding(0, 18, 0, 18),
            shadow=ft.BoxShadow(blur_radius=16, color=ft.Colors.with_opacity(0.3, SOIL)),
            width=300,
        ),
        alignment=ft.Alignment(0, 0),
        padding=ft.Padding(0, 16, 0, 0),
    )

    # ── Back link ──
    back_link = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, size=12, color=TEXT_SEC),
            ft.Text("แก้ไขข้อมูล", size=13, color=TEXT_SEC),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=4),
        padding=ft.Padding(0, 8, 0, 24),
        on_click=lambda _: back_func(page) if back_func else None,
    )

    page.add(
        ft.Column([
            header,
            ft.Container(
                content=ft.Column([
                    sub_header,
                    details_card,
                    notes_section,
                    error_text,
                    loading_indicator,
                    confirm_button,
                    back_link,
                ], spacing=0, scroll=ft.ScrollMode.ADAPTIVE),
                expand=True,
            ),
        ], spacing=0, expand=True)
    )
    page.update()