import flet as ft
import requests
import os
import base64
from datetime import datetime, date, timedelta

API_URL = "http://192.168.1.41:8000"

BG          = "#F2EBE0"
SURFACE     = "#FDF8F2"
CARD        = "#FFFFFF"
CARD2       = "#FAF5EE"
BORDER      = "#DDD0BE"
BORDER2     = "#C9B89E"
GOLD        = "#C8963E"
GOLD_DARK   = "#9B6E1F"
GOLD_PALE   = "#C8963E20"
GOLD_RICH   = "#E8B04B"
ESPRESSO    = "#2B1A0D"
MAHOGANY    = "#6B2D0F"
CREAM       = "#F9F1E3"
COPPER      = "#B5622B"
TEXT_PRI    = "#1C0F06"
TEXT_SEC    = "#7A5C3E"
TEXT_DIM    = "#B89A7A"
TEXT_LIGHT  = "#FDF5E8"
AMBER       = "#D4860A"
GREEN       = "#3A7A2E"
GREEN_RICH  = "#4E9E40"
RED         = "#B83030"
RED_RICH    = "#D04040"
BLUE        = "#2E5F9A"

STATUS_CONFIG = {
    "pending":   {
        "color": AMBER,     
        "bg":    "#FEF3C7", 
        "label": "รอยืนยัน",
        "icon":  ft.Icons.HOURGLASS_EMPTY_ROUNDED
    },
    "confirmed": {
        "color": GREEN_RICH,
        "bg":    "#D1FAE5", 
        "label": "ยืนยันแล้ว",
        "icon":  ft.Icons.CHECK_CIRCLE_OUTLINE
    },
    "cancelled": {
        "color": RED_RICH,
        "bg":    "#FEE2E2", 
        "label": "ยกเลิก",
        "icon":  ft.Icons.CANCEL_OUTLINED
    },
    "completed": {
        "color": BLUE,
        "bg":    "#DBEAFE",  
        "label": "เสร็จสิ้น",
        "icon":  ft.Icons.RESTAURANT_OUTLINED
    },
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

def rgba(hex6, opacity):
    return ft.Colors.with_opacity(opacity, hex6)


def _load_hero_b64():
    """
    ลองหา hero.jpg/png จากหลาย path
    คืน data URI ถ้าเจอ ไม่งั้น None
    """
    _here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(os.getcwd(), "image", "hero.jpg"),
        os.path.join(os.getcwd(), "image", "hero.png"),
        os.path.join(_here, "image", "hero.jpg"),
        os.path.join(_here, "image", "hero.png"),
        os.path.join(_here, "hero.jpg"),
        os.path.join(_here, "hero.png"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                ext = "jpeg" if path.endswith(".jpg") else "png"
                with open(path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                print(f"[hero] OK: {path}")
                return f"data:image/{ext};base64,{b64}"
            except Exception as ex:
                print(f"[hero] read error {path}: {ex}")
    print(f"[hero] not found in: {candidates}")
    return None


HERO_SRC = _load_hero_b64()


def show_restaurant_dashboard(page: ft.Page, user_info: dict):
    page.clean()
    page.title = "Restaurant Dashboard"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = BG

    info = user_info or {}
    name = info.get("name") or "ร้านค้า"

    state = {
        "filter_status": "all",
        "filter_range":  "today",
        "all_data":      [],
    }

    list_col              = ft.Ref[ft.Column]()
    stat_total_ref        = ft.Ref[ft.Text]()
    stat_pend_ref         = ft.Ref[ft.Text]()
    stat_conf_ref         = ft.Ref[ft.Text]()
    stat_canc_ref         = ft.Ref[ft.Text]()
    loading_ref           = ft.Ref[ft.Container]()
    empty_ref             = ft.Ref[ft.Container]()
    status_filter_row_ref = ft.Ref[ft.Row]()
    range_filter_row_ref  = ft.Ref[ft.Row]()

    def fetch_all():
        try:
            res = requests.get(f"{API_URL}/reservations/all", timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    def filter_data(data):
        today     = datetime.now().date()
        range_key = state["filter_range"]
        filtered  = []
        for r in data:
            try:
                r_date = datetime.fromisoformat(r.get("reservation_time", "")).date()
            except Exception:
                r_date = None
            if range_key == "today":
                if r_date == today: filtered.append(r)
            elif range_key == "week":
                ws = today - timedelta(days=today.weekday())
                if r_date and ws <= r_date <= ws + timedelta(days=6): filtered.append(r)
            elif range_key == "month":
                if r_date and r_date.month == today.month and r_date.year == today.year: filtered.append(r)
            else:
                filtered.append(r)
        sk = state["filter_status"]
        if sk != "all":
            filtered = [r for r in filtered if r.get("status") == sk]
        return filtered

    def update_stats_for_range():
        today     = datetime.now().date()
        range_key = state["filter_range"]
        rf = []
        for r in state["all_data"]:
            try:
                r_date = datetime.fromisoformat(r.get("reservation_time", "")).date()
            except Exception:
                r_date = None
            if range_key == "today":
                if r_date == today: rf.append(r)
            elif range_key == "week":
                ws = today - timedelta(days=today.weekday())
                if r_date and ws <= r_date <= ws + timedelta(days=6): rf.append(r)
            elif range_key == "month":
                if r_date and r_date.month == today.month and r_date.year == today.year: rf.append(r)
            else:
                rf.append(r)
        if stat_total_ref.current: stat_total_ref.current.value = str(len(rf))
        if stat_pend_ref.current:  stat_pend_ref.current.value  = str(sum(1 for r in rf if r.get("status") == "pending"))
        if stat_conf_ref.current:  stat_conf_ref.current.value  = str(sum(1 for r in rf if r.get("status") == "confirmed"))
        if stat_canc_ref.current:  stat_canc_ref.current.value  = str(sum(1 for r in rf if r.get("status") == "cancelled"))

    def update_status_api(reservation_id, new_status):
        try:
            requests.patch(
                f"{API_URL}/reservations/{reservation_id}/status",
                json={"status": new_status}, timeout=5
            )
        except Exception:
            pass
        load_and_render()

    def load_and_render():
        if loading_ref.current: loading_ref.current.visible = True
        if list_col.current:    list_col.current.controls.clear()
        page.update()
        raw = fetch_all()
        state["all_data"] = raw
        filtered = filter_data(raw)
        update_stats_for_range()
        if loading_ref.current: loading_ref.current.visible = False
        if empty_ref.current:   empty_ref.current.visible = (len(filtered) == 0)
        if list_col.current:
            for r in filtered:
                list_col.current.controls.append(build_card(r))
        rebuild_filter_chips()
        page.update()

    # ── Bottom Sheet ──
    def show_detail(r):
        status = r.get("status", "pending")
        cfg    = STATUS_CONFIG.get(status, STATUS_CONFIG["pending"])
        rid    = r.get("id")
        try:
            dt_str = datetime.fromisoformat(r.get("reservation_time", "")).strftime("%d %b %Y  •  %H:%M น.")
        except Exception:
            dt_str = r.get("reservation_time", "-")
        occasion_key = r.get("occasion", "general") or "general"
        cust_id      = r.get("customer_id", "-")
        cust_name    = r.get("customer_name") or f"ลูกค้า #{cust_id}"
        phone_val    = r.get("phone") or "-"
        guest_count  = r.get("guest_count", "-")
        table_cap    = r.get("table_capacity")
        notes        = r.get("special_requests") or "-"
        cap_text     = f"{guest_count} ท่าน" + (f"  (สูงสุด {table_cap} ท่าน)" if table_cap else "")

        def close_bs(bs):
            bs.open = False
            bs.update()

        def detail_row(icon, label, value, val_color=TEXT_PRI):
            return ft.Container(
                content=ft.Row([
                    ft.Container(content=ft.Icon(icon, size=16, color=CARD2),
                                 width=36, height=36, bgcolor=TEXT_SEC,
                                 border_radius=10, alignment=ft.Alignment(0, 0)),
                    ft.Column([
                        ft.Text(label, size=10, color=TEXT_SEC),
                        ft.Text(str(value) if value else "-", size=14, weight="w600", color=val_color),
                    ], spacing=1, tight=True),
                ], spacing=12),
                padding=ft.Padding(0, 5, 0, 5),
            )

        status_badge = ft.Container(
            content=ft.Row([
                ft.Icon(cfg["icon"], size=13, color=cfg["color"]),
                ft.Container(width=4),
                ft.Text(cfg["label"], size=11, weight="bold", color=cfg["color"]),
            ], tight=True),
            bgcolor=cfg["bg"], padding=ft.Padding(10, 6, 10, 6),
            border_radius=20, border=ft.Border.all(1, rgba(cfg["color"], 0.4)),
        )

        confirm_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.CHECK_ROUNDED, size=16, color=CARD),
                            ft.Text("ยืนยันการจอง", size=13, weight="bold", color=CARD)],
                           alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            bgcolor=GREEN_RICH, border_radius=12, padding=ft.Padding(0, 14, 0, 14),
            expand=True, alignment=ft.Alignment(0, 0),
            visible=(status == "pending"), on_click=lambda e: None,
        )
        complete_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.RESTAURANT_ROUNDED, size=16, color=CARD),
                            ft.Text("เสร็จสิ้น", size=13, weight="bold", color=CARD)],
                           alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            bgcolor=BLUE, border_radius=12, padding=ft.Padding(0, 14, 0, 14),
            expand=True, alignment=ft.Alignment(0, 0),
            visible=(status == "confirmed"), on_click=lambda e: None,
        )
        cancel_btn = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.CLOSE_ROUNDED, size=16, color=CARD),
                            ft.Text("ยกเลิก", size=13, weight="bold", color=CARD)],
                           alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            bgcolor=RED_RICH, border_radius=12, padding=ft.Padding(0, 14, 0, 14),
            expand=True, alignment=ft.Alignment(0, 0),
            visible=(status in ["pending", "confirmed"]), on_click=lambda e: None,
        )

        bs_content = ft.Container(
            content=ft.Column([
                ft.Container(ft.Container(width=44, height=4, bgcolor=BORDER2, border_radius=2),
                             alignment=ft.Alignment(0, 0), padding=ft.Padding(0, 10, 0, 4)),
                ft.Container(height=4),
                ft.Row([
                    ft.Column([
                        ft.Text(f"โต๊ะ {r.get('table_number', '-')}", size=24, weight="bold", color=TEXT_PRI),
                        ft.Text(f"การจอง #{rid}", size=12, color=TEXT_SEC),
                    ], spacing=3),
                    status_badge,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=16),
                ft.Container(
                    content=ft.Column([
                        detail_row(ft.Icons.PERSON_OUTLINE_ROUNDED, "ชื่อลูกค้า", cust_name),
                        ft.Divider(height=1, color=BORDER),
                        detail_row(ft.Icons.PHONE_OUTLINED, "เบอร์ติดต่อ", phone_val),
                        ft.Divider(height=1, color=BORDER),
                        detail_row(ft.Icons.ACCESS_TIME_ROUNDED, "วันเวลาจอง", dt_str),
                        ft.Divider(height=1, color=BORDER),
                        detail_row(ft.Icons.GROUP_OUTLINED, "จำนวนผู้เข้าร่วม", cap_text),
                        ft.Divider(height=1, color=BORDER),
                        detail_row(OCCASION_ICONS.get(occasion_key, ft.Icons.RESTAURANT_OUTLINED),
                                   "โอกาสพิเศษ", OCCASION_LABELS.get(occasion_key, "ทั่วไป")),
                    ], spacing=0),
                    bgcolor=CARD2, border_radius=14,
                    padding=ft.Padding(16, 8, 16, 8), border=ft.Border.all(1, BORDER),
                ),
                ft.Container(height=12),
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Icon(ft.Icons.EDIT_NOTE_ROUNDED, size=15, color=CARD),
                                ft.Text("โน้ตจากลูกค้า", size=12, color=SURFACE, weight="w600")], spacing=6),
                        ft.Container(height=6),
                        ft.Text(notes, size=13, color=TEXT_PRI, no_wrap=False),
                    ]),
                    bgcolor=TEXT_SEC, padding=ft.Padding(14, 12, 14, 12),
                    border_radius=12, border=ft.Border.all(1, rgba(GOLD, 0.3)),
                ),
                ft.Container(height=20),
                ft.Row([confirm_btn, complete_btn, cancel_btn], spacing=8),
                ft.Container(height=8),
            ], spacing=0, scroll=ft.ScrollMode.ADAPTIVE),
            bgcolor=CARD, padding=ft.Padding(20, 0, 20, 24),
            border_radius=ft.BorderRadius(24, 24, 0, 0),
        )

        bs = ft.BottomSheet(content=bs_content, open=True, bgcolor=CARD)
        confirm_btn.on_click  = lambda e: (close_bs(bs), update_status_api(rid, "confirmed"))
        complete_btn.on_click = lambda e: (close_bs(bs), update_status_api(rid, "completed"))
        cancel_btn.on_click   = lambda e: (close_bs(bs), update_status_api(rid, "cancelled"))
        page.overlay.append(bs)
        page.update()

    # ── Card ──
    def build_card(r):
        status    = r.get("status", "pending")
        cfg       = STATUS_CONFIG.get(status, STATUS_CONFIG["pending"])
        rid       = r.get("id")
        cust_id   = r.get("customer_id", "-")
        cust_name = r.get("customer_name") or f"ลูกค้า #{cust_id}"
        try:
            dt_str = datetime.fromisoformat(r.get("reservation_time", "")).strftime("%d/%m  %H:%M")
        except Exception:
            dt_str = r.get("reservation_time", "-")
        occasion_key = r.get("occasion", "general") or "general"
        table_num    = r.get("table_number", "-")
        g_count      = r.get("guest_count", "-")

        status_badge = ft.Container(
            content=ft.Row([ft.Icon(cfg["icon"], size=10, color=cfg["color"]),
                            ft.Container(width=4),
                            ft.Text(cfg["label"], size=10, color=cfg["color"], weight="bold")],
                           tight=True, spacing=0),
            bgcolor=cfg["bg"], padding=ft.Padding(8, 4, 8, 4),
            border_radius=12, border=ft.Border.all(1, rgba(cfg["color"], 0.35)),
        )

        quick_confirm = ft.Container(
            content=ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=20, color=GREEN_RICH),
            width=36, height=36, bgcolor=rgba(GREEN_RICH, 0.15), border_radius=18,
            alignment=ft.Alignment(0, 0), border=ft.Border.all(1, rgba(GREEN_RICH, 0.45)),
            visible=(status == "pending"),
            on_click=lambda e, rid_=rid: update_status_api(rid_, "confirmed"),
            tooltip="ยืนยันเร็ว",
        )

        return ft.Container(
            content=ft.Row([
                ft.Container(width=4, bgcolor=cfg["color"], border_radius=ft.BorderRadius(4, 0, 0, 4)),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Column([
                                ft.Text(f"โต๊ะ {table_num}", size=15, weight="bold", color=TEXT_PRI),
                                ft.Container(height=2),
                                ft.Row([ft.Icon(ft.Icons.PERSON_OUTLINE_ROUNDED, size=11, color=TEXT_DIM),
                                        ft.Text(cust_name, size=11, color=TEXT_SEC)], spacing=3),
                            ], spacing=0, tight=True, expand=True),
                            ft.Column([
                                status_badge,
                                ft.Container(height=4),
                                ft.Row([ft.Text("ดูรายละเอียด", size=10, color=GOLD),
                                        ft.Icon(ft.Icons.CHEVRON_RIGHT_ROUNDED, size=14, color=GOLD)],
                                       spacing=0, tight=True),
                            ], horizontal_alignment=ft.CrossAxisAlignment.END, spacing=0),
                        ]),
                        ft.Container(height=10),
                        ft.Row([
                            ft.Row([ft.Icon(ft.Icons.ACCESS_TIME_OUTLINED, size=12, color=TEXT_DIM),
                                    ft.Text(dt_str, size=11, color=TEXT_SEC)], spacing=4),
                            ft.Row([ft.Icon(ft.Icons.GROUP_OUTLINED, size=12, color=TEXT_DIM),
                                    ft.Text(f"{g_count} คน", size=11, color=TEXT_SEC)], spacing=4),
                            ft.Row([ft.Icon(OCCASION_ICONS.get(occasion_key, ft.Icons.RESTAURANT_OUTLINED),
                                           size=12, color=TEXT_DIM),
                                    ft.Text(OCCASION_LABELS.get(occasion_key, "ทั่วไป"), size=11, color=TEXT_SEC)],
                                   spacing=4),
                            ft.Container(expand=True),
                            quick_confirm,
                        ], spacing=12),
                    ], spacing=0),
                    expand=True, padding=ft.Padding(14, 14, 12, 14),
                ),
            ], spacing=0),
            bgcolor=CARD, border_radius=14, border=ft.Border.all(1, BORDER),
            shadow=ft.BoxShadow(blur_radius=12, color=rgba(ESPRESSO, 0.08), offset=ft.Offset(0, 3)),
            on_click=lambda e, rv=r: show_detail(rv),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

    # ── Filter Chips ──
    def make_status_chip(key, label, icon):
        is_active = (state["filter_status"] == key)
        def on_tap(e, k=key):
            state["filter_status"] = k
            rerender()
        return ft.Container(
            content=ft.Row([
                ft.Icon(icon, size=12, color=SURFACE if is_active else TEXT_SEC),
                ft.Text(label, size=11, weight="bold" if is_active else "normal",
                        color=SURFACE if is_active else TEXT_SEC),
            ], spacing=5, tight=True),
            bgcolor=ESPRESSO if is_active else CARD,
            border_radius=20, padding=ft.Padding(12, 6, 14, 6),
            border=ft.Border.all(1, ESPRESSO if is_active else BORDER),
            on_click=on_tap,
        )

    def make_range_chip(key, label):
        is_active = (state["filter_range"] == key)
        def on_tap(e, k=key):
            state["filter_range"] = k
            load_and_render()
        return ft.Container(
            content=ft.Text(label, size=11, weight="bold" if is_active else "normal",
                            color=CREAM if is_active else TEXT_SEC),
            bgcolor=TEXT_SEC if is_active else "transparent",
            border_radius=16, padding=ft.Padding(12, 6, 12, 6),
            border=ft.Border.all(1, TEXT_PRI if is_active else BORDER),
            on_click=on_tap,
        )

    def rebuild_filter_chips():
        if status_filter_row_ref.current:
            status_filter_row_ref.current.controls = [
                make_status_chip("all",       "ทั้งหมด",    ft.Icons.LIST_ROUNDED),
                make_status_chip("pending",   "รอยืนยัน",   ft.Icons.HOURGLASS_EMPTY_ROUNDED),
                make_status_chip("confirmed", "ยืนยันแล้ว",  ft.Icons.CHECK_CIRCLE_OUTLINE),
                make_status_chip("cancelled", "ยกเลิก",     ft.Icons.CANCEL_OUTLINED),
            ]
        if range_filter_row_ref.current:
            range_filter_row_ref.current.controls = [
                make_range_chip("today", "วันนี้"),
                make_range_chip("week",  "สัปดาห์นี้"),
                make_range_chip("month", "เดือนนี้"),
                make_range_chip("all",   "ทั้งหมด"),
            ]

    def rerender():
        filtered = filter_data(state["all_data"])
        if list_col.current:
            list_col.current.controls = [build_card(r) for r in filtered]
        if empty_ref.current:
            empty_ref.current.visible = (len(filtered) == 0)
        rebuild_filter_chips()
        page.update()

    # ── Stat Card ──
    def stat_card(ref, label, color, icon):
        return ft.Container(
            content=ft.Column([
                ft.Container(content=ft.Icon(icon, size=18, color=color),
                             width=40, height=40,
                             bgcolor=ft.Colors.with_opacity(0.15, color),
                             border_radius=13, alignment=ft.Alignment(0, 0)),
                ft.Container(height=6),
                ft.Text(ref=ref, value="0", size=26, weight="bold", color=color),
                ft.Text(label, size=9, color=TEXT_SEC, text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=2),
            bgcolor=CARD, border_radius=16, padding=ft.Padding(12, 16, 12, 16),
            border=ft.Border(
                top=ft.BorderSide(3, rgba(color, 0.5)),
                left=ft.BorderSide(1, BORDER),
                right=ft.BorderSide(1, BORDER),
                bottom=ft.BorderSide(1, BORDER),
            ),
            shadow=ft.BoxShadow(blur_radius=8, color=rgba(ESPRESSO, 0.07), offset=ft.Offset(0, 3)),
            expand=True,
        )

    # ── Header ──
    today_str = datetime.now().strftime("%d %b %Y")

    gold_rule = ft.Container(
        height=1, margin=ft.Margin(0, 6, 0, 0),
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
            colors=["transparent", GOLD_RICH, GOLD, "transparent"],
        ),
    )

    refresh_btn = ft.Container(
        content=ft.Icon(ft.Icons.REFRESH_ROUNDED, color=GOLD_RICH, size=20),
        width=42, height=42, bgcolor=rgba(ESPRESSO, 0.55), border_radius=21,
        alignment=ft.Alignment(0, 0), border=ft.Border.all(1, rgba(GOLD, 0.6)),
        on_click=lambda _: load_and_render(),
    )

    header_text_col = ft.Column([
        ft.Row([ft.Icon(ft.Icons.STOREFRONT_OUTLINED, size=13, color=GOLD_RICH),
                ft.Text("Restaurant", size=11, color=GOLD_RICH, weight="w600")], spacing=5),
        ft.Container(height=2),
        ft.Text("DAYLIGHT RESTAURANT", size=22, weight="bold", color=TEXT_LIGHT),
        gold_rule,
        ft.Container(height=4),
        ft.Text(today_str, size=12, color=rgba(TEXT_LIGHT, 0.75)),
    ], spacing=2)


    _pw = int(page.width) if page.width and page.width > 0 else 800

    if HERO_SRC:
        header_inner = ft.Stack([
            
            ft.Image(
                src=HERO_SRC,
                width=_pw,
                height=160,
                fit="cover",
                gapless_playback=True,
            ),
            # Dark overlay ขนาดเดียวกับรูป
            ft.Container(
                width=_pw,
                height=160,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                    colors=[rgba(ESPRESSO, 0.82), rgba(ESPRESSO, 0.65), rgba(ESPRESSO, 0.40)],
                ),
            ),
            # Text + button อยู่บนสุด
            ft.Container(
                width=_pw,
                content=ft.Row([header_text_col, refresh_btn],
                               alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.Padding(20, 52, 20, 20),
            ),
        ], width=_pw, height=160)
    else:
        # Fallback: gradient banner ถ้าไม่มีรูป
        header_inner = ft.Container(
            content=ft.Row([header_text_col, refresh_btn],
                           alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.Padding(20, 52, 20, 20),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1),
                colors=[ESPRESSO, MAHOGANY, COPPER],
            ),
        )

    header = ft.Container(
        content=header_inner,
        height=160,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        shadow=ft.BoxShadow(blur_radius=16, color=rgba(ESPRESSO, 0.25), offset=ft.Offset(0, 4)),
    )

    stats_row = ft.Container(
        content=ft.Row([
            stat_card(stat_total_ref, "ทั้งหมด",    GOLD,       ft.Icons.RECEIPT_LONG_OUTLINED),
            stat_card(stat_pend_ref,  "รอยืนยัน",   AMBER,      ft.Icons.HOURGLASS_EMPTY_ROUNDED),
            stat_card(stat_conf_ref,  "ยืนยันแล้ว",  GREEN_RICH, ft.Icons.CHECK_CIRCLE_OUTLINE),
            stat_card(stat_canc_ref,  "ยกเลิก",     RED_RICH,   ft.Icons.CANCEL_OUTLINED),
        ], spacing=8),
        padding=ft.Padding(16, 16, 16, 8),
    )

    def section_label(text):
        return ft.Container(
            content=ft.Row([
                ft.Container(width=3, height=12, bgcolor=GOLD, border_radius=2),
                ft.Text(text, size=10, color=TEXT_SEC, weight="w700"),
            ], spacing=8),
            padding=ft.Padding(16, 10, 16, 0),
        )

    loading_spinner = ft.Container(
        ref=loading_ref,
        content=ft.Row([ft.ProgressRing(width=16, height=16, stroke_width=2, color=GOLD),
                        ft.Text("กำลังโหลด...", size=12, color=TEXT_SEC)],
                       alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        visible=False, padding=ft.Padding(0, 24, 0, 8),
    )

    empty_state = ft.Container(
        ref=empty_ref, visible=False,
        content=ft.Column([
            ft.Icon(ft.Icons.INBOX_OUTLINED, size=52, color=TEXT_DIM),
            ft.Container(height=10),
            ft.Text("ไม่มีรายการจองในช่วงนี้", size=14, color=TEXT_SEC),
            ft.Text("ลองเลือกช่วงเวลาอื่น", size=11, color=TEXT_DIM),
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
        alignment=ft.Alignment(0, 0), padding=ft.Padding(0, 48, 0, 24),
    )

    reservations_list = ft.Column(ref=list_col, controls=[], spacing=10)

    page.add(
        ft.Column([
            header,
            ft.Container(
                content=ft.Column([
                    stats_row,
                    section_label("ช่วงเวลา"),
                    ft.Container(content=ft.Row(ref=range_filter_row_ref, controls=[],
                                               scroll=ft.ScrollMode.HIDDEN, spacing=8),
                                 padding=ft.Padding(16, 6, 16, 4)),
                    section_label("สถานะ"),
                    ft.Container(content=ft.Row(ref=status_filter_row_ref, controls=[],
                                               scroll=ft.ScrollMode.HIDDEN, spacing=8),
                                 padding=ft.Padding(16, 6, 16, 12)),
                    ft.Container(height=1, margin=ft.Margin(16, 0, 16, 0),
                                 gradient=ft.LinearGradient(
                                     begin=ft.Alignment(-1, 0), end=ft.Alignment(1, 0),
                                     colors=["transparent", BORDER2, "transparent"])),
                    ft.Container(height=8),
                    loading_spinner,
                    empty_state,
                    ft.Container(content=reservations_list, padding=ft.Padding(16, 0, 16, 40)),
                ], spacing=0),
                expand=True,
            ),
        ], spacing=0, scroll=ft.ScrollMode.ADAPTIVE, expand=True)
    )

    # ── resize handler: อัปเดต hero image width เมื่อ window ขนาดเปลี่ยน ──
    if HERO_SRC:
        def on_page_resize(e):
            try:
                pw = int(page.width) if page.width and page.width > 0 else 800
                # อัปเดต Image, overlay, text container ใน Stack
                stack = header.content  # the Stack
                if hasattr(stack, "controls") and len(stack.controls) >= 3:
                    stack.controls[0].width = pw   # Image
                    stack.controls[1].width = pw   # overlay
                    stack.controls[2].width = pw   # text row
                    stack.width = pw
                    header.update()
            except Exception:
                pass
        page.on_resized = on_page_resize

    load_and_render()