import flet as ft
import re
import requests
from datetime import date, datetime

API_URL = "http://192.168.1.41:8000"


CREAM       = "#F7F1E8"
WARM_WHITE  = "#FDFAF5"
SAND        = "#EDE3D4"
SAND_MID    = "#D4C0A4"
SAND_DARK   = "#BFA882"

CLAY        = "#C0924A"   # gold-clay  (primary accent)
CLAY_DARK   = "#8F6420"   # deep gold
CLAY_PALE   = "#C0924A14"

ESPRESSO    = "#3A1F08"   # near-black warm
MAHOGANY    = "#6B2D0F"   # deep red-brown
BROWN_MID   = "#7A4F28"
BROWN_LIGHT = "#A07040"

RUST        = "#B85030"   # terracotta
RUST_PALE   = "#B8503018"

BLUSH       = "#C06050"   # warm rose-brown
BLUSH_PALE  = "#C0605018"

AMBER       = "#C8820A"   # warm amber
AMBER_PALE  = "#C8820A18"

TEXT_PRI    = "#2C1608"
TEXT_SEC    = "#7A5430"
TEXT_DIM    = "#B89870"

BROWN_MID_PALE = "#7A4F2818"   
MAHOGANY_PALE  = "#6B2D0F18"

MIN_HOUR = 11
MAX_HOUR = 22


OCCASIONS = [
    {"value": "birthday",    "label": "ฉลองวันเกิด", "icon": ft.Icons.CAKE_OUTLINED,            "color": BLUSH,     "bg": BLUSH_PALE      },
    {"value": "anniversary", "label": "วันครบรอบ",   "icon": ft.Icons.FAVORITE_BORDER_ROUNDED,  "color": RUST,      "bg": RUST_PALE       },
    {"value": "business",    "label": "นัดธุรกิจ",   "icon": ft.Icons.BUSINESS_CENTER_OUTLINED, "color": BROWN_MID, "bg": BROWN_MID_PALE  },
    {"value": "first_date",  "label": "เดทแรก",      "icon": ft.Icons.LOCAL_FLORIST_OUTLINED,   "color": MAHOGANY,  "bg": MAHOGANY_PALE   },
    {"value": "general",     "label": "ทั่วไป",       "icon": ft.Icons.RESTAURANT_OUTLINED,      "color": AMBER,     "bg": AMBER_PALE      },
]


