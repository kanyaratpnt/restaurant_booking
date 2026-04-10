import flet as ft
from login import show_login
from home import show_home
from restaurant_dashboard import show_restaurant_dashboard

def main(page: ft.Page):
    def on_login_success(page, user_info):
        print("✅ on_login_success called:", user_info)
        role = user_info.get("role", "customer")
        try:
            if role == "restaurant":
                show_restaurant_dashboard(page, user_info)
            else:
                show_home(page, user_info, on_login_success) 
        except Exception as ex:
            import traceback
            traceback.print_exc()
            page.clean()
            page.add(ft.Text(f"❌ Error: {ex}", color="red", size=14))
            page.update()

    show_login(page, on_login_success)

ft.app(target=main,
       view=ft.AppView.FLET_APP,)