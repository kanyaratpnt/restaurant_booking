import flet as ft
import requests

API_URL = "http://192.168.1.41:8000"

# ── Brown theme palette ──
BROWN_DARK   = "#4A2C0A"
BROWN_MID    = "#7B4A1E"
BROWN_LIGHT  = "#C8965A"
BROWN_PALE   = "#F5E6D3"
BROWN_CARD   = "#FDF6EE"
BROWN_BORDER = "#D4A574"
BROWN_TEXT   = "#3D1F08"
ACCENT       = "#E8B86D"

def show_login(page: ft.Page, on_success):
    page.clean()
    page.title = "เข้าสู่ระบบ"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 0
    page.bgcolor = BROWN_CARD

    error_text = ft.Text("", color="#C0392B", size=12, text_align=ft.TextAlign.CENTER)

    # ── Refs ──
    phone_ref  = ft.Ref[ft.TextField]()
    login_user = ft.Ref[ft.TextField]()
    login_pass = ft.Ref[ft.TextField]()
    reg_user   = ft.Ref[ft.TextField]()
    reg_pass   = ft.Ref[ft.TextField]()
    reg_pass2  = ft.Ref[ft.TextField]()
    rest_user  = ft.Ref[ft.TextField]()
    rest_pass  = ft.Ref[ft.TextField]()

    otp_box    = ft.Ref[ft.Container]()
    email_box  = ft.Ref[ft.Container]()
    reg_box    = ft.Ref[ft.Container]()
    rest_box   = ft.Ref[ft.Container]()

    tab_otp_ref   = ft.Ref[ft.Container]()
    tab_email_ref = ft.Ref[ft.Container]()
    tab_reg_ref   = ft.Ref[ft.Container]()

    customer_tabs_ref  = ft.Ref[ft.Container]()
    restaurant_box_ref = ft.Ref[ft.Container]()

    current_role = ft.Ref[str]()  # "customer" | "restaurant"
    current_role_val = ["customer"]

    def clear_error():
        error_text.value = ""

    # ════════════════════════════════════════════
    #  ROLE TOGGLE
    # ════════════════════════════════════════════
    role_cust_ref = ft.Ref[ft.Container]()
    role_rest_ref = ft.Ref[ft.Container]()

    def switch_role(role):
        current_role_val[0] = role
        clear_error()

        is_cust = (role == "customer")

        # ปุ่ม toggle style
        role_cust_ref.current.bgcolor  = BROWN_DARK  if is_cust  else "transparent"
        role_rest_ref.current.bgcolor  = BROWN_DARK  if not is_cust else "transparent"
        for c in role_cust_ref.current.content.controls:
            c.color = "white" if is_cust  else BROWN_MID
        for c in role_rest_ref.current.content.controls:
            c.color = "white" if not is_cust else BROWN_MID

        # แสดง / ซ่อน
        customer_tabs_ref.current.visible  = is_cust
        restaurant_box_ref.current.visible = not is_cust
        page.update()

    def make_role_btn(ref, icon, label, role, active):
        return ft.Container(
            ref=ref,
            content=ft.Row([
                ft.Icon(icon, size=15, color="white" if active else BROWN_MID),
                ft.Text(label, size=13, weight="bold",
                        color="white" if active else BROWN_MID),
            ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=BROWN_DARK if active else "transparent",
            border_radius=10,
            padding=ft.Padding(0, 10, 0, 10),
            expand=True,
            on_click=lambda e, r=role: switch_role(r),
            animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
        )

    role_toggle = ft.Container(
        content=ft.Row([
            make_role_btn(role_cust_ref, ft.Icons.PERSON_OUTLINE,
                          "ลูกค้า",      "customer",   True),
            make_role_btn(role_rest_ref, ft.Icons.STOREFRONT_OUTLINED,
                          "ร้านอาหาร",  "restaurant", False),
        ], spacing=3),
        bgcolor=BROWN_PALE,
        border_radius=12,
        padding=4,
        width=310,
        border=ft.Border.all(1, BROWN_BORDER),
    )

    # ════════════════════════════════════════════
    #  CUSTOMER TABS
    # ════════════════════════════════════════════
    def switch_tab(tab):
        clear_error()
        tabs = {
            "otp":   (tab_otp_ref,   otp_box),
            "email": (tab_email_ref, email_box),
            "reg":   (tab_reg_ref,   reg_box),
        }
        for key, (t_ref, b_ref) in tabs.items():
            is_active = (key == tab)
            t_ref.current.bgcolor = BROWN_DARK if is_active else "transparent"
            for ctrl in t_ref.current.content.controls:
                ctrl.color = "white" if is_active else BROWN_MID
            b_ref.current.visible = is_active
        page.update()

    def make_tab(ref, icon, label, key, active):
        return ft.Container(
            ref=ref,
            content=ft.Row([
                ft.Icon(icon, size=13, color="white" if active else BROWN_MID),
                ft.Text(label, size=11, weight="bold",
                        color="white" if active else BROWN_MID),
            ], spacing=4, alignment=ft.MainAxisAlignment.CENTER),
            bgcolor=BROWN_DARK if active else "transparent",
            border_radius=9,
            padding=ft.Padding(0, 8, 0, 8),
            expand=True,
            on_click=lambda e, t=key: switch_tab(t),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

    tab_bar = ft.Container(
        content=ft.Row([
            make_tab(tab_otp_ref,   ft.Icons.PHONE_ANDROID,      "OTP",    "otp",   True),
            make_tab(tab_email_ref, ft.Icons.PERSON_OUTLINE,      "Login",  "email", False),
            make_tab(tab_reg_ref,   ft.Icons.PERSON_ADD_OUTLINED, "สมัคร", "reg",   False),
        ], spacing=3),
        bgcolor=BROWN_PALE,
        border_radius=11,
        padding=3,
        width=310,
        border=ft.Border.all(1, BROWN_BORDER),
    )

    # ── Field / Button helpers ──
    def mk_field(ref, label, hint, icon, kb=ft.KeyboardType.TEXT, password=False):
        return ft.TextField(
            ref=ref, label=label, hint_text=hint,
            keyboard_type=kb, password=password, can_reveal_password=password,
            width=300, border_radius=12,
            label_style=ft.TextStyle(color=BROWN_MID),
            border_color=BROWN_BORDER,
            focused_border_color=BROWN_DARK,
            cursor_color=BROWN_DARK,
            prefix_icon=icon,
            on_change=lambda e: clear_error(),
        )

    def mk_btn(label, icon, on_click, color=None):
        bg = color or BROWN_DARK
        return ft.FilledButton(
            content=ft.Row([
                ft.Icon(icon, color="white", size=15),
                ft.Text(label, size=14, weight="bold", color="white"),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            on_click=on_click, width=300, height=48,
            style=ft.ButtonStyle(
                bgcolor=bg,
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
        )

    # ── OTP ──
    def on_send_otp(e):
        phone = phone_ref.current.value.strip()
        if len(phone) < 9:
            error_text.value = "กรุณากรอกเบอร์โทรให้ครบ"
            page.update(); return
        try:
            res = requests.post(f"{API_URL}/auth/send-otp",
                                json={"phone": phone}, timeout=5)
            if res.status_code == 200:
                from otp import show_otp
                show_otp(page, phone, on_success)
            else:
                error_text.value = "เกิดข้อผิดพลาด กรุณาลองใหม่"
                page.update()
        except Exception:
            error_text.value = "ไม่สามารถเชื่อมต่อ server"
            page.update()

    # ── Email Login ──
    def on_login(e):
        username = login_user.current.value.strip()
        password = login_pass.current.value.strip()
        if not username or not password:
            error_text.value = "กรุณากรอก Username และรหัสผ่าน"
            page.update(); return
        try:
            res = requests.post(f"{API_URL}/auth/email-login",
                                json={"email": username, "password": password}, timeout=5)
            if res.status_code == 200:
                on_success(page, res.json())
            else:
                error_text.value = res.json().get("detail", "Username หรือรหัสผ่านไม่ถูกต้อง")
                page.update()
        except Exception:
            error_text.value = "ไม่สามารถเชื่อมต่อ server"
            page.update()

    # ── Register ──
    def on_register(e):
        username = reg_user.current.value.strip()
        pw       = reg_pass.current.value.strip()
        pw2      = reg_pass2.current.value.strip()
        if not username or not pw:
            error_text.value = "กรุณากรอกข้อมูลให้ครบ"
            page.update(); return
        if len(username) < 4:
            error_text.value = "Username ต้องมีอย่างน้อย 4 ตัวอักษร"
            page.update(); return
        if pw != pw2:
            error_text.value = "รหัสผ่านไม่ตรงกัน"
            page.update(); return
        if len(pw) < 6:
            error_text.value = "รหัสผ่านต้องมีอย่างน้อย 6 ตัวอักษร"
            page.update(); return
        try:
            res = requests.post(f"{API_URL}/auth/register",
                                json={"username": username, "password": pw}, timeout=5)
            if res.status_code == 200:
                on_success(page, res.json())
            else:
                error_text.value = res.json().get("detail", "สมัครไม่สำเร็จ")
                page.update()
        except Exception:
            error_text.value = "ไม่สามารถเชื่อมต่อ server"
            page.update()

    # ── Restaurant Login ──
    def on_restaurant_login(e):
        username = rest_user.current.value.strip()
        password = rest_pass.current.value.strip()
        if not username or not password:
            error_text.value = "กรุณากรอก Username และรหัสผ่าน"
            page.update(); return
        try:
            res = requests.post(f"{API_URL}/auth/restaurant-login",
                                json={"username": username, "password": password}, timeout=5)
            if res.status_code == 200:
                on_success(page, {**res.json(), "role": "restaurant"})
            else:
                error_text.value = res.json().get("detail", "Username หรือรหัสผ่านไม่ถูกต้อง")
                page.update()
        except Exception:
            error_text.value = "ไม่สามารถเชื่อมต่อ server"
            page.update()

    # ── Forms ──
    otp_form = ft.Container(
        ref=otp_box, visible=True,
        content=ft.Column([
            mk_field(phone_ref, "เบอร์โทรศัพท์", "08x-xxx-xxxx",
                     ft.Icons.PHONE_OUTLINED, ft.KeyboardType.PHONE),
            mk_btn("รับรหัส OTP", ft.Icons.SEND_OUTLINED, on_send_otp),
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    )

    email_form = ft.Container(
        ref=email_box, visible=False,
        content=ft.Column([
            mk_field(login_user, "Username", "กรอก username ของคุณ", ft.Icons.PERSON_OUTLINE),
            mk_field(login_pass, "รหัสผ่าน", "", ft.Icons.LOCK_OUTLINE, password=True),
            mk_btn("เข้าสู่ระบบ", ft.Icons.LOGIN, on_login),
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    )

    reg_form = ft.Container(
        ref=reg_box, visible=False,
        content=ft.Column([
            mk_field(reg_user,  "Username", "ตั้งชื่อผู้ใช้ (4+ ตัว)", ft.Icons.PERSON_OUTLINE),
            mk_field(reg_pass,  "รหัสผ่าน", "อย่างน้อย 6 ตัวอักษร",
                     ft.Icons.LOCK_OUTLINE, password=True),
            mk_field(reg_pass2, "ยืนยันรหัสผ่าน", "กรอกอีกครั้ง",
                     ft.Icons.LOCK_OUTLINE, password=True),
            mk_btn("สมัครสมาชิก", ft.Icons.PERSON_ADD_OUTLINED, on_register),
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    )

    # ── Customer section (tabs + forms) ──
    customer_section = ft.Container(
        ref=customer_tabs_ref,
        visible=True,
        content=ft.Column([
            tab_bar,
            ft.Container(height=14),
            otp_form,
            email_form,
            reg_form,
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
    )

    # ── Restaurant section ──
    restaurant_section = ft.Container(
        ref=restaurant_box_ref,
        visible=False,
        content=ft.Column([
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.STOREFRONT_OUTLINED, color=BROWN_MID, size=16),
                    ft.Text("เข้าสู่ระบบสำหรับร้านอาหาร",
                            size=13, color=BROWN_MID, weight="bold"),
                ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
                bgcolor=BROWN_PALE,
                padding=ft.Padding(16, 10, 16, 10),
                border_radius=10,
                border=ft.Border.all(1, BROWN_BORDER),
                width=300,
            ),
            ft.Container(height=8),
            mk_field(rest_user, "Username", "กรอก username ร้านอาหาร",
                     ft.Icons.STOREFRONT_OUTLINED),
            mk_field(rest_pass, "รหัสผ่าน", "", ft.Icons.LOCK_OUTLINE, password=True),
            mk_btn("เข้าสู่ระบบร้านอาหาร", ft.Icons.LOGIN, on_restaurant_login,
                   color=BROWN_MID),
        ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
    )

    page.add(
        ft.Column(controls=[
            # ── Header ──
            ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Icon(ft.Icons.RESTAURANT, color=BROWN_DARK, size=32),
                        width=64, height=64,
                        bgcolor=ACCENT,
                        border_radius=32,
                        alignment=ft.Alignment(0, 0),
                        shadow=ft.BoxShadow(blur_radius=20, color="#00000040"),
                    ),
                    ft.Container(height=12),
                    ft.Text("DAYLIGHT RESTAURANT", size=26, weight="bold", color="white"),
                    ft.Text("ยินดีต้อนรับ", size=18, weight="bold", color=BROWN_PALE),
                    ft.Text("--- จองโต๊ะออนไลน์ได้ง่ายๆ ---",
                            size=12, color="#D4A07A"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0, -1),
                    end=ft.Alignment(0, 1),
                    colors=[BROWN_DARK, BROWN_MID],
                ),
                padding=ft.Padding(20, 55, 20, 30),
                border_radius=ft.BorderRadius(0, 0, 32, 32),
                shadow=ft.BoxShadow(blur_radius=16, color="#00000030"),
            ),
            # ── Body ──
            ft.Container(
                content=ft.Column([
                    ft.Container(height=20),
                    ft.Container(
                        content=ft.Column([
                            # Role toggle (อยู่บนสุด ก่อน tabs)
                            ft.Text("เลือกประเภทผู้ใช้งาน",
                                    size=12, color=BROWN_MID,
                                    weight="bold",
                                    text_align=ft.TextAlign.CENTER),
                            ft.Container(height=8),
                            role_toggle,
                            ft.Container(height=8),
                            # Customer tabs / Restaurant form
                            customer_section,
                            restaurant_section,
                            ft.Container(height=4),
                            error_text,
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0),
                        bgcolor="white",
                        border_radius=20,
                        padding=20,
                        shadow=ft.BoxShadow(blur_radius=20, color="#00000012"),
                        border=ft.Border.all(1, BROWN_BORDER + "40"),
                    ),
                    ft.Container(height=12),

                ], scroll=ft.ScrollMode.ADAPTIVE, spacing=0),
                padding=ft.Padding(20, 0, 20, 0),
                expand=True,
            ),
        ], spacing=0, expand=True)
    )
    page.update()