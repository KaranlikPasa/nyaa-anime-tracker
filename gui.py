"""
Modern Desktop GUI for Nyaa Anime Tracker using CustomTkinter
"""
import os
import sys
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from config import config, PROJECT_DIR, get_asset_path
from tracker import tracker
from startup import is_startup_enabled, set_startup
from notifier import notifier

# Configure CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ICON_ICO = get_asset_path("icon.ico")

class AnimeTrackerApp(ctk.CTk):
    def __init__(self, start_minimized: bool = False):
        super().__init__()

        self.title("Nyaa.si Anime Çeviri Takipçisi")
        self.geometry("980x680")
        self.minsize(850, 580)
        
        # Set icon
        if os.path.exists(ICON_ICO):
            try:
                self.iconbitmap(ICON_ICO)
            except Exception as e:
                print(f"[GUI] Could not set iconbitmap: {e}")

        self.tray_manager = None
        self._is_closing = False

        # Intercept window close (X button)
        self.protocol("WM_DELETE_WINDOW", self.on_close_button_clicked)

        # Build UI layout
        self._create_header()
        self._create_tabview()
        self._create_statusbar()

        # Connect tracker callbacks
        tracker.on_status_change = self._on_tracker_status
        tracker.on_match_found = self._on_new_match
        tracker.on_check_finished = self._on_check_finished

        # Initial data population
        self.refresh_anime_list()
        self.refresh_history_list()
        self.sync_settings_ui()

        # Handle start minimized
        if start_minimized:
            self.withdraw()

    def set_tray_manager(self, tray_manager):
        self.tray_manager = tray_manager

    # ================= UI CREATION =================

    def _create_header(self):
        self.header_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#181e29")
        self.header_frame.pack(fill="x", side="top", padx=0, pady=0)

        # Title & Subtitle
        title_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        title_box.pack(side="left", padx=20, pady=12)

        self.lbl_title = ctk.CTkLabel(
            title_box,
            text="🎬 Nyaa Anime Takipçisi",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.lbl_title.pack(anchor="w")

        self.lbl_subtitle = ctk.CTkLabel(
            title_box,
            text="Çeviri Ekipleri İçin Otomatik Bölüm Yakalama Sistemi",
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        self.lbl_subtitle.pack(anchor="w")

        # Quick Control Buttons (Right side)
        btn_box = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        btn_box.pack(side="right", padx=20, pady=12)

        self.status_pill = ctk.CTkLabel(
            btn_box,
            text="🟢 Çalışıyor",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#064e3b",
            text_color="#34d399",
            corner_radius=8,
            padx=12,
            pady=6
        )
        self.status_pill.pack(side="left", padx=(0, 10))

        self.btn_check_now = ctk.CTkButton(
            btn_box,
            text="🔍 Şimdi Tara",
            width=110,
            command=self.action_check_now
        )
        self.btn_check_now.pack(side="left", padx=4)

        self.btn_pause_toggle = ctk.CTkButton(
            btn_box,
            text="⏸️ Duraklat",
            width=100,
            fg_color="#334155",
            hover_color="#475569",
            command=self.action_toggle_pause
        )
        self.btn_pause_toggle.pack(side="left", padx=4)

        self.btn_hide = ctk.CTkButton(
            btn_box,
            text="📌 Gizle (Tepsi)",
            width=105,
            fg_color="#1e293b",
            hover_color="#334155",
            command=self.hide_to_tray
        )
        self.btn_hide.pack(side="left", padx=4)

    def _create_tabview(self):
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=16, pady=(10, 5))

        self.tab_anime = self.tabview.add("📺 Takip Edilen Animeler")
        self.tab_history = self.tabview.add("🔔 Düşen Bölümler (Geçmiş)")
        self.tab_settings = self.tabview.add("⚙️ Ayarlar")

        self._build_anime_tab()
        self._build_history_tab()
        self._build_settings_tab()

    # ---------------- TAB 1: ANIME LIST ----------------

    def _build_anime_tab(self):
        # Top input card
        input_card = ctk.CTkFrame(self.tab_anime, fg_color="#1e293b", corner_radius=10)
        input_card.pack(fill="x", padx=10, pady=(10, 15))

        card_title = ctk.CTkLabel(
            input_card,
            text="➕ Yeni Anime Takibi Ekle",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        card_title.grid(row=0, column=0, columnspan=4, sticky="w", padx=16, pady=(12, 8))

        # Row 1: Anime Name & Resolution
        lbl_name = ctk.CTkLabel(input_card, text="Anime Adı:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_name.grid(row=1, column=0, sticky="w", padx=16, pady=2)

        self.entry_anime_name = ctk.CTkEntry(
            input_card,
            placeholder_text="Örn: Dandadan, Bleach, Re:Zero...",
            width=320
        )
        self.entry_anime_name.grid(row=2, column=0, sticky="ew", padx=(16, 10), pady=(0, 10))
        self.entry_anime_name.bind("<Return>", lambda event: self.action_add_anime())

        lbl_res = ctk.CTkLabel(input_card, text="Çözünürlük:", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_res.grid(row=1, column=1, sticky="w", padx=10, pady=2)

        self.combo_res = ctk.CTkComboBox(
            input_card,
            values=["Tümü", "1080p", "720p", "2160p"],
            width=110
        )
        self.combo_res.set("Tümü")
        self.combo_res.grid(row=2, column=1, sticky="w", padx=10, pady=(0, 10))

        lbl_group = ctk.CTkLabel(input_card, text="Grup (İsteğe Bağlı):", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_group.grid(row=1, column=2, sticky="w", padx=10, pady=2)

        self.entry_group = ctk.CTkEntry(
            input_card,
            placeholder_text="Örn: SubsPlease, Erai-raws...",
            width=180
        )
        self.entry_group.grid(row=2, column=2, sticky="ew", padx=10, pady=(0, 10))

        lbl_exc = ctk.CTkLabel(input_card, text="Hariç Tut (İsteğe Bağlı):", font=ctk.CTkFont(size=12, weight="bold"))
        lbl_exc.grid(row=1, column=3, sticky="w", padx=10, pady=2)

        self.entry_exclude = ctk.CTkEntry(
            input_card,
            placeholder_text="Örn: Dub, Batch",
            width=140
        )
        self.entry_exclude.grid(row=2, column=3, sticky="ew", padx=(10, 16), pady=(0, 10))

        # Add button
        self.btn_add_anime = ctk.CTkButton(
            input_card,
            text="✨ Listeye Ekle",
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            height=36,
            command=self.action_add_anime
        )
        self.btn_add_anime.grid(row=3, column=0, columnspan=4, sticky="ew", padx=16, pady=(0, 14))

        input_card.grid_columnconfigure(0, weight=3)
        input_card.grid_columnconfigure(2, weight=2)

        # Scrollable list of active anime
        list_header = ctk.CTkFrame(self.tab_anime, fg_color="transparent")
        list_header.pack(fill="x", padx=10, pady=(0, 5))

        self.lbl_anime_count = ctk.CTkLabel(
            list_header,
            text="Takip Edilen Animeler (0)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#94a3b8"
        )
        self.lbl_anime_count.pack(side="left")

        self.scroll_anime = ctk.CTkScrollableFrame(self.tab_anime, corner_radius=10)
        self.scroll_anime.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_anime_list(self):
        # Clear existing widgets in scroll frame
        for widget in self.scroll_anime.winfo_children():
            widget.destroy()

        anime_list = config.tracked_anime
        self.lbl_anime_count.configure(text=f"Takip Edilen Animeler ({len(anime_list)})")

        if not anime_list:
            empty_lbl = ctk.CTkLabel(
                self.scroll_anime,
                text="ℹ️ Listenizde henüz anime yok.\nYukarıdaki formdan çevirisini yaptığınız anime adını ekleyin.",
                font=ctk.CTkFont(size=13),
                text_color="#64748b"
            )
            empty_lbl.pack(pady=40)
            return

        for anime in anime_list:
            self._render_anime_card(anime)

    def _render_anime_card(self, anime: dict):
        anime_id = anime["id"]
        is_enabled = anime.get("enabled", True)

        card = ctk.CTkFrame(self.scroll_anime, fg_color="#1e293b", corner_radius=8)
        card.pack(fill="x", pady=5, padx=2)

        # Left Info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=14, pady=10)

        name_lbl = ctk.CTkLabel(
            info_frame,
            text=anime["name"],
            font=ctk.CTkFont(size=15, weight="bold")
        )
        name_lbl.pack(anchor="w")

        # Tags frame
        tags_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        tags_frame.pack(anchor="w", pady=(4, 0))

        # Resolution badge
        res = anime.get("resolution", "Tümü")
        res_tag = ctk.CTkLabel(
            tags_frame,
            text=f"📺 {res}",
            font=ctk.CTkFont(size=11),
            fg_color="#0f172a",
            corner_radius=6,
            padx=8,
            pady=2
        )
        res_tag.pack(side="left", padx=(0, 6))

        # Group badge
        if anime.get("group"):
            grp_tag = ctk.CTkLabel(
                tags_frame,
                text=f"🏷️ Grup: {anime['group']}",
                font=ctk.CTkFont(size=11),
                fg_color="#0f172a",
                corner_radius=6,
                padx=8,
                pady=2
            )
            grp_tag.pack(side="left", padx=(0, 6))

        # Exclude badge
        if anime.get("exclude"):
            exc_tag = ctk.CTkLabel(
                tags_frame,
                text=f"🚫 Hariç: {anime['exclude']}",
                font=ctk.CTkFont(size=11),
                fg_color="#3f1c1c",
                text_color="#fca5a5",
                corner_radius=6,
                padx=8,
                pady=2
            )
            exc_tag.pack(side="left", padx=(0, 6))

        # Right Controls
        ctrl_frame = ctk.CTkFrame(card, fg_color="transparent")
        ctrl_frame.pack(side="right", padx=14, pady=10)

        # Toggle Switch
        switch = ctk.CTkSwitch(
            ctrl_frame,
            text="Aktif" if is_enabled else "Pasif",
            command=lambda aid=anime_id, s=None: self.action_toggle_anime(aid),
            font=ctk.CTkFont(size=12)
        )
        if is_enabled:
            switch.select()
        else:
            switch.deselect()
        switch.configure(command=lambda aid=anime_id, sw=switch: self._on_switch_change(aid, sw))
        switch.pack(side="left", padx=10)

        # Search Now Button
        btn_search = ctk.CTkButton(
            ctrl_frame,
            text="🔍 Nyaa'da Ara",
            width=100,
            height=28,
            fg_color="#0284c7",
            hover_color="#0369a1",
            command=lambda a=anime: self.action_search_specific_anime(a)
        )
        btn_search.pack(side="left", padx=6)

        # Delete Button
        btn_del = ctk.CTkButton(
            ctrl_frame,
            text="🗑️ Sil",
            width=65,
            height=28,
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=lambda aid=anime_id: self.action_delete_anime(aid)
        )
        btn_del.pack(side="left", padx=6)

    def _on_switch_change(self, anime_id: str, switch_widget):
        new_val = bool(switch_widget.get())
        switch_widget.configure(text="Aktif" if new_val else "Pasif")
        config.toggle_anime(anime_id, new_val)
        self._update_status_bar()

    # ---------------- TAB 2: HISTORY ----------------

    def _build_history_tab(self):
        top_bar = ctk.CTkFrame(self.tab_history, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=(10, 5))

        self.lbl_history_count = ctk.CTkLabel(
            top_bar,
            text="Yakalanan Bölümler (0)",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.lbl_history_count.pack(side="left")

        btn_nyaa_home = ctk.CTkButton(
            top_bar,
            text="🌐 Nyaa.si Aç",
            width=100,
            height=30,
            fg_color="#334155",
            hover_color="#475569",
            command=lambda: webbrowser.open("https://nyaa.si/?c=1_2")
        )
        btn_nyaa_home.pack(side="right", padx=(6, 0))

        btn_clear = ctk.CTkButton(
            top_bar,
            text="🗑️ Geçmişi Temizle",
            width=120,
            height=30,
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            command=self.action_clear_history
        )
        btn_clear.pack(side="right", padx=6)

        self.scroll_history = ctk.CTkScrollableFrame(self.tab_history, corner_radius=10)
        self.scroll_history.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    def refresh_history_list(self):
        for widget in self.scroll_history.winfo_children():
            widget.destroy()

        history = config.history
        self.lbl_history_count.configure(text=f"Yakalanan Bölümler ({len(history)})")

        if not history:
            empty_lbl = ctk.CTkLabel(
                self.scroll_history,
                text="🔔 Henüz yakalanan bir bölüm yok.\nNyaa'ya yeni bölümler düştükçe burada listelenecek ve bildirim gelecektir.",
                font=ctk.CTkFont(size=13),
                text_color="#64748b"
            )
            empty_lbl.pack(pady=40)
            return

        for item in history:
            self._render_history_card(item)

    def _render_history_card(self, item: dict):
        card = ctk.CTkFrame(self.scroll_history, fg_color="#1e293b", corner_radius=8)
        card.pack(fill="x", pady=4, padx=2)

        # Top row: Anime Tag, Release Title, Detected At
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=12, pady=(10, 2))

        anime_tag = ctk.CTkLabel(
            top_row,
            text=item.get("anime_name", "Anime"),
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#2563eb",
            text_color="#ffffff",
            corner_radius=6,
            padx=8,
            pady=2
        )
        anime_tag.pack(side="left", padx=(0, 8))

        date_str = item.get("detected_at", "")
        if date_str:
            date_lbl = ctk.CTkLabel(
                top_row,
                text=f"🕒 {date_str}",
                font=ctk.CTkFont(size=11),
                text_color="#94a3b8"
            )
            date_lbl.pack(side="right")

        # Title
        title_box = ctk.CTkFrame(card, fg_color="transparent")
        title_box.pack(fill="x", padx=12, pady=(2, 6))

        title_lbl = ctk.CTkLabel(
            title_box,
            text=item.get("title", ""),
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            justify="left",
            wraplength=620
        )
        title_lbl.pack(side="left", fill="x", expand=True)

        # Bottom row: Meta & Action buttons
        bottom_row = ctk.CTkFrame(card, fg_color="transparent")
        bottom_row.pack(fill="x", padx=12, pady=(0, 10))

        details = []
        if item.get("size"):
            details.append(f"📦 {item['size']}")
        if item.get("seeders"):
            details.append(f"🌱 {item['seeders']} seed")
        details_txt = "  |  ".join(details)

        meta_lbl = ctk.CTkLabel(
            bottom_row,
            text=details_txt,
            font=ctk.CTkFont(size=11),
            text_color="#cbd5e1"
        )
        meta_lbl.pack(side="left")

        # Buttons on right
        btn_box = ctk.CTkFrame(bottom_row, fg_color="transparent")
        btn_box.pack(side="right")

        guid = item.get("guid", "")
        link = item.get("link", "")
        magnet = item.get("magnet", "")

        if magnet:
            btn_mag = ctk.CTkButton(
                btn_box,
                text="🧲 Magnet Kopyala",
                width=110,
                height=26,
                fg_color="#475569",
                hover_color="#64748b",
                font=ctk.CTkFont(size=11),
                command=lambda m=magnet: self.copy_magnet_to_clipboard(m)
            )
            btn_mag.pack(side="left", padx=3)

        if link:
            btn_dl = ctk.CTkButton(
                btn_box,
                text="📥 Torrent İndir",
                width=100,
                height=26,
                fg_color="#059669",
                hover_color="#047857",
                font=ctk.CTkFont(size=11),
                command=lambda l=link: webbrowser.open(l)
            )
            btn_dl.pack(side="left", padx=3)

        if guid:
            btn_open = ctk.CTkButton(
                btn_box,
                text="🌐 Nyaa'da Aç",
                width=95,
                height=26,
                fg_color="#2563eb",
                hover_color="#1d4ed8",
                font=ctk.CTkFont(size=11),
                command=lambda g=guid: webbrowser.open(g)
            )
            btn_open.pack(side="left", padx=3)

    def copy_magnet_to_clipboard(self, magnet_link: str):
        self.clipboard_clear()
        self.clipboard_append(magnet_link)
        self.status_bar_lbl.configure(text="✅ Magnet linki panoya kopyalandı!")
        self.after(2500, self._update_status_bar)

    # ---------------- TAB 3: SETTINGS ----------------

    def _build_settings_tab(self):
        settings_frame = ctk.CTkScrollableFrame(self.tab_settings, corner_radius=10)
        settings_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Section 1: Background & Startup
        sec1 = ctk.CTkFrame(settings_frame, fg_color="#1e293b", corner_radius=8)
        sec1.pack(fill="x", pady=6, padx=5)

        s1_title = ctk.CTkLabel(sec1, text="🖥️ Başlangıç ve Arka Plan", font=ctk.CTkFont(size=14, weight="bold"))
        s1_title.pack(anchor="w", padx=16, pady=(12, 6))

        self.sw_startup = ctk.CTkSwitch(
            sec1,
            text="Bilgisayar açıldığında otomatik başlasın (Windows Başlangıç)",
            font=ctk.CTkFont(size=13),
            command=self._on_setting_startup_change
        )
        self.sw_startup.pack(anchor="w", padx=16, pady=6)

        self.sw_close_tray = ctk.CTkSwitch(
            sec1,
            text="Pencere kapatıldığında (X) arka planda / sistem tepsisinde çalışmaya devam et",
            font=ctk.CTkFont(size=13),
            command=lambda: config.set_setting("close_to_tray", bool(self.sw_close_tray.get()))
        )
        self.sw_close_tray.pack(anchor="w", padx=16, pady=(6, 14))

        # Section 2: Scanning & Filters
        sec2 = ctk.CTkFrame(settings_frame, fg_color="#1e293b", corner_radius=8)
        sec2.pack(fill="x", pady=6, padx=5)

        s2_title = ctk.CTkLabel(sec2, text="🌐 Nyaa Filtreleri ve Tarama Sıklığı", font=ctk.CTkFont(size=14, weight="bold"))
        s2_title.pack(anchor="w", padx=16, pady=(12, 6))

        self.sw_english_only = ctk.CTkSwitch(
            sec2,
            text="Sadece İngilizce Çevirileri Takip Et (c=1_2 Anime - English-translated)",
            font=ctk.CTkFont(size=13),
            command=lambda: config.set_setting("english_only", bool(self.sw_english_only.get()))
        )
        self.sw_english_only.pack(anchor="w", padx=16, pady=6)

        interval_box = ctk.CTkFrame(sec2, fg_color="transparent")
        interval_box.pack(anchor="w", padx=16, pady=6)

        lbl_int = ctk.CTkLabel(interval_box, text="Kontrol Sıklığı:", font=ctk.CTkFont(size=13))
        lbl_int.pack(side="left", padx=(0, 10))

        self.combo_interval = ctk.CTkComboBox(
            interval_box,
            values=["30 saniye", "60 saniye (1 dk)", "120 saniye (2 dk)", "300 saniye (5 dk)"],
            command=self._on_interval_change,
            width=180
        )
        self.combo_interval.pack(side="left")

        # Notification Sound
        self.sw_sound = ctk.CTkSwitch(
            sec2,
            text="Bölüm düştüğünde bildirim sesi çal",
            font=ctk.CTkFont(size=13),
            command=lambda: config.set_setting("play_sound", bool(self.sw_sound.get()))
        )
        self.sw_sound.pack(anchor="w", padx=16, pady=(8, 14))

        # Section 3: Diagnostic & Actions
        sec3 = ctk.CTkFrame(settings_frame, fg_color="#1e293b", corner_radius=8)
        sec3.pack(fill="x", pady=6, padx=5)

        s3_title = ctk.CTkLabel(sec3, text="🧪 Test ve Sistem Araçları", font=ctk.CTkFont(size=14, weight="bold"))
        s3_title.pack(anchor="w", padx=16, pady=(12, 6))

        btn_row = ctk.CTkFrame(sec3, fg_color="transparent")
        btn_row.pack(anchor="w", padx=16, pady=(6, 14))

        btn_test_notify = ctk.CTkButton(
            btn_row,
            text="🔔 Test Bildirimi Gönder",
            fg_color="#0284c7",
            hover_color="#0369a1",
            command=self.action_test_notification
        )
        btn_test_notify.pack(side="left", padx=(0, 10))

        btn_open_folder = ctk.CTkButton(
            btn_row,
            text="📁 Veri Klasörünü Aç",
            fg_color="#334155",
            hover_color="#475569",
            command=lambda: os.startfile(PROJECT_DIR)
        )
        btn_open_folder.pack(side="left")

        # About Fansub Hint
        about_box = ctk.CTkFrame(settings_frame, fg_color="#0f172a", corner_radius=8)
        about_box.pack(fill="x", pady=10, padx=5)

        about_text = (
            "💡 Çeviri Ekipleri (Fansub) İçin Tavsiye:\n"
            "• Sadece İngilizce Çeviriler seçeneği açıkken SubsPlease, Erai-raws gibi grupların paylaştığı "
            "tüm İngilizce bölümler anında tespit edilir.\n"
            "• Bildirim geldiğinde 'Nyaa'da Aç' veya 'Torrent İndir' butonuna tıklayarak doğrudan çeviri dosyalarına ulaşabilirsiniz.\n"
            "• Bilgisayar açılışına eklediğinizde sistem arka planda sessizce çalışır ve ram tüketimi neredeyse sıfırdır."
        )
        about_lbl = ctk.CTkLabel(
            about_box,
            text=about_text,
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8",
            justify="left",
            wraplength=850
        )
        about_lbl.pack(padx=16, pady=12, anchor="w")

    def sync_settings_ui(self):
        # Startup
        in_reg = is_startup_enabled()
        if in_reg:
            self.sw_startup.select()
        else:
            self.sw_startup.deselect()

        # Close to tray
        if config.get_setting("close_to_tray", True):
            self.sw_close_tray.select()
        else:
            self.sw_close_tray.deselect()

        # English only
        if config.get_setting("english_only", True):
            self.sw_english_only.select()
        else:
            self.sw_english_only.deselect()

        # Play sound
        if config.get_setting("play_sound", True):
            self.sw_sound.select()
        else:
            self.sw_sound.deselect()

        # Interval
        cur_interval = config.get_setting("check_interval", 60)
        mapping = {
            30: "30 saniye",
            60: "60 saniye (1 dk)",
            120: "120 saniye (2 dk)",
            300: "300 saniye (5 dk)"
        }
        self.combo_interval.set(mapping.get(cur_interval, "60 saniye (1 dk)"))

    def _on_setting_startup_change(self):
        enable = bool(self.sw_startup.get())
        success = set_startup(enable, start_minimized=True)
        if success:
            config.set_setting("start_with_windows", enable)
            status_text = "açılışına eklendi." if enable else "açılışından kaldırıldı."
            self.status_bar_lbl.configure(text=f"✅ Windows {status_text}")
        else:
            messagebox.showerror("Hata", "Windows başlangıç ayarı güncellenirken hata oluştu.")
            self.sync_settings_ui()

    def _on_interval_change(self, choice: str):
        sec = 60
        if "30" in choice:
            sec = 30
        elif "120" in choice:
            sec = 120
        elif "300" in choice:
            sec = 300
        config.set_setting("check_interval", sec)

    # ---------------- STATUS BAR ----------------

    def _create_statusbar(self):
        self.statusbar = ctk.CTkFrame(self, height=28, corner_radius=0, fg_color="#0f172a")
        self.statusbar.pack(fill="x", side="bottom")

        self.status_bar_lbl = ctk.CTkLabel(
            self.statusbar,
            text="Hazır | Tracker başlatılıyor...",
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )
        self.status_bar_lbl.pack(side="left", padx=16)

        self.status_stats_lbl = ctk.CTkLabel(
            self.statusbar,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        )
        self.status_stats_lbl.pack(side="right", padx=16)

    def _update_status_bar(self):
        active_count = len([a for a in config.tracked_anime if a.get("enabled", True)])
        total_anime = len(config.tracked_anime)
        history_count = len(config.history)
        self.status_stats_lbl.configure(
            text=f"Takip: {active_count}/{total_anime} Aktif  |  Toplam Bölüm: {history_count}"
        )

    # ================= ACTIONS & EVENT HANDLERS =================

    def action_add_anime(self):
        name = self.entry_anime_name.get().strip()
        if not name:
            messagebox.showwarning("Eksik Bilgi", "Lütfen bir anime adı girin!")
            return

        res = self.combo_res.get()
        group = self.entry_group.get().strip()
        exclude = self.entry_exclude.get().strip()

        item = config.add_anime(name=name, resolution=res, group=group, exclude=exclude)
        if not item:
            messagebox.showinfo("Bilgi", f"'{name}' zaten takip listenizde mevcut.")
            return

        # Clear inputs
        self.entry_anime_name.delete(0, "end")
        self.entry_group.delete(0, "end")
        self.entry_exclude.delete(0, "end")
        self.combo_res.set("Tümü")

        self.refresh_anime_list()
        self._update_status_bar()

        # Trigger tracker check now
        tracker.trigger_check_now()

    def action_delete_anime(self, anime_id: str):
        config.remove_anime(anime_id)
        self.refresh_anime_list()
        self._update_status_bar()

    def action_search_specific_anime(self, anime_rule: dict):
        anime_name = anime_rule.get("name", "")
        self.status_bar_lbl.configure(text=f"🔍 '{anime_name}' için Nyaa taranıyor...")

        def _do_search():
            matches = tracker.search_recent_for_anime(anime_rule)
            for m in reversed(matches):
                config.add_history_entry(m)

            def _update_ui():
                self.refresh_history_list()
                self._update_status_bar()
                if matches:
                    messagebox.showinfo("Arama Sonucu", f"'{anime_name}' için son {len(matches)} bölüm bulundu ve Geçmiş sekmesine eklendi.")
                    self.tabview.set("🔔 Düşen Bölümler (Geçmiş)")
                else:
                    messagebox.showinfo("Arama Sonucu", f"'{anime_name}' için filtrelere uygun bölüm bulunamadı.")
                self.status_bar_lbl.configure(text="Tarama tamamlandı.")

            self.after(0, _update_ui)

        import threading
        threading.Thread(target=_do_search, daemon=True).start()

    def action_check_now(self):
        self.status_bar_lbl.configure(text="🔍 Nyaa şimdi taranıyor...")
        tracker.trigger_check_now()

    def action_toggle_pause(self):
        if tracker.is_paused:
            tracker.resume()
            self.btn_pause_toggle.configure(text="⏸️ Duraklat")
            self.status_pill.configure(
                text="🟢 Çalışıyor",
                fg_color="#064e3b",
                text_color="#34d399"
            )
        else:
            tracker.pause()
            self.btn_pause_toggle.configure(text="▶️ Devam Et")
            self.status_pill.configure(
                text="🟡 Duraklatıldı",
                fg_color="#451a03",
                text_color="#fcd34d"
            )

    def action_clear_history(self):
        if not config.history:
            return
        if messagebox.askyesno("Onay", "Geçmişteki tüm bölümleri silmek istediğinizden emin misiniz?"):
            config.clear_history()
            self.refresh_history_list()
            self._update_status_bar()

    def action_test_notification(self):
        play_sound = bool(self.sw_sound.get())
        notifier.test_notification(play_sound=play_sound)
        self.status_bar_lbl.configure(text="✅ Test bildirimi gönderildi.")

    def hide_to_tray(self):
        """Hides the window to system tray."""
        self.withdraw()
        if self.tray_manager:
            self.tray_manager.notify(
                "Nyaa Takipçisi arka planda çalışmaya devam ediyor.",
                "Sistem Tepsisine Küçültüldü"
            )

    def show_from_tray(self):
        """Restores the window from system tray."""
        self.deiconify()
        self.lift()
        self.focus_force()

    def on_close_button_clicked(self):
        """Triggered when the user clicks the 'X' button of the window."""
        close_to_tray = config.get_setting("close_to_tray", True)
        if close_to_tray and self.tray_manager:
            self.hide_to_tray()
        else:
            self.full_exit()

    def full_exit(self):
        """Completely exits the app."""
        if self._is_closing:
            return
        self._is_closing = True
        tracker.stop()
        if self.tray_manager:
            self.tray_manager.stop()
        self.destroy()
        sys.exit(0)

    # ================= TRACKER CALLBACKS =================

    def _on_tracker_status(self, status: str):
        def _apply():
            if not self._is_closing:
                self.status_bar_lbl.configure(text=status)
                self._update_status_bar()
        self.after(0, _apply)

    def _on_new_match(self, item: dict):
        def _apply():
            if not self._is_closing:
                self.refresh_history_list()
                self._update_status_bar()
        self.after(0, _apply)

    def _on_check_finished(self, check_time: datetime, new_count: int):
        def _apply():
            if not self._is_closing:
                time_str = check_time.strftime("%H:%M:%S")
                msg = f"Son Kontrol: {time_str}"
                if new_count > 0:
                    msg += f" (🎉 {new_count} yeni bölüm yakalandı!)"
                self.status_bar_lbl.configure(text=msg)
                self._update_status_bar()
        self.after(0, _apply)
