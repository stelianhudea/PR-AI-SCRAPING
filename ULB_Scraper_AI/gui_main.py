import flet as ft
import os
import threading
import time
import json
import shutil  # Necesar pentru ștergerea folderelor
from datetime import datetime
from src.crawler import ULBDeepScraper
from src.extractors import ULBExtractor
from src.ai_analyzer import ULBAdvancedAnalyzer

SETTINGS_FILE = "data/settings.json"

def main(page: ft.Page):
    page.title = "ULBS AI Assistant - Clean Slate Edition"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 500
    page.window_height = 900
    page.padding = 20

    # --- LOGICA DE SETĂRI ---
    def load_settings():
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        return {"url": "https://www.ulbsibiu.ro/", "interval": "24"}

    initial_settings = load_settings()
    last_saved_url = initial_settings["url"]

    # --- STATE-UL APLICAȚIEI ---
    is_scraping_active = False
    analyzer = None
    csv_path = "data/database/files_index.csv"

    # --- COMPONENTE UI ---
    chat_list = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    user_input = ft.TextField(hint_text="Întreabă ceva...", expand=True, border_radius=20)
    url_input = ft.TextField(label="URL Țintă Scraping", value=initial_settings["url"], expand=True)
    interval_input = ft.TextField(label="Interval (ore)", value=initial_settings["interval"], width=100)
    status_text = ft.Text("Auto-Scraping: Dezactivat", color=ft.colors.GREY_400)
    last_run_text = ft.Text("Ultima rulare: Niciodată", size=12, color=ft.colors.BLUE_200)

    def add_message(sender, text, is_user=False):
        bg = ft.colors.BLUE_900 if is_user else ft.colors.BLUE_GREY_900
        chat_list.controls.append(
            ft.Container(
                content=ft.Text(f"{sender}: {text}", selectable=True),
                bgcolor=bg, padding=12, border_radius=10,
                alignment=ft.alignment.center_right if is_user else ft.alignment.center_left
            )
        )
        page.update()

    def clear_all_data():
        """Șterge folderele de date pentru a preveni contaminarea între site-uri."""
        folders_to_clean = ["data/database", "data/raw", "data/database/chroma_db"]
        for folder in folders_to_clean:
            if os.path.exists(folder):
                try:
                    shutil.rmtree(folder)
                    print(f"🧹 Folder șters: {folder}")
                except Exception as e:
                    print(f"⚠️ Nu am putut șterge {folder}: {e}")
        
        # Recreăm structura de bază goală
        os.makedirs("data/database", exist_ok=True)
        os.makedirs("data/raw", exist_ok=True)

    def run_full_sync():
        try:
            target_url = url_input.value
            add_message("Sistem", f"🔄 Sincronizare nouă pentru: {target_url}")
            
            scraper = ULBDeepScraper(base_url=target_url, max_pages=150)
            scraper.run()
            
            extractor = ULBExtractor()
            extractor.process_all()
            
            nonlocal analyzer
            analyzer = ULBAdvancedAnalyzer(csv_path=csv_path)
            
            last_run_text.value = f"Ultima rulare: {datetime.now().strftime('%H:%M:%S')}"
            add_message("Sistem", "✅ Date noi indexate cu succes!")
        except Exception as e:
            add_message("Sistem", f"❌ Eroare: {e}")
        page.update()

    def scraping_timer_worker():
        nonlocal is_scraping_active
        while is_scraping_active:
            run_full_sync()
            try:
                wait_seconds = float(interval_input.value) * 3600
            except:
                wait_seconds = 3600
            
            elapsed = 0
            while elapsed < wait_seconds and is_scraping_active:
                time.sleep(10)
                elapsed += 10

    def toggle_scraping(e):
        nonlocal is_scraping_active, last_saved_url, analyzer
        
        current_url = url_input.value.strip()

        # --- LOGICA DE RESET LA SCHIMBAREA SITE-ULUI ---
        if current_url != last_saved_url:
            add_message("Sistem", "🧨 Detectat URL nou. Se șterg datele vechi...")
            clear_all_data()
            analyzer = None # Resetăm creierul AI pentru că baza de date a dispărut
            last_saved_url = current_url
        
        # Salvăm noile setări în JSON
        os.makedirs("data", exist_ok=True)
        with open(SETTINGS_FILE, "w") as f:
            json.dump({"url": current_url, "interval": interval_input.value}, f)
        
        if not is_scraping_active:
            is_scraping_active = True
            e.control.text = "STOP AUTO-SCRAPING"
            e.control.bgcolor = ft.colors.RED_700
            status_text.value = "STATUS: ACTIV"
            status_text.color = ft.colors.GREEN_400
            threading.Thread(target=scraping_timer_worker, daemon=True).start()
        else:
            is_scraping_active = False
            e.control.text = "START AUTO-SCRAPING"
            e.control.bgcolor = ft.colors.BLUE_700
            status_text.value = "STATUS: Dezactivat"
            status_text.color = ft.colors.GREY_400
        page.update()

    def send_query(e):
        if not user_input.value: return
        q = user_input.value
        add_message("Tu", q, True)
        user_input.value = ""
        
        def ai_work():
            if analyzer:
                res = analyzer.ask_about_content(q)
                add_message("AI", res)
            else:
                add_message("Sistem", "Baza de date este goală. Așteaptă prima scanare!")
        threading.Thread(target=ai_work, daemon=True).start()

    # --- UI ---
    settings_section = ft.Container(
        content=ft.Column([
            ft.Text("⚙️ CONFIGURARE SCRAPER", weight="bold"),
            url_input,
            ft.Row([interval_input, ft.Text("ore între scanări")]),
            ft.ElevatedButton("START AUTO-SCRAPING", icon=ft.icons.PLAY_ARROW, on_click=toggle_scraping),
            status_text,
            last_run_text,
        ]),
        padding=20, bgcolor=ft.colors.BLUE_GREY_900, border_radius=15
    )

    page.add(
        ft.Row([ft.Icon(ft.icons.AUTO_DELETE, color=ft.colors.RED_400), ft.Text("ULBS AI Assistant", size=22, weight="bold")]),
        ft.Divider(),
        settings_section,
        ft.Divider(),
        chat_list,
        ft.Row([user_input, ft.IconButton(ft.icons.SEND, on_click=send_query)])
    )

    if os.path.exists(csv_path):
        analyzer = ULBAdvancedAnalyzer(csv_path=csv_path)

ft.app(target=main)