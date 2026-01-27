import sys
import os
import json
import subprocess
import threading
import time
import hashlib
import urllib.request
import ssl
from datetime import datetime

# --- Setup Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

try:
    import sdl2
    import sdl2.ext
    import sdl2.sdlttf as ttf
    from sdl2 import *
    try:
        import sdl2.sdlimage as sdlimage
        SDL_IMAGE_AVAILABLE = True
    except ImportError:
        SDL_IMAGE_AVAILABLE = False
except ImportError as e:
    print(f"SDL2 Error: {e}")
    sys.exit(1)

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 480
ssl._create_default_https_context = ssl._create_unverified_context

class Colors:
    BG_PRIMARY = (15, 15, 15)
    BG_SECONDARY = (25, 25, 25)
    BG_TERTIARY = (35, 35, 35)
    YT_RED = (255, 0, 0)
    TEXT_PRIMARY = (255, 255, 255)
    TEXT_SECONDARY = (170, 170, 170)
    TEXT_TERTIARY = (100, 100, 100)
    CARD_BG = (30, 30, 30)
    CARD_SELECTED = (50, 50, 50)
    NAV_BG = (20, 20, 20)
    NAV_ACTIVE = (255, 255, 255)
    NAV_INACTIVE = (100, 100, 100)
    STATUS_LOADING = (255, 204, 0)
    STATUS_ERROR = (255, 70, 70)
    STATUS_SUCCESS = (70, 255, 70)
    DIVIDER = (50, 50, 50)
    THUMB_BG = (40, 40, 40)
    PROGRESS_BG = (60, 60, 60)

# Translations
TRANSLATIONS = {
    "English": {
        "nav_home": "Home", "nav_search": "Search", "nav_favorites": "Favs",
        "nav_history": "History", "nav_settings": "Settings", "settings_title": "Settings",
        "settings_language": "Language", "settings_quality": "Video Quality",
        "settings_search_count": "Search Count", "settings_auto_load": "Auto Load Home",
        "settings_clear_favorites": "Clear Favorites", "settings_clear_history": "Clear History",
        "settings_clear_cache": "Clear Thumb Cache", "settings_execute": "[A] Execute",
        "settings_on": "On", "settings_off": "Off", "msg_searching": "Searching videos...",
        "msg_loading": "Loading...", "msg_loading_video": "Loading Video...",
        "msg_loading_videos": "Loading videos...", "msg_no_results": "No results",
        "msg_press_search": "Press X to search", "msg_no_ytdlp": "yt-dlp not found!",
        "msg_no_player": "No video player!", "msg_install_ytdlp": "Install: pip install yt-dlp",
        "msg_install_player": "Install: mpv or ffplay", "msg_timeout": "Timeout",
        "msg_added_fav": "Added to favorites", "msg_removed_fav": "Removed from favorites",
        "msg_fav_cleared": "Favorites cleared", "msg_history_cleared": "History cleared",
        "msg_cache_cleared": "Cache cleared", "msg_videos": "videos",
        "help_keyboard": "A:Type  B:Close  START:Search",
        "help_main": "A:Select  B:Back  X:Search  Y:Fav  L/R:Tab",
        "kb_space": "SPACE", "kb_go": "GO", "kb_search_placeholder": "Type to search...",
        "time_today": "Today", "time_live": "LIVE",
        "exit_confirm_title": "Are you sure you want to exit?", "exit_confirm_yes": "Yes",
        "exit_confirm_no": "No", "exit_confirm_help": "[<>] Select [A] Confirm [B] Cancel",
    },
    # Other languages omitted for brevity (they default to English if missing)
}

LANGUAGES = ["English", "Turkce", "Espanol", "Portugues", "Deutsch", "Francais", "Russian", "Ukrainian"]
NAV_HOME, NAV_SEARCH, NAV_FAVORITES, NAV_HISTORY, NAV_SETTINGS = 0, 1, 2, 3, 4

def find_ytdlp():
    paths = [os.path.join(SCRIPT_DIR, "yt-dlp"), os.path.expanduser("~/.local/bin/yt-dlp")]
    for p in paths:
        if os.path.exists(p):
            try: os.chmod(p, 0o755)
            except: pass
            return p
    return None

