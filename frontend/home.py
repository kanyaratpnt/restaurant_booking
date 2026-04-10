import os
import flet as ft
import requests
from datetime import date, datetime
from booktable import booktable

API_URL = "http://192.168.1.41:8000"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Brown palette (6-digit hex เท่านั้น) ──
BROWN_DARK   = "#4A2C0A"
BROWN_MID    = "#7B4A1E"
BROWN_LIGHT  = "#C8965A"
BROWN_PALE   = "#F5E6D3"
BROWN_CARD   = "#FDF6EE"
BROWN_BORDER = "#D4A574"
ACCENT       = "#E8B86D"

ZONE_FEATURES = [
    ("🪑", "Indoor",   "บรรยากาศอบอุ่น\nในร้าน",        "indoor",  "indoor.jpg"),
    ("🌿", "Outdoor",  "สวนสวยร่มรื่น\nอากาศดี",         "outdoor", "outdoor.jpg"),
    ("🌊", "Seaview",  "วิวทะเลสวย\nโรแมนติก",           "seaview", "seaview.jpg"),
    ("🚪", "Private",  "ห้องส่วนตัว\nความเป็นส่วนตัว",  "private", "private.jpg"),
]

def img(filename: str) -> str:
    return f"{API_URL}/image/{filename}"

def rgba(hex6: str, opacity: float) -> str:
    return ft.Colors.with_opacity(opacity, hex6)