def show_occasion_screen(page: ft.Page, table_num, back_func):
    page.clean()
    page.title = "Special Requests"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = CREAM

    note_input        = ft.Ref[ft.TextField]()
    phone_input       = ft.Ref[ft.TextField]()
    guest_count_ref   = ft.Ref[ft.Text]()
    guest_warning_ref = ft.Ref[ft.Text]()
    hour_display_ref  = ft.Ref[ft.Text]()
    hour_warning_ref  = ft.Ref[ft.Text]()
    date_display_ref  = ft.Ref[ft.Text]()

    booking_date = getattr(page, 'booking_date', date.today().strftime("%Y-%m-%d"))
    raw_time     = getattr(page, 'booking_time', getattr(page, 'filter_time', "18:00"))
    try:
        current_hour = int(raw_time.split(":")[0])
    except Exception:
        current_hour = 18
    current_hour = max(MIN_HOUR, min(MAX_HOUR, current_hour))

    table_capacity = 4
    try:
        res = requests.get(f"{API_URL}/tables", timeout=3)
        if res.status_code == 200:
            for t in res.json():
                if str(t.get("table_number", "")).strip() == str(table_num).strip():
                    table_capacity = t.get("capacity", 4)
                    break
    except Exception:
        pass

    guest_state    = {"count": min(getattr(page, 'filter_guest', 2), table_capacity)}
    occasion_state = {"value": "general"}

    # ── Sub dropdowns ──
    cake_dropdown = ft.Dropdown(
        label="รับเค้กอะไรดีคะ?",
        label_style=ft.TextStyle(size=12, color=CLAY),
        hint_text="เลือกเค้กที่ชอบ...",
        height=44, text_size=13,
        border_radius=10,
        border_color=SAND_MID,
        focused_border_color=CLAY_DARK,
        bgcolor=WARM_WHITE,
        options=[
            ft.dropdown.Option("Chocolate Fondant"),
            ft.dropdown.Option("Sweet Strawberry"),
            ft.dropdown.Option("Creamy Cheesecake"),
            ft.dropdown.Option("ป้าย HBD"),
            ft.dropdown.Option("ไม่ต้องการเค้ก"),
        ],
    )
    def on_cake_selected(e):
        if e.control.value:
            cur = note_input.current.value or ""
            cur = re.sub(r"\[เค้ก:.*?\] ", "", cur)
            note_input.current.value = f"[เค้ก: {e.control.value}] " + cur
            page.update()
    cake_dropdown.on_change = on_cake_selected
    cake_container = ft.Container(content=cake_dropdown, padding=ft.Padding(4, 4, 0, 0), visible=False, height=0)

    anni_dropdown = ft.Dropdown(
        label="การตกแต่งโต๊ะพิเศษ",
        label_style=ft.TextStyle(size=12, color=CLAY),
        hint_text="เลือกรูปแบบ...",
        height=44, text_size=13,
        border_radius=10,
        border_color=SAND_MID,
        focused_border_color=CLAY_DARK,
        bgcolor=WARM_WHITE,
        options=[
            ft.dropdown.Option("โรยกลีบกุหลาบบนโต๊ะ"),
            ft.dropdown.Option("จัดช่อดอกไม้สด"),
            ft.dropdown.Option("ชุดเทียนหอมอโรม่า"),
        ],
    )
    def on_anni_selected(e):
        if e.control.value:
            cur = note_input.current.value or ""
            cur = re.sub(r"\[ตกแต่ง:.*?\] ", "", cur)
            note_input.current.value = f"[ตกแต่ง: {e.control.value}] " + cur
            page.update()
    anni_dropdown.on_change = on_anni_selected
    anni_container = ft.Container(content=anni_dropdown, padding=ft.Padding(4, 4, 0, 0), visible=False, height=0)

    # ── Occasion tiles ──
    occasion_col = ft.Column(spacing=8)

    def build_occasion_tile(occ, is_sel):
        color  = occ["color"]
        sel_bg = occ["bg"] 
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Container(
                        content=ft.Icon(occ["icon"], size=17,
                                        color=color if is_sel else BROWN_LIGHT),
                        width=34, height=34,
                        bgcolor=occ["bg"] if is_sel else SAND,
                        border_radius=9,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Text(occ["label"], size=13,
                            weight="bold" if is_sel else "normal",
                            color=ESPRESSO if is_sel else TEXT_SEC,
                            expand=True),
                    # Checkmark: filled circle when selected, empty ring otherwise
                    ft.Container(
                        width=20, height=20, border_radius=10,
                        bgcolor=color if is_sel else "transparent",
                        border=ft.Border.all(2, color if is_sel else SAND_MID),
                        content=ft.Icon(ft.Icons.CHECK_ROUNDED, size=12, color=WARM_WHITE) if is_sel else ft.Container(),
                        alignment=ft.Alignment(0, 0),
                    ),
                ], spacing=10),
                *(
                    [cake_container]
                    if (is_sel and occ["value"] == "birthday")
                    else [anni_container]
                    if (is_sel and occ["value"] == "anniversary")
                    else []
                ),
            ], spacing=6),
            bgcolor=WARM_WHITE,
            border_radius=14,
            padding=ft.Padding(14, 11, 14, 11),
            border=ft.Border.all(1.5 if is_sel else 1, color if is_sel else SAND_MID),
            on_click=lambda e, v=occ["value"]: on_occasion_tap(v),
            shadow=ft.BoxShadow(
                blur_radius=4 if is_sel else 1,
                color=ESPRESSO + "0A",
                offset=ft.Offset(0, 1),
            ),
        )

    def render_occasions():
        for occ in OCCASIONS:
            is_sel = occasion_state["value"] == occ["value"]
            if not is_sel:
                if occ["value"] == "birthday":
                    cake_container.visible = False; cake_container.height = 0
                elif occ["value"] == "anniversary":
                    anni_container.visible = False; anni_container.height = 0
            else:
                if occ["value"] == "birthday":
                    cake_container.visible = True; cake_container.height = 58
                elif occ["value"] == "anniversary":
                    anni_container.visible = True; anni_container.height = 58
        occasion_col.controls = [build_occasion_tile(o, occasion_state["value"] == o["value"]) for o in OCCASIONS]

    def on_occasion_tap(value):
        prev = occasion_state["value"]
        occasion_state["value"] = value
        if prev == "birthday" and value != "birthday":
            cur = note_input.current.value or ""
            note_input.current.value = re.sub(r"\[เค้ก:.*?\] ", "", cur)
        if prev == "anniversary" and value != "anniversary":
            cur = note_input.current.value or ""
            note_input.current.value = re.sub(r"\[ตกแต่ง:.*?\] ", "", cur)
        render_occasions()
        page.update()

    render_occasions()

    # ── Date picker ──
    def pick_date(e):
        def on_date_change(ev):
            nonlocal booking_date
            d = ev.control.value
            if d:
                if isinstance(d, datetime): d = d.date()
                booking_date = d.strftime("%Y-%m-%d")
                page.booking_date = booking_date
                date_display_ref.current.value = booking_date
                date_display_ref.current.color = ESPRESSO
                page.update()
        dp = ft.DatePicker(first_date=datetime.now(), last_date=datetime(2026, 12, 31), on_change=on_date_change)
        page.overlay.append(dp)
        page.update()
        dp.open = True
        page.update()

    # ── Time stepper ──
    def update_hour_display():
        hour_display_ref.current.value = f"{current_hour:02d}:00"
        page.booking_time = f"{current_hour:02d}:00"
        if hour_warning_ref.current: hour_warning_ref.current.visible = False
        page.update()

    def change_hour(delta):
        nonlocal current_hour
        new_h = current_hour + delta
        if new_h < MIN_HOUR:
            if hour_warning_ref.current:
                hour_warning_ref.current.value = "เปิด 11:00 น."
                hour_warning_ref.current.visible = True
                page.update()
            return
        if new_h > MAX_HOUR:
            if hour_warning_ref.current:
                hour_warning_ref.current.value = "ปิด 22:00 น."
                hour_warning_ref.current.visible = True
                page.update()
            return
        if hour_warning_ref.current: hour_warning_ref.current.visible = False
        current_hour = new_h
        update_hour_display()

    # ── Guest stepper ──
    def update_guest_display():
        if guest_count_ref.current: guest_count_ref.current.value = str(guest_state["count"])
        if guest_warning_ref.current: guest_warning_ref.current.visible = False
        page.update()

    def change_guest(delta):
        new_val = guest_state["count"] + delta
        if new_val < 1: return
        if new_val > table_capacity:
            if guest_warning_ref.current:
                guest_warning_ref.current.value = f"สูงสุด {table_capacity} ท่าน"
                guest_warning_ref.current.visible = True
                page.update()
            return
        guest_state["count"] = new_val
        update_guest_display()

    # ── Reusable stepper components ──
    def step_btn(icon, fn):
        return ft.Container(
            content=ft.Icon(icon, color=WARM_WHITE, size=14),
            width=32, height=32, bgcolor=CLAY,
            border_radius=16, alignment=ft.Alignment(0, 0),
            on_click=fn,
            shadow=ft.BoxShadow(blur_radius=4, color=CLAY_DARK + "40"),
        )

    def step_display(ref_obj, val, sub=None):
        kids = [ft.Text(ref=ref_obj, value=val, size=18, weight="bold",
                        color=ESPRESSO, text_align=ft.TextAlign.CENTER,
                        no_wrap=True, overflow=ft.TextOverflow.CLIP)]
        if sub:
            kids.append(ft.Text(sub, size=8, color=TEXT_DIM, text_align=ft.TextAlign.CENTER))
        return ft.Container(
            content=ft.Column(kids, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, tight=True),
            width=70,          # fixed narrow width — prevents wrapping
            bgcolor=SAND, border_radius=10,
            padding=ft.Padding(4, 7, 4, 7),
            border=ft.Border.all(1.5, SAND_MID),
            alignment=ft.Alignment(0, 0),
        )

    def step_card(title_icon, title, row_widget, warn_ref):
        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(title_icon, size=11, color=CLAY),
                    ft.Text(title, size=10, weight="w600", color=BROWN_MID),
                ], spacing=3),
                ft.Container(height=5),
                row_widget,
                ft.Text(ref=warn_ref, value="", size=9, color=RUST,
                        visible=False, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=WARM_WHITE, border_radius=14,
            padding=ft.Padding(10, 10, 10, 10),
            border=ft.Border.all(1, SAND_MID),
            expand=True,
        )

    guest_row = ft.Row([
        step_btn(ft.Icons.REMOVE_ROUNDED, lambda e: change_guest(-1)),
        step_display(guest_count_ref, str(guest_state["count"]), f"max {table_capacity}"),
        step_btn(ft.Icons.ADD_ROUNDED,   lambda e: change_guest(1)),
    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER)

    time_row = ft.Row([
        step_btn(ft.Icons.REMOVE_ROUNDED, lambda e: change_hour(-1)),
        step_display(hour_display_ref, f"{current_hour:02d}:00", "น."),
        step_btn(ft.Icons.ADD_ROUNDED,   lambda e: change_hour(1)),
    ], spacing=6, alignment=ft.MainAxisAlignment.CENTER)

    guest_time_row = ft.Row([
        step_card(ft.Icons.GROUP_OUTLINED,      "จำนวนคน", guest_row, guest_warning_ref),
        ft.Container(width=10),
        step_card(ft.Icons.ACCESS_TIME_ROUNDED, "เวลา",    time_row,  hour_warning_ref),
    ], spacing=0)

    # ── Section label ──
    def section_label(text, icon):
        return ft.Row([
            ft.Container(width=3, height=14, bgcolor=CLAY, border_radius=2),
            ft.Icon(icon, size=14, color=CLAY),
            ft.Text(text, size=13, weight="bold", color=ESPRESSO),
        ], spacing=6)

    # ── Submit ──
    def go_to_summary(e):
        user_info   = getattr(page, 'user_info', {}) or {}
        customer_id = user_info.get("customer_id", 0)
        notes       = note_input.current.value or ""
        occ_val     = occasion_state["value"]
        if occ_val == "birthday" and "[เค้ก:" not in notes and cake_dropdown.value:
            notes = f"[เค้ก: {cake_dropdown.value}] " + notes
        if occ_val == "anniversary" and "[ตกแต่ง:" not in notes and anni_dropdown.value:
            notes = f"[ตกแต่ง: {anni_dropdown.value}] " + notes
        if guest_state["count"] > table_capacity:
            if guest_warning_ref.current:
                guest_warning_ref.current.value = f"สูงสุด {table_capacity} ท่าน"
                guest_warning_ref.current.visible = True
                page.update()
            return
        booking_data = {
            "customer_id":      customer_id,
            "table_number":     table_num,
            "occasion":         occ_val,
            "special_requests": notes,
            "reservation_date": getattr(page, 'booking_date', booking_date),
            "reservation_time": getattr(page, 'booking_time', f"{current_hour:02d}:00"),
            "guest_count":      guest_state["count"],
            "phone":            phone_input.current.value or "",
            "zone":             getattr(page, 'filter_zone', 'indoor'),
        }
        from reservation_summary import show_reservation_summary
        show_reservation_summary(page, booking_data,
            back_func=lambda p: show_occasion_screen(p, table_num, back_func))

    # ── Header ──
    header_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.ARROW_BACK_IOS_NEW_ROUNDED, color=ESPRESSO, size=16),
                    width=38, height=38, bgcolor=SAND, border_radius=19,
                    alignment=ft.Alignment(0, 0),
                    on_click=lambda _: back_func(page),
                    border=ft.Border.all(1, SAND_MID),
                ),
                ft.Container(
                    content=ft.Text("รายละเอียดการจอง", size=17, weight="bold", color=ESPRESSO),
                    alignment=ft.Alignment(0, 0), expand=True,
                ),
                ft.Container(width=38),
            ]),
            ft.Container(
                height=1, margin=ft.Margin(0, 8, 0, 0),
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                    colors=["transparent", SAND_MID, "transparent"],
                ),
            ),
        ]),
        padding=ft.Padding(16, 48, 16, 0),
        bgcolor=CREAM,
    )

    table_info_row = ft.Container(
        content=ft.Row([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.TABLE_RESTAURANT_OUTLINED, size=14, color=CLAY_DARK),
                    ft.Text(f"โต๊ะ {table_num}", size=14, weight="bold", color=ESPRESSO),
                ], spacing=6),
                bgcolor=SAND, padding=ft.Padding(14, 7, 14, 7),
                border_radius=20, border=ft.Border.all(1, SAND_MID),
            ),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.GROUP_OUTLINED, size=13, color=SAND_MID),
                    ft.Text(f"สูงสุด {table_capacity} ท่าน", size=12, color=SAND_MID, weight="w500"),
                ], spacing=4),
                bgcolor=TEXT_SEC, padding=ft.Padding(12, 6, 12, 6),
                border_radius=20, border=ft.Border.all(1, SAND_DARK),
            ),
        ], spacing=8),
        padding=ft.Padding(20, 14, 20, 0),
    )

    content_section = ft.Container(
        content=ft.Column([
            # โอกาสพิเศษ
            section_label("โอกาสพิเศษ", ft.Icons.CELEBRATION_OUTLINED),
            occasion_col,
            ft.Container(height=2),
            # วันที่ (ก่อนเวลา)
            section_label("วันที่จอง", ft.Icons.CALENDAR_TODAY_OUTLINED),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.CALENDAR_MONTH_OUTLINED, color=CLAY, size=15),
                    ft.Text(ref=date_display_ref, value=booking_date, size=14, weight="bold", color=ESPRESSO),
                    ft.Container(expand=True),
                    ft.Icon(ft.Icons.EDIT_CALENDAR_OUTLINED, color=TEXT_DIM, size=13),
                ], spacing=8),
                on_click=pick_date, bgcolor=WARM_WHITE,
                padding=ft.Padding(16, 13, 16, 13), border_radius=12,
                border=ft.Border.all(1.5, SAND_MID),
            ),
            # จำนวนคน & เวลา (หลังวันที่)
            section_label("จำนวนคน & เวลา", ft.Icons.TUNE_ROUNDED),
            guest_time_row,
            # โน้ต
            section_label("โน้ตพิเศษ", ft.Icons.EDIT_NOTE_ROUNDED),
            ft.TextField(
                ref=note_input,
                hint_text="ความต้องการเพิ่มเติม เช่น จัดดอกไม้, แพ้อาหาร...",
                hint_style=ft.TextStyle(size=12, color=TEXT_DIM),
                text_style=ft.TextStyle(size=13, color=TEXT_PRI),
                multiline=True, min_lines=2, border_radius=12,
                border_color=SAND_MID, focused_border_color=CLAY_DARK,
                cursor_color=ESPRESSO, bgcolor=WARM_WHITE, filled=True, fill_color=WARM_WHITE,
                expand=True,
            ),
            # เบอร์โทร
            section_label("เบอร์โทรศัพท์", ft.Icons.PHONE_OUTLINED),
            ft.TextField(
                ref=phone_input,
                hint_text="เช่น 0812345678",
                hint_style=ft.TextStyle(size=12, color=TEXT_DIM),
                text_style=ft.TextStyle(size=13, color=TEXT_PRI),
                keyboard_type=ft.KeyboardType.PHONE,
                border_radius=12, border_color=SAND_MID,
                focused_border_color=CLAY_DARK, cursor_color=ESPRESSO,
                bgcolor=WARM_WHITE, filled=True, fill_color=WARM_WHITE,
                expand=True,
            ),
            # Submit
            ft.Container(
                content=ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.RECEIPT_LONG_OUTLINED, color=WARM_WHITE, size=17),
                        ft.Container(width=6),
                        ft.Text("สรุปรายละเอียดการจอง", size=14, weight="bold", color=WARM_WHITE),
                        ft.Container(width=4),
                        ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color=WARM_WHITE, size=14),
                    ], alignment=ft.MainAxisAlignment.CENTER),
                    on_click=go_to_summary,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                        colors=[ESPRESSO, CLAY_DARK],
                    ),
                    border_radius=14,
                    padding=ft.Padding(0, 15, 0, 15),
                    shadow=ft.BoxShadow(blur_radius=14, color=ESPRESSO + "45", offset=ft.Offset(0, 4)),
                ),
                alignment=ft.Alignment(0, 0),
                padding=ft.Padding(0, 8, 0, 0),
            ),
        ], scroll=ft.ScrollMode.ADAPTIVE, spacing=10),
        padding=ft.Padding(20, 14, 20, 30),
    )

    page.add(header_section, table_info_row, ft.Container(content=content_section, expand=True))
    page.update()