def find_video_player():
    players = ["mpv", "ffplay", "vlc", "mplayer"]
    for player in players:
        try:
            result = subprocess.run(["which", player], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip(): return player
        except: continue
    pm_ffplay = "/opt/system/Tools/PortMaster/libs/ffplay"
    if os.path.exists(pm_ffplay): return pm_ffplay
    return None

YTDLP_PATH = find_ytdlp()
VIDEO_PLAYER = find_video_player()

class VideoItem:
    def __init__(self, data=None):
        if data:
            self.id = data.get('id', '')
            self.title = data.get('title', 'Unknown')
            self.channel = data.get('channel', data.get('uploader', 'Unknown'))
            self.duration = data.get('duration', 0)
            self.views = data.get('view_count', 0)
            self.upload_date = data.get('upload_date', '')
            self.url = data.get('webpage_url', data.get('url', f'https://www.youtube.com/watch?v={self.id}'))
            self.thumbnail = ''
            if data.get('thumbnail'): self.thumbnail = data.get('thumbnail')
            elif data.get('thumbnails'):
                thumbs = data.get('thumbnails', [])
                if thumbs:
                    for t in thumbs:
                        if t.get('url'):
                            self.thumbnail = t.get('url')
                            break
            if not self.thumbnail and self.id:
                self.thumbnail = f"https://i.ytimg.com/vi/{self.id}/mqdefault.jpg"
        else:
            self.id = self.title = self.channel = self.thumbnail = self.upload_date = self.url = ''
            self.duration = self.views = 0

    def format_duration(self):
        if not self.duration: return "LIVE"
        mins, secs = divmod(int(self.duration), 60)
        hours, mins = divmod(mins, 60)
        return f"{hours}:{mins:02d}:{secs:02d}" if hours else f"{mins}:{secs:02d}"

    def format_views(self):
        if not self.views: return ""
        if self.views >= 1000000: return f"{self.views/1000000:.1f}M"
        if self.views >= 1000: return f"{self.views/1000:.1f}K"
        return str(self.views)

    def format_date(self):
        if not self.upload_date: return ""
        try:
            date = datetime.strptime(self.upload_date, "%Y%m%d")
            delta = datetime.now() - date
            if delta.days < 1: return "Today"
            if delta.days < 7: return f"{delta.days}d"
            if delta.days < 30: return f"{delta.days // 7}w"
            if delta.days < 365: return f"{delta.days // 30}mo"
            return f"{delta.days // 365}y"
        except: return ""

    def to_dict(self):
        return {'id': self.id, 'title': self.title, 'channel': self.channel, 'duration': self.duration,
                'view_count': self.views, 'thumbnail': self.thumbnail, 'upload_date': self.upload_date, 'url': self.url}

class YouTubeApp:
    def __init__(self):
        SDL_Init(SDL_INIT_VIDEO | SDL_INIT_JOYSTICK | SDL_INIT_GAMECONTROLLER)
        ttf.TTF_Init()
        self.window = SDL_CreateWindow(b"YouTube", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, SCREEN_WIDTH, SCREEN_HEIGHT, SDL_WINDOW_SHOWN)
        self.renderer = SDL_CreateRenderer(self.window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC)
        SDL_SetRenderDrawBlendMode(self.renderer, SDL_BLENDMODE_BLEND)
        
        self.controller = None
        self.joystick = None
        if SDL_NumJoysticks() > 0:
            if SDL_IsGameController(0):
                self.controller = SDL_GameControllerOpen(0)
                print("Controller Detected: Using Mapped Inputs")
            else:
                self.joystick = SDL_JoystickOpen(0)
                print("Joystick Detected: Using Raw Inputs")
        
        font_path = self._find_font()
        self.font = self.font_large = self.font_small = self.font_tiny = None
        if font_path:
            self.font = ttf.TTF_OpenFont(font_path.encode(), 18)
            self.font_large = ttf.TTF_OpenFont(font_path.encode(), 24)
            self.font_small = ttf.TTF_OpenFont(font_path.encode(), 14)
            self.font_tiny = ttf.TTF_OpenFont(font_path.encode(), 12)
        
        self.text_cache = {}
        self.image_cache = {}
        self.failed_images = set()
        self.loading_images = set()
        self.image_cache_dir = os.path.join(SCRIPT_DIR, ".thumb_cache")
        os.makedirs(self.image_cache_dir, exist_ok=True)
        
        if SDL_IMAGE_AVAILABLE:
            try: sdlimage.IMG_Init(sdlimage.IMG_INIT_JPG | sdlimage.IMG_INIT_PNG)
            except: pass
            
        self.running = True
        self.need_redraw = True
        self.frame_count = 0
        self.current_nav = NAV_HOME
        self.selected = 0
        self.scroll = 0
        self.ytdlp_path = YTDLP_PATH
        self.video_player = VIDEO_PLAYER
        
        self.home_videos = []
        self.search_results = []
        self.favorites = self._load_json("yt_favorites.json")
        self.history = self._load_json("yt_history.json")
        self.last_search_query = ""
        self.home_page = self.search_page = 0
        self.max_videos = 50
        
        self.home_batch = 1
        self.search_batch = 1
        self.home_batch_loading = False
        self.search_batch_loading = False
        self.home_first_batch_count = 0
        self.search_first_batch_count = 0
        self.home_existing_ids = set()
        self.search_existing_ids = set()
        
        self.settings = self._load_settings()
        self._update_settings_items()
        self.settings_selected = 0
        self.settings_scroll = 0
        
        status_parts = []
        status_parts.append("yt-dlp OK" if self.ytdlp_path else "NO yt-dlp!")
        status_parts.append(f"Player: {os.path.basename(self.video_player)}" if self.video_player else "NO player!")
        self.status = " | ".join(status_parts)
        self.status_type = "ok" if self.ytdlp_path else "error"
        self.is_loading = False
        
        self.search_active = False
        self.search_query = ""
        self.keyboard_row = self.keyboard_col = 0
        self.caps_lock = False
        self.alphabet_mode = 'Cyrillic'
        self.keyboard_layout = self._get_keyboard_layout()
        
        self.exit_confirm_active = False
        self.exit_confirm_selection = 0
        self.key_held = None
        self.key_hold_start = 0
        self.last_repeat = 0
        
        self.is_playing = False
        self.is_loading_video = False
        self.is_searching = False
        self.player_process = None
        self.current_video = None
        self.player_paused = False
        self.mpv_socket = None
        self.loading_spinner_triggered = False

    def _find_font(self):
        paths = [
            os.path.join(SCRIPT_DIR, "font.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/opt/system/Tools/PortMaster/themes/default.ttf",
        ]
        for p in paths:
            if os.path.exists(p): return p
        return None

    def _load_json(self, filename):
        try:
            path = os.path.join(SCRIPT_DIR, filename)
            if os.path.exists(path):
                with open(path) as f: return [VideoItem(v) for v in json.load(f)]
        except: pass
        return []

    def _save_json(self, filename, items):
        try:
            path = os.path.join(SCRIPT_DIR, filename)
            with open(path, 'w') as f: json.dump([v.to_dict() for v in items[:50]], f)
        except: pass

    def _load_settings(self):
        try:
            path = os.path.join(SCRIPT_DIR, "yt_settings.json")
            if os.path.exists(path):
                with open(path) as f: return json.load(f)
        except: pass
        return {"quality": "480p", "search_count": "10", "auto_load": "On", "language": "English"}

    def _save_settings(self):
        try:
            path = os.path.join(SCRIPT_DIR, "yt_settings.json")
            with open(path, 'w') as f: json.dump(self.settings, f)
        except: pass

    def t(self, key):
        lang = self.settings.get("language", "English")
        if lang in TRANSLATIONS and key in TRANSLATIONS[lang]: return TRANSLATIONS[lang][key]
        return TRANSLATIONS["English"].get(key, key)

    def _update_settings_items(self):
        lang = self.settings.get("language", "English")
        tr = TRANSLATIONS.get(lang, TRANSLATIONS["English"])
        on_off = [tr["settings_on"], tr["settings_off"]]
        self.settings_items = [
            (tr["settings_language"], "language", LANGUAGES),
            (tr["settings_quality"], "quality", ["360p", "480p", "720p"]),
            (tr["settings_search_count"], "search_count", ["10", "15", "20", "25"]),
            (tr["settings_auto_load"], "auto_load", on_off),
            (tr["settings_clear_favorites"], "clear_favorites", None),
            (tr["settings_clear_history"], "clear_history", None),
            (tr["settings_clear_cache"], "clear_cache", None),
        ]

    def _get_keyboard_layout(self):
        lang = self.settings.get("language", "English")
        if lang in ["Ukrainian", "Russian"]:
            alphabet_mode = getattr(self, 'alphabet_mode', 'Cyrillic')
            if lang == "Ukrainian":
                return [list("1234567890"), list("йцукенгшщзхї"), list("фівапролджєґ"), list("ячсмитьбюъ")] if alphabet_mode == 'Cyrillic' else [list("1234567890"), list("qwertyuiop"), list("asdfghjkl"), list("zxcvbnm")]
            elif lang == "Russian":
                return [list("1234567890"), list("йцукенгшщзхъ"), list("фывапролджэ"), list("ячсмитьбюё")] if alphabet_mode == 'Cyrillic' else [list("1234567890"), list("qwertyuiop"), list("asdfghjkl"), list("zxcvbnm")]
        layouts = {
            "English": [list("1234567890"), list("qwertyuiop"), list("asdfghjkl"), list("zxcvbnm")],
            "Turkce": [list("1234567890"), list("qwertyuıopğü"), list("asdfghjklşi"), list("zxcvbnmöç")],
            "Deutsch": [list("1234567890"), list("qwertzuiopü"), list("asdfghjklöä"), list("yxcvbnmß")],
            "Francais": [list("1234567890"), list("azertyuiop"), list("qsdfghjklm"), list("wxcvbn"), list("àçéèêëîïôùûü")],
            "Espanol": [list("1234567890"), list("qwertyuiop"), list("asdfghjklñ"), list("zxcvbnm"), list("áéíóúü")],
            "Portugues": [list("1234567890"), list("qwertyuiop"), list("asdfghjklç"), list("zxcvbnm"), list("ãõâêôáéíóú")],
        }
        return layouts.get(lang, layouts["English"])

    def add_to_history(self, video):
        self.history = [v for v in self.history if v.id != video.id]
        self.history.insert(0, video)
        self._save_json("yt_history.json", self.history)

    def search_youtube(self, query):
        if not self.ytdlp_path:
            self.status = "yt-dlp not found!"
            self.status_type = "error"
            return
        self.last_search_query = query
        self.search_batch = 1
        self.search_existing_ids = set()
        self.search_first_batch_count = 0
        self.search_results = []
        self.selected = 0
        self.scroll = 0
        self.current_nav = NAV_SEARCH
        self.search_active = False
        self.is_loading = True
        self.is_searching = True
        self.status = "Searching..."
        self.status_type = "loading"
        self.need_redraw = True
        self._load_batch("search", 1)

    def _load_batch(self, list_type, batch_num):
        count = int(self.settings.get("search_count", "8"))
        if list_type == "search":
            if self.search_batch_loading: return
            self.search_batch_loading = True
            target_list = self.search_results
            existing_ids = self.search_existing_ids
            query = f"ytsearch{count}:{self.last_search_query}" if batch_num == 1 else (f"ytsearch{count}:{self.last_search_query} music" if batch_num == 2 else f"ytsearch{count}:{self.last_search_query} video {batch_num}")
        else:
            if self.home_batch_loading: return
            self.home_batch_loading = True
            target_list = self.home_videos
            existing_ids = self.home_existing_ids
            query = f"ytsearch{count}:trending music" if batch_num == 1 else (f"ytsearch{count}:popular music 2024" if batch_num == 2 else f"ytsearch{count}:top hits music {batch_num}")
        
        def worker():
            try:
                # Force H.264 (MP4) to prevent crashes on non-VP9 devices
                cmd = [
                    self.ytdlp_path, 
                    "-f", "best[height<=480][ext=mp4]/best[height<=480]", 
                    query, 
                    "--flat-playlist", 
                    "--dump-json", 
                    "--no-warnings", 
                    "--ignore-errors", 
                    "--no-check-certificates", 
                    "--extractor-args", "youtube:skip=dash,hls;youtube:player_client=android", 
                    "--socket-timeout", "15"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            vid_id = data.get('id')
                            if vid_id and vid_id not in existing_ids:
                                video = VideoItem(data)
                                target_list.append(video)
                                existing_ids.add(vid_id)
                        except: continue
                
                if list_type == "search":
                    self.search_batch = batch_num
                    self.search_batch_loading = False
                    if batch_num == 1: self.search_first_batch_count = len(target_list)
                else:
                    self.home_batch = batch_num
                    self.home_batch_loading = False
                    if batch_num == 1: self.home_first_batch_count = len(target_list)
                
                self.loading_spinner_triggered = False
                if target_list:
                    self.status = f"{len(target_list)} videos"
                    self.status_type = "ok"
                else:
                    self.status = "No results" if list_type == "search" else "Press X to search"
                    self.status_type = "error" if list_type == "search" else "ok"
                
                if batch_num == 1:
                    self.is_loading = False
                    if list_type == "search": self.is_searching = False
                    if target_list: threading.Timer(1.0, lambda: self._load_batch(list_type, 2)).start()
                self.need_redraw = True
            except subprocess.TimeoutExpired:
                if batch_num == 1:
                    self.status, self.status_type, self.is_loading = "Timeout", "error", False
                    if list_type == "search": self.is_searching = False
                if list_type == "search": self.search_batch_loading = False
                else: self.home_batch_loading = False
                self.need_redraw = True
            except Exception as e:
                if batch_num == 1:
                    self.status, self.status_type, self.is_loading = f"Error: {str(e)[:20]}", "error", False
                    if list_type == "search": self.is_searching = False
                if list_type == "search": self.search_batch_loading = False
                else: self.home_batch_loading = False
                self.need_redraw = True
        threading.Thread(target=worker, daemon=True).start()

    def check_load_next_batch(self):
        if self.current_nav == NAV_HOME:
            if (self.home_batch == 2 and self.selected >= self.home_first_batch_count and not self.home_batch_loading and len(self.home_videos) < self.max_videos): self._load_batch("home", 3)
            elif (self.home_batch >= 3 and self.selected >= len(self.home_videos) - 3 and not self.home_batch_loading and len(self.home_videos) < self.max_videos): self._load_batch("home", self.home_batch + 1)
        elif self.current_nav == NAV_SEARCH:
            if (self.search_batch == 2 and self.selected >= self.search_first_batch_count and not self.search_batch_loading and len(self.search_results) < self.max_videos): self._load_batch("search", 3)
            elif (self.search_batch >= 3 and self.selected >= len(self.search_results) - 3 and not self.search_batch_loading and len(self.search_results) < self.max_videos): self._load_batch("search", self.search_batch + 1)

    def load_trending(self):
        if not self.ytdlp_path or self.settings.get("auto_load") == "Off": return
        self.home_batch = 1
        self.home_existing_ids = set()
        self.home_first_batch_count = 0
        self.home_videos = []
        self.is_loading = True
        self.status, self.status_type = "Loading...", "loading"
        self.need_redraw = True
        self.render()
        self._load_batch("home", 1)

    def draw_rect(self, x, y, w, h, color, alpha=255):
        SDL_SetRenderDrawColor(self.renderer, color[0], color[1], color[2], alpha)
        SDL_RenderFillRect(self.renderer, SDL_Rect(int(x), int(y), int(w), int(h)))

    def draw_spinner(self, center_x, center_y, radius=12, dot_size=3):
        import math
        positions = []
        for i in range(8):
            angle = math.pi / 2 - (i * math.pi / 4)
            px = center_x + int(radius * math.cos(angle))
            py = center_y - int(radius * math.sin(angle))
            positions.append((px, py))
        active_index = (self.frame_count // 6) % 8
        for i, (px, py) in enumerate(positions):
            if i == active_index: self.draw_rect(px - dot_size, py - dot_size, dot_size * 2, dot_size * 2, Colors.YT_RED)
            else: self.draw_rect(px - 1, py - 1, 2, 2, Colors.TEXT_TERTIARY)

    def draw_text(self, text, x, y, color=Colors.TEXT_PRIMARY, font=None):
        if not font: font = self.font
        if not font: return 0
        text = str(text)[:80]
        key = (text, color, id(font))
        if key not in self.text_cache:
            if len(self.text_cache) > 150:
                for tex, _, _ in self.text_cache.values():
                    if tex: SDL_DestroyTexture(tex)
                self.text_cache.clear()
            sdl_color = SDL_Color(color[0], color[1], color[2], 255)
            surface = ttf.TTF_RenderUTF8_Blended(font, text.encode('utf-8'), sdl_color)
            if not surface: return 0
            w, h = surface.contents.w, surface.contents.h
            texture = SDL_CreateTextureFromSurface(self.renderer, surface)
            SDL_FreeSurface(surface)
            self.text_cache[key] = (texture, w, h)
        tex, w, h = self.text_cache[key]
        if tex: SDL_RenderCopy(self.renderer, tex, None, SDL_Rect(int(x), int(y), w, h))
        return w

    def render_loading_screen(self, title="Loading...", subtitle=""):
        SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255)
        SDL_RenderClear(self.renderer)
        logo_x, logo_y = SCREEN_WIDTH // 2 - 17, SCREEN_HEIGHT // 2 - 80
        logo_w, logo_h = 34, 24
        self.draw_rect(logo_x + 2, logo_y, logo_w - 4, logo_h, Colors.YT_RED)
        self.draw_rect(logo_x, logo_y + 2, logo_w, logo_h - 4, Colors.YT_RED)
        self.draw_rect(logo_x + 1, logo_y + 1, logo_w - 2, logo_h - 2, Colors.YT_RED)
        tri_x, tri_y, tri_size = logo_x + 12, logo_y + 6, 12
        for row in range(tri_size):
            w = row + 1 if row < tri_size // 2 else tri_size - row
            self.draw_rect(tri_x, tri_y + row, w, 1, Colors.TEXT_PRIMARY)
        self.draw_text(title, SCREEN_WIDTH // 2 - len(title) * 5, SCREEN_HEIGHT // 2 - 20, Colors.TEXT_PRIMARY, self.font_large)
        if subtitle:
            short_title = subtitle[:40] + "..." if len(subtitle) > 40 else subtitle
            self.draw_text(short_title, SCREEN_WIDTH // 2 - len(short_title) * 4, SCREEN_HEIGHT // 2 + 20, Colors.TEXT_SECONDARY, self.font_small)
        bar_width, bar_height = 200, 4
        bar_x, bar_y = SCREEN_WIDTH // 2 - bar_width // 2, SCREEN_HEIGHT // 2 + 60
        self.draw_rect(bar_x, bar_y, bar_width, bar_height, Colors.PROGRESS_BG)
        progress_width = 60
        offset = (self.frame_count * 3) % (bar_width + progress_width)
        start_x = bar_x + offset - progress_width
        draw_start = bar_x if start_x < bar_x else start_x
        draw_width = progress_width - (bar_x - start_x) if start_x < bar_x else min(progress_width, bar_x + bar_width - start_x)
        if draw_width > 0 and draw_start < bar_x + bar_width: self.draw_rect(int(draw_start), bar_y, int(draw_width), bar_height, Colors.YT_RED)
        SDL_RenderPresent(self.renderer)
        self.frame_count += 1

    def render_exit_confirm(self):
        self.draw_rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0), 180)
        box_w, box_h = 400, 160
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2
        self.draw_rect(box_x, box_y, box_w, box_h, Colors.BG_SECONDARY)
        self.draw_rect(box_x, box_y, box_w, 2, Colors.YT_RED)
        self.draw_rect(box_x, box_y + box_h - 2, box_w, 2, Colors.YT_RED)
        icon_y = box_y + 20
        icon_size, icon_x = 40, SCREEN_WIDTH // 2 - 20
        self.draw_rect(icon_x, icon_y, icon_size, icon_size, Colors.YT_RED)
        for i in range(24):
            for t in range(4):
                self.draw_rect(icon_x + 8 + i, icon_y + 8 + i + t, 1, 1, Colors.TEXT_PRIMARY)
                self.draw_rect(icon_x + 32 - i, icon_y + 8 + i + t, 1, 1, Colors.TEXT_PRIMARY)
        title = self.t("exit_confirm_title")
        self.draw_text(title, SCREEN_WIDTH // 2 - len(title) * 4.5, icon_y + 55, Colors.TEXT_PRIMARY, self.font)
        btn_y, btn_w, btn_h, gap = box_y + box_h - 50, 140, 36, 20
        no_x = box_x + (box_w - btn_w * 2 - gap) // 2
        no_sel = self.exit_confirm_selection == 0
        self.draw_rect(no_x, btn_y, btn_w, btn_h, Colors.YT_RED if no_sel else Colors.CARD_BG)
        if not no_sel:
            for i in range(2): self.draw_rect(no_x, btn_y + i*(btn_h-2), btn_w, 2, Colors.TEXT_TERTIARY)
            for i in range(2): self.draw_rect(no_x + i*(btn_w-2), btn_y, 2, btn_h, Colors.TEXT_TERTIARY)
        no_txt = self.t("exit_confirm_no")
        self.draw_text(no_txt, no_x + btn_w//2 - len(no_txt)*4.5, btn_y + 10, Colors.TEXT_PRIMARY, self.font)
        yes_x = no_x + btn_w + gap
        yes_sel = self.exit_confirm_selection == 1
        self.draw_rect(yes_x, btn_y, btn_w, btn_h, Colors.YT_RED if yes_sel else Colors.CARD_BG)
        if not yes_sel:
            for i in range(2): self.draw_rect(yes_x, btn_y + i*(btn_h-2), btn_w, 2, Colors.TEXT_TERTIARY)
            for i in range(2): self.draw_rect(yes_x + i*(btn_w-2), btn_y, 2, btn_h, Colors.TEXT_TERTIARY)
        yes_txt = self.t("exit_confirm_yes")
        self.draw_text(yes_txt, yes_x + btn_w//2 - len(yes_txt)*4.5, btn_y + 10, Colors.TEXT_PRIMARY, self.font)
        help_txt = self.t("exit_confirm_help")
        self.draw_text(help_txt, SCREEN_WIDTH // 2 - len(help_txt) * 3, box_y + box_h - 12, Colors.TEXT_TERTIARY, self.font_tiny)

    def play_video(self, video):
        if not self.ytdlp_path:
            self.status, self.status_type = "yt-dlp not found!", "error"
            return
        if not self.video_player:
            self.status, self.status_type = "No video player found!", "error"
            return
        self.add_to_history(video)
        self.current_video = video
        self.is_loading_video = True
        self.status, self.status_type = "Loading video...", "loading"
        self.need_redraw = True
        self.render_loading_screen(self.t("msg_loading_video"), video.title)
        quality = self.settings.get("quality", "480p")
        height = quality.replace("p", "")
        
        def worker():
            try:
                # Force H.264 (MP4) to prevent crashes on non-VP9 devices
                cmd = [
                    self.ytdlp_path, 
                    "-f", f"best[height<={height}][ext=mp4]/best[height<={height}]", 
                    "-g", 
                    "--no-warnings", 
                    "--no-check-certificates", 
                    "--no-playlist", 
                    "--extractor-args", "youtube:player_client=android", 
                    video.url
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    self.status, self.status_type, self.is_loading_video, self.need_redraw = "Failed to get URL", "error", False, True
                    return
                stream_url = result.stdout.strip().split('\n')[0]
                if not stream_url:
                    self.status, self.status_type, self.is_loading_video, self.need_redraw = "No stream URL", "error", False, True
                    return
                self.is_loading_video = False
                SDL_HideWindow(self.window)
                self.is_playing = True
                self.player_paused = False
                player = self.video_player
                player_name = os.path.basename(player)
                self.mpv_socket = f"/tmp/mpv_{os.getpid()}"
                
                if player_name == "mpv":
                    player_cmd = [player, "--fs", "--no-terminal", "--really-quiet", f"--input-ipc-server={self.mpv_socket}", "--osd-level=1", "--osd-duration=1500", "--cache=yes", "--demuxer-max-bytes=50M", stream_url]
                elif player_name == "ffplay":
                    player_cmd = [player, "-fs", "-autoexit", "-noborder", "-framedrop", "-exitonkeydown"]
                    if height and int(height) <= 480: player_cmd.extend(["-lowres", "1"])
                    player_cmd.extend(["-infbuf", "-threads", "4", "-sync", "video", stream_url])
                elif player_name == "vlc":
                    player_cmd = [player, "--fullscreen", "--play-and-exit", "-q", stream_url]
                else:
                    player_cmd = [player, stream_url]
                
                env = os.environ.copy()
                if 'DISPLAY' not in env: env['DISPLAY'] = ':0'
                
                # FIX: Use local variable first to avoid race condition
                proc = subprocess.Popen(player_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL, env=env)
                self.player_process = proc
                
                last_button_check = time.time()
                while proc.poll() is None:
                    if self.controller and (time.time() - last_button_check > 0.15):
                        SDL_GameControllerUpdate()
                        dpad_up = SDL_GameControllerGetButton(self.controller, SDL_CONTROLLER_BUTTON_DPAD_UP)
                        dpad_down = SDL_GameControllerGetButton(self.controller, SDL_CONTROLLER_BUTTON_DPAD_DOWN)
                        if dpad_up: subprocess.run(["amixer", "set", "Playback", "5%+"], capture_output=True)
                        if dpad_down: subprocess.run(["amixer", "set", "Playback", "5%-"], capture_output=True)
                        last_button_check = time.time()
                    time.sleep(0.05)
            except Exception as e: print(f"Play error: {e}")
            finally:
                self.is_playing = False
                self.player_process = None
                self.current_video = None
                self.player_paused = False
                try:
                    if hasattr(self, 'mpv_socket') and self.mpv_socket and os.path.exists(self.mpv_socket): os.remove(self.mpv_socket)
                except: pass
                SDL_ShowWindow(self.window)
                SDL_RaiseWindow(self.window)
                self.status, self.status_type, self.need_redraw = "Ready", "ok", True
        threading.Thread(target=worker, daemon=True).start()

    def send_mpv_command(self, command):
        if not self.is_playing or not hasattr(self, 'mpv_socket') or not self.mpv_socket: return False
        try:
            import socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect(self.mpv_socket)
            sock.send((json.dumps({"command": command}) + "\n").encode())
            sock.close()
            return True
        except: return False

    def player_seek(self, seconds):
        if self.is_playing: self.send_mpv_command(["seek", str(seconds), "relative"])

    def player_toggle_pause(self):
        if self.is_playing: self.send_mpv_command(["cycle", "pause"])

    def player_brightness(self, delta):
        if self.is_playing: self.send_mpv_command(["add", "brightness", str(delta)])

    def stop_playback(self):
        if self.player_process:
            try: self.player_process.terminate(); self.player_process.wait(timeout=2)
            except:
                try: self.player_process.kill()
                except: pass
        self.is_playing = False
        self.player_process = None
        self.current_video = None
        SDL_ShowWindow(self.window)
        SDL_RaiseWindow(self.window)
        self.status, self.status_type, self.need_redraw = "Stopped", "ok", True

    def get_thumb_path(self, url):
        h = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.image_cache_dir, f"{h}.jpg")

    def download_thumbnail(self, url):
        if not url or url in self.failed_images or url in self.loading_images: return
        if len(self.loading_images) >= 3: return
        self.loading_images.add(url)
        def worker():
            try:
                cache_path = self.get_thumb_path(url)
                if os.path.exists(cache_path):
                    self.loading_images.discard(url)
                    self.need_redraw = True
                    return
                download_url = url
                if download_url.startswith("//"): download_url = "https:" + download_url
                req = urllib.request.Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
                    data = resp.read()
                    if len(data) > 500:
                        with open(cache_path, 'wb') as f: f.write(data)
                    else: self.failed_images.add(url)
            except: self.failed_images.add(url)
            finally:
                self.loading_images.discard(url)
                self.need_redraw = True
        threading.Thread(target=worker, daemon=True).start()

    def load_thumbnail(self, url):
        if not url: return None
        if url in self.image_cache: return self.image_cache[url]
        if url in self.failed_images: return None
        cache_path = self.get_thumb_path(url)
        if os.path.exists(cache_path) and SDL_IMAGE_AVAILABLE:
            try:
                surface = sdlimage.IMG_Load(cache_path.encode())
                if surface:
                    texture = SDL_CreateTextureFromSurface(self.renderer, surface)
                    w, h = surface.contents.w, surface.contents.h
                    SDL_FreeSurface(surface)
                    if texture:
                        if len(self.image_cache) > 30:
                            old_key = next(iter(self.image_cache))
                            old_tex = self.image_cache.pop(old_key)
                            if old_tex and old_tex[0]: SDL_DestroyTexture(old_tex[0])
                        self.image_cache[url] = (texture, w, h)
                        return (texture, w, h)
            except Exception as e: print(f"Load thumbnail error: {e}")
        if url not in self.loading_images: self.download_thumbnail(url)
        return None

    def draw_thumbnail(self, x, y, width, height, url):
        self.draw_rect(x, y, width, height, Colors.THUMB_BG)
        if not url: return
        result = self.load_thumbnail(url)
        if result:
            texture, img_w, img_h = result
            if texture:
                aspect = img_w / img_h if img_h else 16/9
                target_aspect = width / height
                if aspect > target_aspect:
                    draw_w = width
                    draw_h = int(width / aspect)
                    draw_x = x
                    draw_y = y + (height - draw_h) // 2
                else:
                    draw_h = height
                    draw_w = int(height * aspect)
                    draw_x = x + (width - draw_w) // 2
                    draw_y = y
                SDL_RenderCopy(self.renderer, texture, None, SDL_Rect(int(draw_x), int(draw_y), int(draw_w), int(draw_h)))
                return
        if url in self.loading_images:
            dots = "." * ((self.frame_count // 20) % 4)
            self.draw_text(dots, x + width//2 - 10, y + height//2 - 5, Colors.TEXT_SECONDARY, self.font_small)

    def render_header(self):
        self.draw_rect(0, 0, SCREEN_WIDTH, 50, Colors.BG_PRIMARY)
        logo_x, logo_y = 15, 12
        logo_w, logo_h = 34, 24
        self.draw_rect(logo_x + 2, logo_y, logo_w - 4, logo_h, Colors.YT_RED)
        self.draw_rect(logo_x, logo_y + 2, logo_w, logo_h - 4, Colors.YT_RED)
        self.draw_rect(logo_x + 1, logo_y + 1, logo_w - 2, logo_h - 2, Colors.YT_RED)
        tri_x, tri_y, tri_size = logo_x + 12, logo_y + 6, 12
        for row in range(tri_size):
            w = row + 1 if row < tri_size // 2 else tri_size - row
            self.draw_rect(tri_x, tri_y + row, w, 1, Colors.TEXT_PRIMARY)
        self.draw_text("MuTube", 55, 13, Colors.TEXT_PRIMARY, self.font_large)
        self.draw_rect(0, 49, SCREEN_WIDTH, 1, Colors.DIVIDER)

    def render_navigation(self):
        nav_y = SCREEN_HEIGHT - 55
        help_y = nav_y - 18
        self.draw_rect(0, help_y, SCREEN_WIDTH, 18, Colors.BG_SECONDARY)
        help_text = self.t("help_keyboard") if self.search_active else self.t("help_main")
        self.draw_text(help_text, SCREEN_WIDTH//2 - len(help_text)*3, help_y + 3, Colors.TEXT_TERTIARY, self.font_tiny)
        self.draw_rect(0, nav_y, SCREEN_WIDTH, 55, Colors.NAV_BG)
        self.draw_rect(0, nav_y, SCREEN_WIDTH, 1, Colors.DIVIDER)
        items = [("home", self.t("nav_home"), NAV_HOME), ("search", self.t("nav_search"), NAV_SEARCH),
                 ("favorites", self.t("nav_favorites"), NAV_FAVORITES), ("history", self.t("nav_history"), NAV_HISTORY),
                 ("settings", self.t("nav_settings"), NAV_SETTINGS)]
        item_w = SCREEN_WIDTH // len(items)
        for i, (icon_type, label, nav_id) in enumerate(items):
            x = i * item_w
            cx = x + item_w // 2
            active = self.current_nav == nav_id
            if active: self.draw_rect(cx - 20, nav_y + 2, 40, 3, Colors.YT_RED)
            icon_color = Colors.NAV_ACTIVE if active else Colors.NAV_INACTIVE
            icon_y = nav_y + 12
            # Simplified icon drawing
            if icon_type == "home":
                self.draw_rect(cx - 1, icon_y, 2, 2, icon_color)
                self.draw_rect(cx - 3, icon_y + 2, 6, 2, icon_color)
                self.draw_rect(cx - 5, icon_y + 4, 10, 2, icon_color)
                self.draw_rect(cx - 7, icon_y + 6, 14, 2, icon_color)
                self.draw_rect(cx - 6, icon_y + 8, 12, 8, icon_color)
                self.draw_rect(cx - 2, icon_y + 10, 4, 6, Colors.NAV_BG if active else Colors.BG_PRIMARY)
                self.draw_rect(cx + 3, icon_y - 1, 2, 4, icon_color)
            elif icon_type == "search":
                self.draw_rect(cx - 3, icon_y, 6, 2, icon_color)
                self.draw_rect(cx - 5, icon_y + 2, 2, 2, icon_color)
                self.draw_rect(cx + 3, icon_y + 2, 2, 2, icon_color)
                self.draw_rect(cx - 6, icon_y + 4, 2, 4, icon_color)
                self.draw_rect(cx + 4, icon_y + 4, 2, 4, icon_color)
                self.draw_rect(cx - 5, icon_y + 8, 2, 2, icon_color)
                self.draw_rect(cx + 3, icon_y + 8, 2, 2, icon_color)
                self.draw_rect(cx - 3, icon_y + 10, 6, 2, icon_color)
                self.draw_rect(cx + 4, icon_y + 11, 3, 2, icon_color)
                self.draw_rect(cx + 6, icon_y + 13, 3, 2, icon_color)
            elif icon_type == "favorites":
                self.draw_rect(cx - 5, icon_y + 2, 4, 4, icon_color)
                self.draw_rect(cx + 1, icon_y + 2, 4, 4, icon_color)
                self.draw_rect(cx - 6, icon_y + 3, 2, 3, icon_color)
                self.draw_rect(cx + 4, icon_y + 3, 2, 3, icon_color)
                self.draw_rect(cx - 4, icon_y + 1, 2, 2, icon_color)
                self.draw_rect(cx + 2, icon_y + 1, 2, 2, icon_color)
                self.draw_rect(cx - 6, icon_y + 5, 12, 3, icon_color)
                self.draw_rect(cx - 5, icon_y + 8, 10, 2, icon_color)
                self.draw_rect(cx - 4, icon_y + 10, 8, 2, icon_color)
                self.draw_rect(cx - 3, icon_y + 12, 6, 1, icon_color)
                self.draw_rect(cx - 2, icon_y + 13, 4, 1, icon_color)
                self.draw_rect(cx - 1, icon_y + 14, 2, 1, icon_color)
            elif icon_type == "history":
                self.draw_rect(cx - 3, icon_y, 6, 2, icon_color)
                self.draw_rect(cx - 5, icon_y + 2, 2, 2, icon_color)
                self.draw_rect(cx + 3, icon_y + 2, 2, 2, icon_color)
                self.draw_rect(cx - 6, icon_y + 4, 2, 6, icon_color)
                self.draw_rect(cx + 4, icon_y + 4, 2, 6, icon_color)
                self.draw_rect(cx - 5, icon_y + 10, 2, 2, icon_color)
                self.draw_rect(cx + 3, icon_y + 10, 2, 2, icon_color)
                self.draw_rect(cx - 3, icon_y + 12, 6, 2, icon_color)
                self.draw_rect(cx - 1, icon_y + 6, 2, 2, icon_color)
                self.draw_rect(cx - 1, icon_y + 3, 2, 3, icon_color)
                self.draw_rect(cx + 1, icon_y + 6, 3, 2, icon_color)
                self.draw_rect(cx - 8, icon_y + 5, 2, 4, icon_color)
                self.draw_rect(cx - 10, icon_y + 7, 2, 2, icon_color)
                self.draw_rect(cx - 8, icon_y + 9, 2, 2, icon_color)
            elif icon_type == "settings":
                self.draw_rect(cx - 3, icon_y + 4, 6, 6, icon_color)
                self.draw_rect(cx - 1, icon_y + 6, 2, 2, Colors.NAV_BG if active else Colors.BG_PRIMARY)
                self.draw_rect(cx - 2, icon_y, 4, 4, icon_color)
                self.draw_rect(cx - 2, icon_y + 10, 4, 4, icon_color)
                self.draw_rect(cx - 7, icon_y + 5, 4, 4, icon_color)
                self.draw_rect(cx + 3, icon_y + 5, 4, 4, icon_color)
                self.draw_rect(cx - 6, icon_y + 1, 3, 3, icon_color)
                self.draw_rect(cx + 3, icon_y + 1, 3, 3, icon_color)
                self.draw_rect(cx - 6, icon_y + 10, 3, 3, icon_color)
                self.draw_rect(cx + 3, icon_y + 10, 3, 3, icon_color)
            
            label_color = Colors.TEXT_PRIMARY if active else Colors.TEXT_TERTIARY
            self.draw_text(label, cx - len(label)*3, nav_y + 35, label_color, self.font_tiny)

    def render_content(self):
        y = 55
        h = SCREEN_HEIGHT - 55 - 73
        if self.current_nav == NAV_SETTINGS: self.render_settings(y, h); return
        if self.is_searching: self.render_searching(y); return
        videos = self._get_list()
        if videos: self.render_video_list(videos, y, h)
        else: self.render_empty(y)

    def render_searching(self, y):
        msg = self.t("msg_searching")
        self.draw_text(msg, SCREEN_WIDTH//2 - len(msg)*5, y + 100, Colors.TEXT_SECONDARY, self.font)
        if hasattr(self, 'last_search_query') and self.last_search_query:
            query_text = f'"{self.last_search_query}"'
            if len(query_text) > 35: query_text = query_text[:32] + '..."'
            self.draw_text(query_text, SCREEN_WIDTH//2 - len(query_text)*4, y + 130, Colors.TEXT_TERTIARY, self.font_small)
        self.draw_spinner(SCREEN_WIDTH // 2, y + 190, radius=14, dot_size=4)

    def render_empty(self, y):
        msg = self.t("msg_press_search")
        if not self.ytdlp_path: msg = self.t("msg_no_ytdlp")
        elif not self.video_player: msg = self.t("msg_no_player")
        self.draw_text(msg, SCREEN_WIDTH//2 - len(msg)*5, y + 100, Colors.TEXT_SECONDARY, self.font)
        if not self.ytdlp_path: self.draw_text(self.t("msg_install_ytdlp"), 150, y + 140, Colors.TEXT_TERTIARY, self.font_tiny)
        if not self.video_player: self.draw_text(self.t("msg_install_player"), 170, y + 160, Colors.TEXT_TERTIARY, self.font_tiny)
        if self.current_nav == NAV_HOME and (self.is_loading or self.home_batch_loading):
            self.draw_spinner(SCREEN_WIDTH // 2, y + 200, radius=12, dot_size=3)
            self.draw_text(self.t("msg_loading_videos"), SCREEN_WIDTH // 2 - 55, y + 230, Colors.TEXT_TERTIARY, self.font_small)

    def render_settings(self, start_y, height):
        self.draw_text(self.t("settings_title"), 20, start_y + 10, Colors.TEXT_PRIMARY, self.font_large)
        self.draw_text("Ported By: Ronax", SCREEN_WIDTH - 105, start_y + 12, Colors.TEXT_PRIMARY, self.font_small)
        item_h, margin = 50, 5
        list_start_y = start_y + 50
        list_height = height - 60
        visible_count = list_height // (item_h + margin)
        if self.settings_selected < self.settings_scroll: self.settings_scroll = self.settings_selected
        elif self.settings_selected >= self.settings_scroll + visible_count: self.settings_scroll = self.settings_selected - visible_count + 1
        y = list_start_y
        for i in range(self.settings_scroll, min(self.settings_scroll + visible_count, len(self.settings_items))):
            label, key, options = self.settings_items[i]
            selected = i == self.settings_selected
            if selected:
                self.draw_rect(15, y, SCREEN_WIDTH - 30, item_h, Colors.CARD_SELECTED)
                self.draw_rect(15, y, 4, item_h, Colors.YT_RED)
            else: self.draw_rect(15, y, SCREEN_WIDTH - 30, item_h, Colors.CARD_BG)
            self.draw_text(label, 30, y + 15, Colors.TEXT_PRIMARY if selected else Colors.TEXT_SECONDARY, self.font)
            if options is None: self.draw_text(self.t("settings_execute"), SCREEN_WIDTH - 130, y + 15, Colors.YT_RED, self.font_small)
            else:
                current = self.settings.get(key, options[0])
                self.draw_text(f"< {current} >", SCREEN_WIDTH - 130, y + 15, Colors.TEXT_PRIMARY if selected else Colors.TEXT_TERTIARY, self.font)
            y += item_h + margin
        if len(self.settings_items) > visible_count:
            sb_height = list_height
            thumb_height = max(20, int(sb_height * visible_count / len(self.settings_items)))
            thumb_y = list_start_y + int((sb_height - thumb_height) * self.settings_scroll / max(1, len(self.settings_items) - visible_count))
            self.draw_rect(SCREEN_WIDTH - 8, list_start_y, 4, sb_height, Colors.PROGRESS_BG)
            self.draw_rect(SCREEN_WIDTH - 8, thumb_y, 4, thumb_height, Colors.YT_RED)

    def change_setting(self, direction):
        if self.settings_selected >= len(self.settings_items): return
        label, key, options = self.settings_items[self.settings_selected]
        if options is None: return
        current = self.settings.get(key, options[0])
        try: idx = options.index(current)
        except: idx = 0
        idx = (idx + direction) % len(options)
        self.settings[key] = options[idx]
        self._save_settings()
        if key == "language":
            self._update_settings_items()
            self.text_cache.clear()
            self.keyboard_layout = self._get_keyboard_layout()
            lang = self.settings.get("language", "English")
            if lang in ["Ukrainian", "Russian"]: self.alphabet_mode = 'Cyrillic'
            else: self.alphabet_mode = 'Latin'
            self.keyboard_row = self.keyboard_col = 0
        self.status, self.status_type, self.need_redraw = f"{label}: {options[idx]}", "ok", True

    def execute_setting_action(self, key):
        if key == "clear_favorites":
            self.favorites = []
            self._save_json("yt_favorites.json", [])
            self.status, self.status_type = self.t("msg_fav_cleared"), "ok"
        elif key == "clear_history":
            self.history = []
            self._save_json("yt_history.json", [])
            self.status, self.status_type = self.t("msg_history_cleared"), "ok"
        elif key == "clear_cache":
            try:
                import shutil
                if os.path.exists(self.image_cache_dir):
                    shutil.rmtree(self.image_cache_dir)
                    os.makedirs(self.image_cache_dir, exist_ok=True)
                self.image_cache.clear()
                self.failed_images.clear()
                self.status, self.status_type = self.t("msg_cache_cleared"), "ok"
            except Exception as e: self.status, self.status_type = f"Error: {str(e)[:20]}", "error"
        self.need_redraw = True

    def render_video_list(self, videos, start_y, height):
        card_h, margin, thumb_w, thumb_h = 80, 6, 142, 70
        is_batch_loading = (self.current_nav == NAV_HOME and self.home_batch_loading) or (self.current_nav == NAV_SEARCH and self.search_batch_loading)
        is_at_bottom = self.selected >= len(videos) - 1 if len(videos) > 0 else False
        is_near_end = self.selected >= len(videos) - 3 if len(videos) >= 3 else True
        if is_at_bottom and is_batch_loading: self.loading_spinner_triggered = True
        if not is_near_end or not is_batch_loading: self.loading_spinner_triggered = False
        show_loading_card = self.loading_spinner_triggered and is_batch_loading and len(videos) > 0
        base_visible = height // (card_h + margin)
        visible = base_visible - 1 if show_loading_card and base_visible > 1 else base_visible
        if self.selected >= len(videos): self.selected = max(0, len(videos) - 1)
        if self.selected < self.scroll: self.scroll = self.selected
        elif self.selected >= self.scroll + visible: self.scroll = self.selected - visible + 1
        for i, video in enumerate(videos[self.scroll:self.scroll + visible]):
            idx = self.scroll + i
            y = start_y + i * (card_h + margin)
            selected = idx == self.selected
            self.draw_rect(10, y, SCREEN_WIDTH - 20, card_h, Colors.CARD_SELECTED if selected else Colors.CARD_BG)
            if selected: self.draw_rect(10, y, 4, card_h, Colors.YT_RED)
            self.draw_thumbnail(18, y + 5, thumb_w, thumb_h, video.thumbnail)
            if video.duration:
                dur = video.format_duration()
                dur_w = len(dur) * 7 + 6
                self.draw_rect(18 + thumb_w - dur_w - 4, y + thumb_h - 13, dur_w, 14, (0, 0, 0), 200)
                self.draw_text(dur, 18 + thumb_w - dur_w, y + thumb_h - 11, Colors.TEXT_PRIMARY, self.font_tiny)
            info_x = 18 + thumb_w + 10
            title = video.title[:32] + "..." if len(video.title) > 32 else video.title
            self.draw_text(title, info_x, y + 8, Colors.TEXT_PRIMARY if selected else Colors.TEXT_SECONDARY, self.font_small)
            channel = video.channel[:25] if video.channel else ""
            self.draw_text(channel, info_x, y + 28, Colors.TEXT_TERTIARY, self.font_tiny)
            meta = " - ".join(filter(None, [video.format_views(), video.format_date()]))
            self.draw_text(meta[:30], info_x, y + 44, Colors.TEXT_TERTIARY, self.font_tiny)
        if show_loading_card:
            displayed_count = min(len(videos) - self.scroll, visible)
            spinner_card_y = start_y + displayed_count * (card_h + margin)
            self.draw_rect(10, spinner_card_y, SCREEN_WIDTH - 20, card_h, Colors.BG_SECONDARY)
            self.draw_spinner(SCREEN_WIDTH // 2, spinner_card_y + card_h // 2 - 5, radius=12, dot_size=3)
            self.draw_text(self.t("msg_loading"), SCREEN_WIDTH // 2 - 35, spinner_card_y + card_h // 2 + 18, Colors.TEXT_TERTIARY, self.font_small)
        if len(videos) > base_visible:
            sb_h = height
            thumb = max(20, int(sb_h * visible / len(videos)))
            thumb_y = start_y + int((sb_h - thumb) * self.scroll / max(1, len(videos) - visible))
            self.draw_rect(SCREEN_WIDTH - 8, start_y, 4, sb_h, Colors.PROGRESS_BG)
            self.draw_rect(SCREEN_WIDTH - 8, thumb_y, 4, thumb, Colors.YT_RED)

    def render_keyboard(self):
        base_kb_y = SCREEN_HEIGHT - 260
        num_rows = len(self.keyboard_layout)
        if num_rows > 4: base_kb_y -= (num_rows - 4) * 38
        kb_y = base_kb_y
        self.draw_rect(0, kb_y - 45, SCREEN_WIDTH, SCREEN_HEIGHT - kb_y + 45, (0, 0, 0), 240)
        input_y = kb_y - 38
        self.draw_rect(15, input_y, SCREEN_WIDTH - 30, 32, Colors.BG_TERTIARY)
        self.draw_rect(15, input_y, SCREEN_WIDTH - 30, 2, Colors.YT_RED)
        query = self.search_query or self.t("kb_search_placeholder")
        color = Colors.TEXT_PRIMARY if self.search_query else Colors.TEXT_TERTIARY
        display_query = query[:35]
        text_width = self.draw_text(display_query, 25, input_y + 7, color, self.font)
        if self.search_query and (self.frame_count // 15) % 2:
            cursor_x = 25 + text_width + 2
            self.draw_rect(cursor_x, input_y + 5, 2, 20, Colors.YT_RED)
        layout = self.keyboard_layout.copy()
        if self.caps_lock:
            new_layout = []
            for i, row in enumerate(layout):
                if i == 0: new_layout.append(row)
                else: new_layout.append([c.upper() for c in row])
            layout = new_layout
        max_keys, gap, side_margin = max(len(row) for row in layout), 4, 10
        available_width = SCREEN_WIDTH - (2 * side_margin)
        key_w = (available_width - (max_keys - 1) * gap) // max_keys
        key_h = 34
        for row_i, row in enumerate(layout):
            row_width = len(row) * key_w + (len(row) - 1) * gap
            row_offset = (SCREEN_WIDTH - row_width) // 2
            for col_i, char in enumerate(row):
                x, y = row_offset + col_i * (key_w + gap), kb_y + row_i * (key_h + gap)
                selected = self.keyboard_row == row_i and self.keyboard_col == col_i
                self.draw_rect(x, y, key_w, key_h, Colors.YT_RED if selected else Colors.BG_TERTIARY)
                self.draw_text(char, x + key_w//2 - 5, y + 7, Colors.TEXT_PRIMARY, self.font)
        control_row_index = len(layout)
        ctrl_y = kb_y + control_row_index * (key_h + gap)
        lang = self.settings.get("language", "English")
        if lang in ["Ukrainian", "Russian"]:
            toggle_label = "Кир" if getattr(self, 'alphabet_mode', 'Cyrillic') == 'Cyrillic' else "Lat"
            ctrls = [("ABC" if self.caps_lock else "abc", 55), (toggle_label, 55), (self.t("kb_space"), 170), ("<-", 55), (self.t("kb_go"), 80)]
        else:
            ctrls = [("ABC" if self.caps_lock else "abc", 55), (self.t("kb_space"), 180), ("<-", 55), (self.t("kb_go"), 80)]
        total_ctrl_w = sum(c[1] for c in ctrls) + gap * (len(ctrls) - 1)
        ctrl_x = (SCREEN_WIDTH - total_ctrl_w) // 2
        for i, (label, w) in enumerate(ctrls):
            selected = self.keyboard_row == control_row_index and self.keyboard_col == i
            is_go_btn = (lang in ["Ukrainian", "Russian"] and i == 4) or (lang not in ["Ukrainian", "Russian"] and i == 3)
            bg = Colors.YT_RED if (selected or is_go_btn) else Colors.BG_TERTIARY
            self.draw_rect(ctrl_x, ctrl_y, w, key_h, bg if not selected else Colors.YT_RED)
            self.draw_text(label, ctrl_x + w//2 - len(label)*4, ctrl_y + 7, Colors.TEXT_PRIMARY, self.font_small)
            ctrl_x += w + gap
        self.draw_text(self.t("help_keyboard"), 140, ctrl_y + key_h + 8, Colors.TEXT_TERTIARY, self.font_tiny)

    def _get_list(self):
        if self.current_nav == NAV_HOME: return self.home_videos
        if self.current_nav == NAV_SEARCH: return self.search_results
        if self.current_nav == NAV_FAVORITES: return self.favorites
        if self.current_nav == NAV_HISTORY: return self.history
        return []

    def handle_keyboard_nav(self, d):
        lang = self.settings.get("language", "English")
        ctrl_len = 5 if lang in ["Ukrainian", "Russian"] else 4
        lens = [len(row) for row in self.keyboard_layout] + [ctrl_len]
        max_row = len(self.keyboard_layout)
        if d == "up" and self.keyboard_row > 0:
            self.keyboard_row -= 1
            self.keyboard_col = min(self.keyboard_col, lens[self.keyboard_row] - 1)
        elif d == "down" and self.keyboard_row < max_row:
            self.keyboard_row += 1
            self.keyboard_col = min(self.keyboard_col, lens[self.keyboard_row] - 1)
        elif d == "left" and self.keyboard_col > 0: self.keyboard_col -= 1
        elif d == "right" and self.keyboard_col < lens[self.keyboard_row] - 1: self.keyboard_col += 1
        self.need_redraw = True

    def handle_keyboard_select(self):
        num_char_rows = len(self.keyboard_layout)
        if self.keyboard_row < num_char_rows:
            layout = self.keyboard_layout.copy()
            if self.caps_lock:
                new_layout = []
                for i, row in enumerate(layout):
                    if i == 0: new_layout.append(row)
                    else: new_layout.append([c.upper() for c in row])
                layout = new_layout
            row = layout[self.keyboard_row]
            if self.keyboard_col < len(row) and len(self.search_query) < 50: self.search_query += row[self.keyboard_col]
        else:
            lang = self.settings.get("language", "English")
            is_cyrillic = lang in ["Ukrainian", "Russian"]
            col = self.keyboard_col
            if is_cyrillic:
                if col == 0: self.caps_lock = not self.caps_lock
                elif col == 1:
                    self.alphabet_mode = 'Latin' if getattr(self, 'alphabet_mode', 'Cyrillic') == 'Cyrillic' else 'Cyrillic'
                    self.keyboard_layout = self._get_keyboard_layout()
                    self.keyboard_row = min(self.keyboard_row, len(self.keyboard_layout))
                    self.keyboard_col = 0
                elif col == 2 and len(self.search_query) < 50: self.search_query += " "
                elif col == 3 and self.search_query: self.search_query = self.search_query[:-1]
                elif col == 4 and self.search_query.strip(): self.search_youtube(self.search_query.strip())
            else:
                if col == 0: self.caps_lock = not self.caps_lock
                elif col == 1 and len(self.search_query) < 50: self.search_query += " "
                elif col == 2 and self.search_query: self.search_query = self.search_query[:-1]
                elif col == 3 and self.search_query.strip(): self.search_youtube(self.search_query.strip())
        self.need_redraw = True

    def action_up(self):
        if self.selected > 0:
            self.selected -= 1
            self.need_redraw = True

    def action_down(self):
        videos = self._get_list()
        if self.selected < len(videos) - 1:
            self.selected += 1
            self.need_redraw = True
            self.check_load_next_batch()

    def action_left(self):
        self.current_nav = (self.current_nav - 1) % 5
        self.selected = self.scroll = 0
        self.loading_spinner_triggered = False
        self.need_redraw = True

    def action_right(self):
        self.current_nav = (self.current_nav + 1) % 5
        self.selected = self.scroll = 0
        self.loading_spinner_triggered = False
        self.need_redraw = True

    def action_select(self):
        if self.current_nav == NAV_SEARCH and not self.search_results:
            self.search_active = True
            self.search_query = ""
            self.keyboard_row = self.keyboard_col = 0
        else:
            videos = self._get_list()
            if videos and self.selected < len(videos): self.play_video(videos[self.selected])
        self.need_redraw = True

    def action_back(self):
        if self.exit_confirm_active:
            self.exit_confirm_active = False
            self.exit_confirm_selection = 0
        elif self.search_active: self.search_active = False
        elif self.is_playing: self.stop_playback()
        else:
            self.exit_confirm_active = True
            self.exit_confirm_selection = 0
        self.need_redraw = True

    def action_search(self):
        self.search_active = True
        self.search_query = ""
        self.keyboard_row = self.keyboard_col = 0
        self.current_nav = NAV_SEARCH
        self.need_redraw = True

    def toggle_favorite(self):
        videos = self._get_list()
        if not videos or self.selected >= len(videos): return
        video = videos[self.selected]
        is_favorite = any(v.id == video.id for v in self.favorites)
        if is_favorite:
            self.favorites = [v for v in self.favorites if v.id != video.id]
            self.status = self.t("msg_removed_fav")
        else:
            self.favorites.insert(0, video)
            self.status = self.t("msg_added_fav")
        self._save_json("yt_favorites.json", self.favorites)
        self.status_type, self.need_redraw = "ok", True

    def process_repeat(self):
        if not self.key_held: return
        now = SDL_GetTicks()
        if now - self.key_hold_start < 400: return
        if now - self.last_repeat >= 100:
            self.last_repeat = now
            if self.search_active: self.handle_keyboard_nav(self.key_held)
            elif self.key_held == "up": self.action_up()
            elif self.key_held == "down": self.action_down()

    def handle_event(self, event):
        now = SDL_GetTicks()
        if self.is_loading_video: return

        if self.exit_confirm_active:
            if event.type == SDL_CONTROLLERBUTTONDOWN:
                btn = event.cbutton.button
                if btn == SDL_CONTROLLER_BUTTON_DPAD_LEFT: self.exit_confirm_selection = 0
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_RIGHT: self.exit_confirm_selection = 1
                elif btn == SDL_CONTROLLER_BUTTON_A:
                    if self.exit_confirm_selection == 1: self.running = False
                    else: self.exit_confirm_active = False
                elif btn == SDL_CONTROLLER_BUTTON_B: self.exit_confirm_active = False
                self.need_redraw = True
            elif event.type == SDL_KEYDOWN:
                key = event.key.keysym.sym
                if key in (SDLK_LEFT, SDLK_a): self.exit_confirm_selection = 0
                elif key in (SDLK_RIGHT, SDLK_d): self.exit_confirm_selection = 1
                elif key in (SDLK_RETURN, SDLK_z):
                    if self.exit_confirm_selection == 1: self.running = False
                    else: self.exit_confirm_active = False
                elif key in (SDLK_ESCAPE, SDLK_x): self.exit_confirm_active = False
                self.need_redraw = True
            return

        if self.search_active:
            if event.type == SDL_CONTROLLERBUTTONDOWN:
                btn = event.cbutton.button
                if btn == SDL_CONTROLLER_BUTTON_DPAD_UP:
                    self.handle_keyboard_nav("up")
                    self.key_held, self.key_hold_start = "up", now
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_DOWN:
                    self.handle_keyboard_nav("down")
                    self.key_held, self.key_hold_start = "down", now
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_LEFT: self.handle_keyboard_nav("left")
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_RIGHT: self.handle_keyboard_nav("right")
                elif btn == SDL_CONTROLLER_BUTTON_A: self.handle_keyboard_select()
                elif btn == SDL_CONTROLLER_BUTTON_B:
                    self.search_active = False
                    self.need_redraw = True
                elif btn == SDL_CONTROLLER_BUTTON_START:
                    if self.search_query.strip(): self.search_youtube(self.search_query.strip())
                elif btn == SDL_CONTROLLER_BUTTON_Y:
                    if self.search_query: self.search_query = self.search_query[:-1]; self.need_redraw = True
            elif event.type == SDL_CONTROLLERBUTTONUP: self.key_held = None
            elif event.type == SDL_JOYHATMOTION and not self.controller:
                hat = event.jhat.value
                if hat & SDL_HAT_UP:
                    self.handle_keyboard_nav("up")
                    self.key_held, self.key_hold_start = "up", now
                elif hat & SDL_HAT_DOWN:
                    self.handle_keyboard_nav("down")
                    self.key_held, self.key_hold_start = "down", now
                elif hat & SDL_HAT_LEFT: self.handle_keyboard_nav("left")
                elif hat & SDL_HAT_RIGHT: self.handle_keyboard_nav("right")
                else: self.key_held = None
            return

        if event.type == SDL_CONTROLLERBUTTONDOWN:
            btn = event.cbutton.button
            if self.is_playing:
                if btn == SDL_CONTROLLER_BUTTON_B:
                    player_name = os.path.basename(self.video_player) if self.video_player else ""
                    if "ffplay" in player_name: return
                    self.stop_playback()
                elif btn == SDL_CONTROLLER_BUTTON_Y: self.player_toggle_pause()
                elif btn == SDL_CONTROLLER_BUTTON_LEFTSHOULDER: self.player_seek(-10)
                elif btn == SDL_CONTROLLER_BUTTON_RIGHTSHOULDER: self.player_seek(10)
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_LEFT: self.player_seek(-5)
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_RIGHT: self.player_seek(5)
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_UP: self.player_brightness(5)
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_DOWN: self.player_brightness(-5)
                return
            
            if self.current_nav == NAV_SETTINGS:
                if btn == SDL_CONTROLLER_BUTTON_A:
                    label, key, options = self.settings_items[self.settings_selected]
                    if options is None: self.execute_setting_action(key)
                    else: self.change_setting(1)
                elif btn == SDL_CONTROLLER_BUTTON_B: self.action_back()
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_UP:
                    if self.settings_selected > 0: self.settings_selected -= 1; self.need_redraw = True
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_DOWN:
                    if self.settings_selected < len(self.settings_items) - 1: self.settings_selected += 1; self.need_redraw = True
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_LEFT:
                    _, _, options = self.settings_items[self.settings_selected]
                    if options is None: self.action_left()
                    else: self.change_setting(-1)
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_RIGHT:
                    _, _, options = self.settings_items[self.settings_selected]
                    if options is None: self.action_right()
                    else: self.change_setting(1)
                elif btn == SDL_CONTROLLER_BUTTON_LEFTSHOULDER: self.action_left()
                elif btn == SDL_CONTROLLER_BUTTON_RIGHTSHOULDER: self.action_right()
                return

            if btn == SDL_CONTROLLER_BUTTON_A: self.action_select()
            elif btn == SDL_CONTROLLER_BUTTON_B: self.action_back()
            elif btn == SDL_CONTROLLER_BUTTON_X: self.action_search()
            elif btn == SDL_CONTROLLER_BUTTON_Y: self.toggle_favorite()
            elif btn == SDL_CONTROLLER_BUTTON_DPAD_UP:
                self.action_up()
                self.key_held, self.key_hold_start = "up", now
            elif btn == SDL_CONTROLLER_BUTTON_DPAD_DOWN:
                self.action_down()
                self.key_held, self.key_hold_start = "down", now
            elif btn == SDL_CONTROLLER_BUTTON_DPAD_LEFT: self.action_left()
            elif btn == SDL_CONTROLLER_BUTTON_DPAD_RIGHT: self.action_right()
            elif btn == SDL_CONTROLLER_BUTTON_LEFTSHOULDER: self.action_left()
            elif btn == SDL_CONTROLLER_BUTTON_RIGHTSHOULDER: self.action_right()
            elif btn == SDL_CONTROLLER_BUTTON_START: self.action_search()
        elif event.type == SDL_CONTROLLERBUTTONUP:
            self.key_held = None
        elif event.type == SDL_JOYHATMOTION and not self.controller:
            hat = event.jhat.value
            if self.is_playing:
                if hat & SDL_HAT_LEFT: self.player_seek(-5)
                elif hat & SDL_HAT_RIGHT: self.player_seek(5)
                elif hat & SDL_HAT_UP: self.player_brightness(5)
                elif hat & SDL_HAT_DOWN: self.player_brightness(-5)
                return
            
            if self.current_nav == NAV_SETTINGS:
                if hat & SDL_HAT_UP:
                    if self.settings_selected > 0: self.settings_selected -= 1; self.need_redraw = True
                elif hat & SDL_HAT_DOWN:
                    if self.settings_selected < len(self.settings_items) - 1: self.settings_selected += 1; self.need_redraw = True
                elif hat & SDL_HAT_LEFT:
                    _, _, options = self.settings_items[self.settings_selected]
                    if options is None: self.action_left()
                    else: self.change_setting(-1)
                elif hat & SDL_HAT_RIGHT:
                    _, _, options = self.settings_items[self.settings_selected]
                    if options is None: self.action_right()
                    else: self.change_setting(1)
                else: self.key_held = None
                return

            if hat & SDL_HAT_UP:
                self.action_up()
                self.key_held, self.key_hold_start = "up", now
            elif hat & SDL_HAT_DOWN:
                self.action_down()
                self.key_held, self.key_hold_start = "down", now
            elif hat & SDL_HAT_LEFT: self.action_left()
            elif hat & SDL_HAT_RIGHT: self.action_right()
            else: self.key_held = None
        elif event.type == SDL_KEYDOWN:
            key = event.key.keysym.sym
            if key in (SDLK_UP, SDLK_w): self.action_up()
            elif key in (SDLK_DOWN, SDLK_s): self.action_down()
            elif key in (SDLK_LEFT, SDLK_a): self.action_left()
            elif key in (SDLK_RIGHT, SDLK_d): self.action_right()
            elif key in (SDLK_RETURN, SDLK_z): self.action_select()
            elif key in (SDLK_ESCAPE, SDLK_x): self.action_back()

    def render(self):
        self.draw_rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, Colors.BG_PRIMARY)
        self.render_header()
        
        if self.exit_confirm_active:
            self.render_content()
            self.render_navigation()
            self.render_exit_confirm()
        elif self.search_active:
            self.render_keyboard()
        else:
            self.render_content()
        
        self.render_navigation()
        SDL_RenderPresent(self.renderer)
        self.need_redraw = False
        self.frame_count += 1

    def run(self):
        if self.ytdlp_path: self.load_trending()
        event = SDL_Event()
        last_render_time = 0
        while self.running:
            while SDL_PollEvent(event):
                if event.type == SDL_QUIT: self.running = False
                else: self.handle_event(event)
            self.process_repeat()
            current_time = SDL_GetTicks()
            if self.is_loading_video: self.render_loading_screen(self.t("msg_loading_video"), self.current_video.title if self.current_video else "")
            elif not self.is_playing:
                is_batch_loading = self.home_batch_loading or self.search_batch_loading
                force_render = (current_time - last_render_time) >= 100
                if self.need_redraw or self.is_loading or self.loading_images or is_batch_loading or self.is_searching or force_render:
                    self.render()
                    last_render_time = current_time
            SDL_Delay(16)
        self.cleanup()

    def cleanup(self):
        self.stop_playback()
        for tex, _, _ in self.text_cache.values():
            if tex: SDL_DestroyTexture(tex)
        for tex, _, _ in self.image_cache.values():
            if tex: SDL_DestroyTexture(tex)
        if self.font: ttf.TTF_CloseFont(self.font)
        if self.font_large: ttf.TTF_CloseFont(self.font_large)
        if self.font_small: ttf.TTF_CloseFont(self.font_small)
        if self.font_tiny: ttf.TTF_CloseFont(self.font_tiny)
        if self.controller: SDL_GameControllerClose(self.controller)
        if self.joystick: SDL_JoystickClose(self.joystick)
        ttf.TTF_Quit()
        SDL_DestroyRenderer(self.renderer)
        SDL_DestroyWindow(self.window)
        SDL_Quit()

if __name__ == "__main__":
    print(f"Script dir: {SCRIPT_DIR}")
    print(f"yt-dlp: {YTDLP_PATH}")
    print(f"Player: {VIDEO_PLAYER}")
    try:
        app = YouTubeApp()
        app.run()
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)