def show_home(page: ft.Page, user_info: dict, on_login_success=None):
    page.clean()
    page.title = "SEAVIEW Restaurant"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = BROWN_CARD
    page.scroll = None

    page.user_info = user_info

    info        = user_info or {}
    name        = info.get("name") or info.get("phone") or "ผู้ใช้งาน"
    if name in ("guest", "ผู้ใช้งาน", ""):
        name = "ผู้ใช้งาน"
    customer_id = info.get("customer_id", 0)
    is_guest    = (customer_id == 0)

    reservations_col = ft.Ref[ft.Column]()
    loading_ref      = ft.Ref[ft.Container]()
    empty_ref        = ft.Ref[ft.Container]()

    # ─────────────────────────────────────────
    #   Navigation
    # ─────────────────────────────────────────
    def go_book(e=None):
        page.filter_zone  = "all"
        page.filter_guest = 2
        page.filter_date  = date.today().strftime("%Y-%m-%d")
        page.filter_time  = "18:00"
        booktable(page)

    def go_book_zone(zone_key):
        page.filter_zone  = zone_key
        page.filter_guest = 2
        page.filter_date  = date.today().strftime("%Y-%m-%d")
        page.filter_time  = "18:00"
        booktable(page)

    # ─────────────────────────────────────────
    #   Reservations helpers
    # ─────────────────────────────────────────
    def load_reservations():
            if is_guest or customer_id == 0:
                return []
            try:
                # ตรวจสอบให้แน่ใจว่าเรียก API ถูกตัว
                res = requests.get(
                    f"{API_URL}/reservations/customer/{customer_id}", 
                    timeout=5
                )
                if res.status_code == 200:
                    return res.json()
                else:
                    print(f"Error: {res.status_code}") # ไว้ Debug ใน Terminal
            except Exception as e:
                print(f"Fetch error: {e}")
            return []

    def get_status_info(status):
        return {
            "pending":   ("⏳", "รอยืนยัน",   "#E67E22", "#FFF8E1"),
            "confirmed": ("✅", "ยืนยันแล้ว",  "#27AE60", "#E8F5E9"),
            "cancelled": ("❌", "ยกเลิกแล้ว",  "#C0392B", "#FFEBEE"),
            "completed": ("🍽️", "เสร็จสิ้น",   "#7F8C8D", "#F5F5F5"),
        }.get(status, ("❓", status, "#7F8C8D", "#F5F5F5"))

    def get_occasion_label(occasion):
        return {
            "birthday":    "🎂 วันเกิด",
            "anniversary": "💍 วันครบรอบ",
            "business":    "💼 ธุรกิจ",
            "first_date":  "🌹 เดทแรก",
            "general":     "✨ ทั่วไป",
        }.get(occasion, occasion or "-")

    def build_reservation_card(r):
        res_id = r.get("id")         
        status = r.get("status", "pending")

        emoji, label, color, bg = get_status_info(r.get("status", "pending"))
        t_num    = r.get("table_number", "-")
        g_count  = r.get("guest_count", "-")
        raw_time = r.get("reservation_time", "")
        try:
            dt       = datetime.fromisoformat(raw_time)
            time_str = dt.strftime("%d %b %Y  •  %H:%M น.")
        except Exception:
            time_str = raw_time or "-"
        occasion_str = get_occasion_label(r.get("occasion"))

        cancel_btn = ft.TextButton(
            content=ft.Row([
                ft.Icon(ft.Icons.CANCEL_OUTLINED, size=16, color="#C0392B"),
                ft.Text("ยกเลิกการจอง", size=12, color="#C0392B", weight="bold"),
            ], tight=True),
            on_click=lambda _: cancel_booking(res_id),
            visible=(status in ["pending", "confirmed"]) # ถ้า cancelled แล้วไม่ต้องโชว์ปุ่ม
        )

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"โต๊ะ {t_num}", size=18, weight="bold", color=BROWN_DARK),
                    ft.Container(
                        content=ft.Row([
                            ft.Text(emoji, size=11),
                            ft.Container(width=4),
                            ft.Text(label, size=11, weight="bold", color=color),
                        ], spacing=0),
                        bgcolor=bg,
                        padding=ft.Padding(10, 5, 10, 5),
                        border_radius=20,
                        border=ft.Border.all(1, color),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=8),
                ft.Divider(height=1, color=rgba(BROWN_BORDER, 0.2)),
                ft.Row([
                    ft.Container(), # ดันปุ่มไปทางขวา
                    cancel_btn
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([
                    ft.Icon(ft.Icons.ACCESS_TIME_ROUNDED, size=13, color=BROWN_LIGHT),
                    ft.Text(time_str, size=12, color=BROWN_MID),
                ], spacing=5),
                ft.Container(height=4),
                ft.Row([
                    ft.Icon(ft.Icons.PEOPLE_ALT_OUTLINED, size=13, color=BROWN_LIGHT),
                    ft.Text(f"{g_count} ท่าน", size=12, color=BROWN_MID),
                ], spacing=5),
                ft.Container(height=4),
                ft.Row([
                    ft.Icon(ft.Icons.CELEBRATION_OUTLINED, size=13, color=BROWN_LIGHT),
                    ft.Text(occasion_str, size=12, color=BROWN_MID),
                ], spacing=5),
            ], spacing=0),
            bgcolor="white",
            padding=ft.Padding(16, 14, 16, 14),
            border_radius=16,
            shadow=ft.BoxShadow(blur_radius=8, color=rgba("#000000", 0.07)),
            border=ft.Border.all(1, rgba(BROWN_BORDER, 0.4)),
        )

    def refresh_reservations(e=None):
        if loading_ref.current:
            loading_ref.current.visible = True
        if reservations_col.current:
            reservations_col.current.controls.clear()
        page.update()
        data = load_reservations()
        if loading_ref.current:
            loading_ref.current.visible = False
        if empty_ref.current:
            empty_ref.current.visible = (len(data) == 0 and not is_guest)
        if reservations_col.current:
            for r in data:
                reservations_col.current.controls.append(build_reservation_card(r))
        page.update()

    def confirm_logout():
        def do_logout(e):          
            bs.open = False
            page.update()
            from login import show_login
            if on_login_success:
                show_login(page, on_login_success)

        logout_btn = ft.Container(
            content=ft.Row([
                ft.Container(
                    content=ft.Icon(ft.Icons.LOGOUT_ROUNDED, size=18, color="#C0392B"),
                    width=40, height=40, bgcolor="#FFEEEE",
                    border_radius=12, alignment=ft.Alignment(0, 0),
                ),
                ft.Column([
                    ft.Text("ออกจากระบบ", size=14, weight="bold", color="#C0392B"),
                    ft.Text("กลับสู่หน้าล็อกอิน", size=11, color="#E57373"),
                ], spacing=2, tight=True),
                ft.Container(expand=True),
                ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, size=18, color="#E57373"),
            ], spacing=12),
            bgcolor="#FFF5F5",
            border_radius=14,
            padding=ft.Padding(14, 12, 14, 12),
            border=ft.Border.all(1, "#FFDDDD"),
            on_click=do_logout,   # ← เพิ่มตรงนี้
        )

        bs = ft.BottomSheet(
            content=ft.Container(
                content=ft.Column([
                    ft.Container(
                        ft.Container(width=36, height=4, bgcolor=BROWN_BORDER, border_radius=2),
                        alignment=ft.Alignment(0, 0),
                        padding=ft.Padding(0, 10, 0, 0),
                    ),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Container(
                            content=ft.Text(name[0].upper(), size=18, weight="bold", color=BROWN_DARK),
                            width=48, height=48, bgcolor=BROWN_PALE,
                            border_radius=24, alignment=ft.Alignment(0, 0),
                            border=ft.Border.all(2, BROWN_BORDER),
                        ),
                        ft.Column([
                            ft.Text(name, size=15, weight="bold", color=BROWN_DARK),
                            ft.Text("ผู้ใช้งานทั่วไป", size=11, color=BROWN_LIGHT),
                        ], spacing=2, tight=True),
                    ], spacing=14),
                    ft.Container(height=16),
                    ft.Divider(height=1, color=rgba(BROWN_BORDER, 0.4)),
                    ft.Container(height=12),
                    logout_btn,
                    ft.Container(height=24),
                ], spacing=0),
                padding=ft.Padding(20, 0, 20, 0),
                bgcolor="white",
                border_radius=ft.BorderRadius(20, 20, 0, 0),
            ),
            open=True,
            bgcolor="white",
        )

        page.overlay.append(bs)
        page.update()

    # ─────────────────────────────────────────
    #   HERO BANNER
    # ─────────────────────────────────────────
    hero = ft.Container(
        height=330,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        border_radius=ft.BorderRadius(0, 0, 24, 24),
        shadow=ft.BoxShadow(blur_radius=16, color=rgba("#000000", 0.14)),
        content=ft.Stack([

            # L1 — ภาพพื้นหลัง
            ft.Image(
                src=img("hero.jpg"),
                fit="cover",
                width=page.width or 400,    
                height=330,
            ),

            # L2 — Solid overlay 31%
            ft.Container(
                bgcolor=rgba("#000000", 0.31),
                expand=True,
            ),

            # L3 — Gradient overlay (บนจาง → ล่างเข้ม)
            ft.Container(
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0, -1),
                    end=ft.Alignment(0, 1),
                    colors=["#00000030", "#000000BB", "#000000EE"],
                ),
                expand=True,
            ),

            # L4 — Content
            ft.Container(
                padding=ft.Padding(20, 44, 20, 24),
                expand=True,
                content=ft.Column([
                    # Avatar ขวาบน
                    ft.Row([
                        ft.Container(),
                        ft.Container(
                            content=ft.Text(
                                name[0].upper() if name else "U",
                                size=14, weight="bold", color=BROWN_DARK,
                            ),
                            width=36, height=36,
                            bgcolor=ACCENT,
                            border_radius=18,
                            alignment=ft.Alignment(0, 0),
                            on_click=lambda _: confirm_logout(),
                        ),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                    ft.Container(height=14),
                    ft.Text(f"สวัสดี, {name}", size=16, color=ACCENT),
                    ft.Container(height=4),
                    ft.Text(
                        "ยินดีต้อนรับสู่\nDaylight Restaurant",
                        size=24, weight="bold", color="white",
                    ),
                    ft.Container(height=8),
                    ft.Text(
                        "วิวทะเลสวย  •  บรรยากาศดี  •  อาหารอร่อย",
                        size=13, color="white", weight="bold",
                    ),
                    ft.Container(height=18),

                    # ปุ่มจองโต๊ะ
                    ft.Container(
                        content=ft.Row([
                            ft.Icon(ft.Icons.TABLE_RESTAURANT_ROUNDED,
                                    color=BROWN_DARK, size=16),
                            ft.Container(width=8),
                            ft.Text("จองโต๊ะเลย", size=14,
                                    weight="bold", color=BROWN_DARK),
                            ft.Container(width=4),
                            ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED,
                                    color=BROWN_DARK, size=14),
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        on_click=go_book,
                        bgcolor=ACCENT,
                        border_radius=12,
                        padding=ft.Padding(0, 12, 0, 12),
                        width=200,
                        shadow=ft.BoxShadow(
                            blur_radius=16,
                            color=rgba(ACCENT, 0.38),
                        ),
                    ),
                ], spacing=0),
            ),
        ]),
    )

    # ─────────────────────────────────────────
    #   ZONE CARDS
    # ─────────────────────────────────────────
    def make_zone_card(emoji, label, desc, zone_key, image_file):
        W, H = 160, 200
        return ft.GestureDetector(
            on_tap=lambda e, zk=zone_key: go_book_zone(zk),
            content=ft.Container(
                width=W,
                height=H,
                border_radius=18,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                shadow=ft.BoxShadow(blur_radius=14, color=rgba("#000000", 0.20)),
                content=ft.Stack(
                    expand=True,
                    controls=[

                        # L1 — ภาพ (กำหนด width/height ตรงๆ ให้เต็มกรอบ)
                        ft.Image(
                            src=img(image_file),
                            fit="cover",
                            width=W,
                            height=H,
                        ),

                        # L2 — Gradient เข้มด้านล่าง
                        ft.Container(
                            gradient=ft.LinearGradient(
                                begin=ft.Alignment(0, -0.2),
                                end=ft.Alignment(0, 1),
                                colors=["#00000000", "#000000CC", "#000000F0"],
                            ),
                            expand=True,
                        ),

                        # L3 — กล่องข้อความด้านล่าง (absolute position)
                        ft.Container(
                            bottom=0,
                            left=0,
                            right=0,
                            padding=ft.Padding(8, 0, 8, 10),
                            content=ft.Container(
                                content=ft.Column([
                                    ft.Text(
                                        label,
                                        size=13,
                                        weight="bold",
                                        color="white",
                                        text_align=ft.TextAlign.LEFT,
                                    ),
                                    ft.Container(height=3),
                                    ft.Text(
                                        desc,
                                        size=9,
                                        color=rgba("#FFFFFF", 0.85),
                                        text_align=ft.TextAlign.LEFT,
                                    ),
                                ], spacing=0, tight=True),
                                bgcolor=rgba("#000000", 0.55),
                                padding=ft.Padding(8, 6, 8, 6),
                                border_radius=ft.BorderRadius(8, 8, 0, 0),
                                border=ft.Border(
                                    left=ft.BorderSide(2, rgba(ACCENT, 0.85)),
                                ),
                            ),
                        ),
                    ],
                ),
            ),
        )

    zone_cards = ft.Row(
        controls=[make_zone_card(*args) for args in ZONE_FEATURES],
        scroll=ft.ScrollMode.AUTO,
        spacing=15,
    )

    # ─────────────────────────────────────────
    #   INFO STRIP
    # ─────────────────────────────────────────
    def info_chip(icon, text):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=14, color=BROWN_MID),
                ft.Text(text, size=11, color=BROWN_MID),
            ], spacing=6, tight=True),
            bgcolor=BROWN_PALE,
            padding=ft.Padding(12, 8, 12, 8),
            border_radius=20,
            border=ft.Border.all(1, BROWN_BORDER),
        )

    info_strip = ft.Row([
        info_chip(ft.Icons.ACCESS_TIME_ROUNDED,  "เปิด 11:00–22:00"),
        info_chip(ft.Icons.LOCATION_ON_OUTLINED, "อโศก, กรุงเทพ"),
        info_chip(ft.Icons.WIFI_ROUNDED,         "Free WiFi"),
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    scroll=None)

    # ─────────────────────────────────────────
    #   MY RESERVATIONS
    # ─────────────────────────────────────────
    loading_spinner = ft.Container(
        ref=loading_ref,
        content=ft.Row([
            ft.ProgressRing(width=18, height=18, stroke_width=2, color=BROWN_MID),
            ft.Text("กำลังโหลด...", size=12, color=BROWN_LIGHT),
        ], spacing=10, alignment=ft.MainAxisAlignment.CENTER),
        visible=True,
        padding=ft.Padding(0, 16, 0, 8),
    )

    empty_state = ft.Container(
        ref=empty_ref,
        visible=False,
        content=ft.Column([
            ft.Text("🍽️", size=40, text_align=ft.TextAlign.CENTER),
            ft.Container(height=8),
            ft.Text("ยังไม่มีรายการจอง", size=14, color=BROWN_LIGHT,
                    text_align=ft.TextAlign.CENTER),
            ft.Text("จองโต๊ะแรกของคุณได้เลย!", size=12, color=BROWN_BORDER,
                    text_align=ft.TextAlign.CENTER),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        padding=ft.Padding(0, 20, 0, 10),
    )

    my_bookings_column = ft.Column(ref=reservations_col, controls=[], spacing=10)

    guest_notice = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.INFO_OUTLINE_ROUNDED, size=14, color=BROWN_LIGHT),
            ft.Text("เข้าสู่ระบบเพื่อดูรายการจองของคุณ",
                    size=12, color=BROWN_MID),
        ], spacing=8),
        bgcolor=BROWN_PALE,
        padding=ft.Padding(14, 10, 14, 10),
        border_radius=12,
        border=ft.Border.all(1, rgba(BROWN_BORDER, 0.44)),
        visible=is_guest,
    )

    my_reservations_section = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("รายการจองของฉัน", size=14,
                        weight="bold", color=BROWN_DARK),
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Icon(ft.Icons.REFRESH_ROUNDED,
                                        size=16, color=BROWN_MID),
                        width=32, height=32,
                        bgcolor=BROWN_PALE,
                        border_radius=16,
                        alignment=ft.Alignment(0, 0),
                        border=ft.Border.all(1, BROWN_BORDER),
                    ),
                    on_tap=refresh_reservations,
                ),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Container(height=12),
            guest_notice,
            loading_spinner,
            empty_state,
            my_bookings_column,
        ], spacing=0),
        bgcolor="white",
        padding=ft.Padding(18, 16, 18, 16),
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=10, color=rgba("#000000", 0.06)),
        border=ft.Border.all(1, rgba(BROWN_BORDER, 0.25)),
    )

    # ─────────────────────────────────────────
    #   MAIN LAYOUT
    # ─────────────────────────────────────────
    page.add(
        ft.Column(
            controls=[
                hero,
                ft.Container(
                    content=ft.Column([
                        ft.Container(height=18),
                        ft.Container(info_strip, padding=ft.Padding(20, 0, 20, 0)),
                        ft.Container(height=24),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("เลือกโซนที่ชอบ", size=15, weight="bold", color=BROWN_DARK),
                                ft.Text("แตะการ์ดเพื่อดูโต๊ะว่างในโซนนั้น", size=11, color=BROWN_LIGHT),
                            ], spacing=0),
                            padding=ft.Padding(20, 0, 20, 0)
                        ),
                        ft.Container(height=12),
                        
                        ft.Container(
                            content=zone_cards,
                            padding=ft.Padding(20, 0, 0, 0),
                        ),

                        ft.Container(height=22),
                        
                        ft.Container(
                            content=ft.Column([
                                ft.Container(
                                    content=ft.Row([
                                        ft.Icon(ft.Icons.SEARCH_ROUNDED, color="white", size=18),
                                        ft.Container(width=8),
                                        ft.Text("ดูโต๊ะว่างทั้งหมด", size=15, weight="bold", color="white"),
                                    ], alignment=ft.MainAxisAlignment.CENTER),
                                    on_click=go_book,
                                    gradient=ft.LinearGradient(
                                        begin=ft.Alignment(-1, 0),
                                        end=ft.Alignment(1, 0),
                                        colors=[BROWN_DARK, BROWN_MID],
                                    ),
                                    border_radius=16,
                                    padding=ft.Padding(0, 16, 0, 16),
                                    shadow=ft.BoxShadow(blur_radius=16, color=rgba(BROWN_DARK, 0.25)),
                                ),
                                ft.Container(height=22),
                                my_reservations_section,
                                ft.Container(height=32),
                            ], spacing=0),
                            padding=ft.Padding(20, 0, 20, 0)
                        ),
                    ], spacing=0),
                    expand=True,
                ),
            ],
            spacing=0,
            scroll=ft.ScrollMode.ADAPTIVE,
            expand=True,
        )
    )

    def cancel_booking(reservation_id):
        try:
            res = requests.post(f"{API_URL}/reservations/{reservation_id}/cancel")
            if res.status_code == 200:
                # ถ้าสำเร็จ ให้รีเฟรชรายการใหม่ทันที
                refresh_reservations()
                page.snack_bar = ft.SnackBar(ft.Text("ยกเลิกการจองเรียบร้อยแล้ว"), bgcolor="#C0392B")
                page.snack_bar.open = True
                page.update()
        except Exception as e:
            print(f"Cancel error: {e}")

    page.update()
    refresh_reservations()


if __name__ == "__main__":
    ft.app(target=lambda page: show_home(
        page, {"name": "ผู้ใช้", "customer_id": 1}
    ))