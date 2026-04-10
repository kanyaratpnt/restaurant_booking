import flet as ft
import requests
import math
from occasion import show_occasion_screen

API_URL = "http://192.168.1.41:8000"

# ── Brown palette ──
WHITE       = "#FFFFFF"
BROWN_DARK   = "#4A2C0A"
BROWN_MID    = "#7B4A1E"
BROWN_LIGHT  = "#C8965A"
BROWN_PALE   = "#F5E6D3"
BROWN_CARD   = "#FDF6EE"
BROWN_BORDER = "#D4A574"
ACCENT       = "#E8B86D"


def show_table_detail(page, table_data, on_confirm):
    t_num  = table_data["table_number"]
    status = table_data.get("status", "available")
    zone   = table_data.get("zone", "indoor")
    cap    = table_data.get("capacity", "-")

    status_color = {
        "available": "#27AE60",
        "reserved":  "#C0392B",
        "occupied":  "#E67E22",
    }.get(status, "#7F8C8D")

    status_label = {
        "available": "Available",
        "reserved":  "Reserved",
        "occupied":  "Occupied",
    }.get(status, status)

    zone_icon = {
        "indoor":  ft.Icons.CHAIR,
        "outdoor": ft.Icons.PARK,
        "seaview": ft.Icons.WATER,
        "private": ft.Icons.MEETING_ROOM,
    }.get(zone, ft.Icons.TABLE_RESTAURANT)

    zone_label = {
        "indoor":  "Indoor",
        "outdoor": "Outdoor",
        "seaview": "Seaview",
        "private": "ห้องส่วนตัว",
    }.get(zone, zone)

    def go_occasion(t_num, bs):
        close_sheet(bs)
        show_occasion_screen(page, t_num, lambda p: booktable(p))

    bs = ft.BottomSheet(
        content=ft.Container(
            content=ft.Column([
                ft.Container(
                    width=40, height=4,
                    bgcolor=BROWN_BORDER,
                    border_radius=2,
                ),
                ft.Container(height=12),
                ft.Row([
                    ft.Text(f"โต๊ะ {t_num}", size=22, weight="bold", color=BROWN_DARK),
                    ft.Container(
                        content=ft.Text(status_label, size=12, color=status_color),
                        padding=ft.Padding(10, 4, 10, 4),
                        border_radius=20,
                        border=ft.Border.all(1, status_color),
                        bgcolor=status_color + "15",
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(height=16, color=BROWN_BORDER + "40"),
                ft.Row([
                    ft.Icon(ft.Icons.PEOPLE_OUTLINE, color=BROWN_LIGHT, size=18),
                    ft.Text(f"รองรับได้ {cap} คน", size=14, color=BROWN_MID),
                ], spacing=8),
                ft.Container(height=6),
                ft.Row([
                    ft.Icon(zone_icon, color=BROWN_LIGHT, size=18),
                    ft.Text(zone_label, size=14, color=BROWN_MID),
                ], spacing=8),
                ft.Container(height=20),
                ft.FilledButton(
                    "เลือกโต๊ะนี้",
                    width=300, height=48,
                    disabled=(status != "available"),
                    on_click=lambda _: go_occasion(t_num, bs),
                    style=ft.ButtonStyle(
                        bgcolor=BROWN_DARK if status == "available" else "#AAAAAA",
                        color="white",
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                ),
                ft.Container(height=8),
                ft.TextButton(
                    "ปิด",
                    on_click=lambda _: close_sheet(bs),
                    style=ft.ButtonStyle(color=BROWN_MID),
                ),
                ft.Container(height=8),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
            ),
            padding=ft.Padding(20, 16, 20, 0),
        ),
        open=True,
    )
    page.overlay.append(bs)
    page.update()


def close_sheet(bs):
    bs.open = False
    bs.update()


def booktable(page: ft.Page):
    page.clean()
    page.title = "Restaurant Floor Plan"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = BROWN_CARD

    page.selected_table_num = None
    page.animating_table    = None
    status_text = ft.Text("กรุณาเลือกโต๊ะ", size=16, weight="bold", color=BROWN_DARK)

    # ── Canvas + scroll column ref ──
    floor_plan_canvas  = ft.Stack(expand=True, height=1000)
    scroll_col_ref     = ft.Ref[ft.Column]()
    empty_msg_ref      = ft.Ref[ft.Container]()

    selected_zone = getattr(page, 'filter_zone', 'all')
    guest_count   = getattr(page, 'filter_guest', 1)

    zone_row_ref  = ft.Ref[ft.Row]()
    guest_lbl_ref = ft.Ref[ft.Text]()

    zones = [
        ("all",     "ทั้งหมด",  ft.Icons.GRID_VIEW),
        ("indoor",  "Indoor",   ft.Icons.CHAIR),
        ("outdoor", "Outdoor",  ft.Icons.PARK),
        ("seaview", "Seaview",  ft.Icons.WATER),
        ("private", "Private",  ft.Icons.MEETING_ROOM),
    ]

    def make_zone_chips():
        chips = []
        for key, label, icon in zones:
            is_sel = (selected_zone == key)
            def on_zone(e, k=key):
                nonlocal selected_zone
                selected_zone    = k
                page.filter_zone = k
                zone_row_ref.current.controls = make_zone_chips()
                page.update()
                build_floor_plan(auto_scroll=True)
            chips.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(icon, size=13,
                                color="white" if is_sel else BROWN_MID),
                        ft.Text(label, size=12,
                                weight="bold" if is_sel else "normal",
                                color="white" if is_sel else BROWN_MID),
                    ], spacing=4, tight=True),
                    bgcolor=BROWN_DARK if is_sel else BROWN_PALE,
                    padding=ft.Padding(12, 7, 12, 7),
                    border_radius=20,
                    border=ft.Border.all(1, BROWN_BORDER if not is_sel else BROWN_DARK),
                    on_click=on_zone,
                    animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                )
            )
        return chips

    def change_guest(delta):
        nonlocal guest_count
        guest_count       = max(1, guest_count + delta)
        page.filter_guest = guest_count
        guest_lbl_ref.current.value = f"{guest_count} คน"
        page.update()
        build_floor_plan(auto_scroll=True)

    filter_bar = ft.Container(
        content=ft.Column([
            ft.Row(
                ref=zone_row_ref,
                controls=make_zone_chips(),
                scroll=ft.ScrollMode.HIDDEN,
                spacing=6,
            ),
            ft.Container(height=4),
            ft.Row([
                ft.Icon(ft.Icons.PEOPLE_OUTLINE, color=BROWN_MID, size=18),
                ft.Text("จำนวนคน:", size=13, color=BROWN_MID),
                ft.IconButton(
                    ft.Icons.REMOVE_CIRCLE_OUTLINE,
                    icon_color=BROWN_LIGHT, icon_size=20,
                    on_click=lambda e: change_guest(-1),
                ),
                ft.Text(
                    ref=guest_lbl_ref,
                    value=f"{guest_count} คน",
                    size=14, weight="bold", color=BROWN_DARK,
                ),
                ft.IconButton(
                    ft.Icons.ADD_CIRCLE_OUTLINE,
                    icon_color=BROWN_LIGHT, icon_size=20,
                    on_click=lambda e: change_guest(1),
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
        ], spacing=4),
        bgcolor="white",
        padding=ft.Padding(12, 10, 12, 10),
        border_radius=12,
        margin=ft.Margin(15, 4, 15, 4),
        shadow=ft.BoxShadow(blur_radius=4, color="#00000012"),
        border=ft.Border.all(1, BROWN_BORDER + "50"),
    )

    def fetch_tables():
        try:
            zone  = getattr(page, 'filter_zone', 'all')
            count = getattr(page, 'filter_guest', 1)
            url   = f"{API_URL}/tables/filter?zone={zone}&guest_count={count}"
            response = requests.get(url, timeout=5)
            return response.json()
        except:
            return []

    def on_click_table(num, table_data):
        # เช็คว่าถ้าสถานะไม่ใช่ available ห้ามกดเลือก
        if table_data.get("status") != "available":
            snack = ft.SnackBar(
                ft.Text(f"โต๊ะ {num} ถูกจองแล้ว ไม่สามารถเลือกได้ค่ะ"),
                bgcolor="#C0392B"
            )
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return
        
        page.selected_table_num = num
        page.animating_table    = num
        status_text.value = f"โต๊ะที่เลือก: {num}"
        build_floor_plan()
        show_table_detail(page, table_data, None)

    def reset_and_refresh(e):
        page.selected_table_num = None
        status_text.value = "กรุณาเลือกโต๊ะ"
        build_floor_plan()
        page.update()

    def create_chair(top=None, bottom=None, left=None, right=None,
                     rotate=0, width=22, height=16):
        return ft.Container(
            width=width, height=height,
            bgcolor=BROWN_PALE,
            border=ft.Border.all(1, BROWN_BORDER),
            border_radius=4,
            top=top, bottom=bottom, left=left, right=right,
            rotate=rotate,
        )

    def build_floor_plan(e=None, auto_scroll=False):
        floor_plan_canvas.controls.clear()
        tables_data = fetch_tables()

        # ── Empty state ──
        if empty_msg_ref.current:
            empty_msg_ref.current.visible = (len(tables_data) == 0)

        if len(tables_data) == 0:
            page.update()
            return tables_data

        # ── หา min position_y สำหรับ auto scroll ──
        min_y = None

        for t in tables_data:
            t_num  = t["table_number"]
            status = t.get("status", "available")
            chairs = []
            rotate_table = 0
            w, h = 55, 55

            if t_num == page.selected_table_num:
                line_color = BROWN_DARK
            elif status == "available":
                line_color = "#27AE60"
            else:
                line_color = "#C0392B"

            m     = 18
            pos_x = t["position_x"]
            pos_y = t["position_y"]

            if min_y is None or pos_y < min_y:
                min_y = pos_y

            if t_num in ["C1", "C3", "D1", "D3"]:
                pos_x -= 15

            if "E" in str(t_num) or "F" in str(t_num):
                w, h = 75, 130
                chairs = [
                    create_chair(top=0, left=m+8), create_chair(top=0, left=m+40),
                    create_chair(bottom=0, left=m+8,  rotate=math.pi),
                    create_chair(bottom=0, left=m+40, rotate=math.pi),
                    create_chair(left=0, top=m+25, rotate=-math.pi/2),
                    create_chair(left=0, top=m+55, rotate=-math.pi/2),
                    create_chair(left=0, top=m+85, rotate=-math.pi/2),
                    create_chair(right=0, top=m+25, rotate=math.pi/2),
                    create_chair(right=0, top=m+55, rotate=math.pi/2),
                    create_chair(right=0, top=m+85, rotate=math.pi/2),
                ]
            elif "A" in str(t_num):
                w, h = 55, 55
                chairs = [
                    create_chair(top=0, left=m + (w/2) - 11),
                    create_chair(bottom=0, left=m + (w/2) - 11, rotate=math.pi),
                ]
            elif "B" in str(t_num):
                w, h = 55, 55
                rotate_table = math.pi / 4
                chairs = [
                    create_chair(top=10, left=10,  rotate=-math.pi/4),
                    create_chair(top=10, right=10, rotate=math.pi/4),
                    create_chair(bottom=10, left=10,  rotate=-3*math.pi/4),
                    create_chair(bottom=10, right=10, rotate=3*math.pi/4),
                ]
            elif "C" in str(t_num) or "D" in str(t_num):
                w, h = 85, 70
                chairs = [
                    create_chair(left=0, top=m + (h/2) - 20, rotate=-math.pi/2),
                    create_chair(left=0, top=m + (h/2) + 2,  rotate=-math.pi/2),
                    create_chair(right=0, top=m + (h/2) - 20, rotate=math.pi/2),
                    create_chair(right=0, top=m + (h/2) + 2,  rotate=math.pi/2),
                ]

            is_selected  = (t_num == page.selected_table_num)
            is_animating = (t_num == getattr(page, 'animating_table', None))
            scale_val    = 1.15 if is_animating else 1.0

            floor_plan_canvas.controls.append(
                ft.Container(
                    content=ft.Stack([
                        *chairs,
                        ft.Container(
                            content=ft.Text(
                                t_num, weight="bold", color=line_color, size=12,
                                rotate=-rotate_table if rotate_table != 0 else 0,
                            ),
                            width=w, height=h,
                            bgcolor=BROWN_PALE if is_selected else "white",
                            border=ft.Border.all(3.5 if is_selected else 2.5, line_color),
                            border_radius=10,
                            alignment=ft.Alignment(0, 0),
                            rotate=rotate_table,
                            margin=ft.Margin(m, m, m, m),
                            shadow=ft.BoxShadow(
                                blur_radius=16 if is_selected else 6,
                                color=BROWN_DARK + "55" if is_selected else "#00000015",
                                spread_radius=2 if is_selected else 0,
                            ),
                            scale=ft.Scale(scale_val),
                            animate_scale=ft.Animation(200, ft.AnimationCurve.BOUNCE_OUT),
                        ),
                    ]),
                    left=pos_x,
                    top=pos_y,
                    on_click=lambda e, num=t_num, td=t: on_click_table(num, td),
                )
            )

        page.animating_table = None
        page.update()

        # ── Auto scroll ไปที่โต๊ะแรกที่ filter ได้ ──
        if auto_scroll and min_y is not None and scroll_col_ref.current:
            try:
                scroll_to = max(0.0, float(min_y) - 40)
                scroll_col_ref.current.scroll_to(offset=scroll_to, duration=400)
            except Exception:
                pass

        return tables_data

    # ── Empty state message ──
    empty_msg = ft.Container(
        ref=empty_msg_ref,
        visible=False,
        content=ft.Column([
            ft.Text("🔍", size=48, text_align=ft.TextAlign.CENTER),
            ft.Container(height=8),
            ft.Text(
                "ไม่มีโต๊ะตามเงื่อนไขที่เลือก",
                size=16, weight="bold", color=BROWN_DARK,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                "ลองเปลี่ยนโซน หรือลดจำนวนคนดูนะคะ",
                size=13, color=BROWN_LIGHT,
                text_align=ft.TextAlign.CENTER,
            ),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        alignment=ft.Alignment(0, 0),
        padding=ft.Padding(20, 60, 20, 60),
    )

    scrollable_canvas = ft.Column(
        ref=scroll_col_ref,
        controls=[floor_plan_canvas, empty_msg],
        scroll=ft.ScrollMode.HIDDEN,
        expand=True,
    )

    header_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_color=BROWN_DARK,
                    on_click=lambda _: __import__('home').show_home(
                        page, getattr(page, 'user_info', None)
                    ),
                ),
                ft.Text("Book a Table", size=20, weight="bold", color=BROWN_DARK),
                ft.IconButton(
                    icon=ft.Icons.REFRESH,
                    icon_color=BROWN_LIGHT,
                    on_click=reset_and_refresh,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

            ft.Container(
                content=ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.CIRCLE, color="#C0392B", size=12),
                        ft.Text("Reserved", size=11, color=BROWN_MID),
                    ], spacing=4),
                    ft.Row([
                        ft.Icon(ft.Icons.CIRCLE, color="#27AE60", size=12),
                        ft.Text("Available", size=11, color=BROWN_MID),
                    ], spacing=4),
                    ft.Row([
                        ft.Icon(ft.Icons.CIRCLE, color=BROWN_DARK, size=10),
                        ft.Text("Selected", size=10, color=BROWN_MID),
                    ], spacing=4),
                ], alignment=ft.MainAxisAlignment.SPACE_AROUND),
                bgcolor=WHITE ,
                padding=10,
                border_radius=12,
                margin=ft.Margin(15, 5, 15, 5),
                border=ft.Border.all(1, BROWN_BORDER + "50"),
            ),

            filter_bar,
            ft.Container(content=status_text, alignment=ft.Alignment(0, 0), padding=5),
            ft.Divider(height=1, color=BROWN_BORDER + "40"),
        ]),
        padding=ft.Padding(10, 45, 10, 0),
        bgcolor=BROWN_CARD,
    )

    page.add(
        header_section,
        ft.Container(content=scrollable_canvas, expand=True, padding=5),
        ft.Container(
            content=ft.FilledButton(
                "ยืนยันโต๊ะของคุณ",
                on_click=lambda _: show_occasion_screen(
                    page, page.selected_table_num,
                    lambda p: booktable(p)
                ) if page.selected_table_num else None,
                style=ft.ButtonStyle(
                    bgcolor=BROWN_DARK,
                    color="white",
                    shape=ft.RoundedRectangleBorder(radius=10),
                ),
                width=300, height=50,
            ),
            alignment=ft.Alignment(0, 0),
            padding=15,
            bgcolor=BROWN_CARD,
        ),
    )
    build_floor_plan()


if __name__ == "__main__":
    ft.run(booktable)