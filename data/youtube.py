import sys
import os
import json
import subprocess
import threading
import time
import hashlib
import urllib.request
import ssl
import ctypes
import shutil
import re
import tarfile
import math
from datetime import datetime

# --- Setup Paths ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

DOWNLOAD_DIR = os.environ.get(
    "MUTUBE_DOWNLOAD_DIR",
    os.path.join(os.path.dirname(SCRIPT_DIR), "downloads")
)
MPV_LOG_PATH = os.path.join(SCRIPT_DIR, "log.txt")

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

# Default Fallback Resolution
SCREEN_WIDTH = 640
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
        "nav_history": "History", "nav_downloads": "Downloads", "nav_settings": "Settings", "settings_title": "Settings",
        "settings_language": "Language", "settings_quality": "Video Quality",
        "settings_search_count": "Search Count", "settings_auto_load": "Auto Load Home",
        "settings_refresh_home": "Refresh Home",
        "settings_clear_favorites": "Clear Favorites", "settings_clear_history": "Clear History",
        "settings_clear_cache": "Clear Thumb Cache", "settings_credits": "Credits", "settings_execute": "[A] Execute",
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
        "help_main": "A:Play  START:Download  Hold A:Menu  X:Search  Y:Fav",
        "kb_space": "SPACE", "kb_go": "GO", "kb_search_placeholder": "Type to search...",
        "time_today": "Today", "time_live": "LIVE",
        "exit_confirm_title": "Are you sure you want to exit?", "exit_confirm_yes": "Yes",
        "exit_confirm_no": "No", "exit_confirm_help": "[<>] Select [A] Confirm [B] Cancel",
        "credits_title": "Credits", "credits_dev": "Dev: Ronax", "credits_lib": "Based on r36swiki.com work, Powered by yt-dlp & SDL2"
    },
    "Espanol": {
        "nav_home": "Inicio", "nav_search": "Buscar", "nav_favorites": "Favs",
        "nav_history": "Historial", "nav_settings": "Ajustes", "settings_title": "Ajustes",
        "settings_language": "Idioma", "settings_quality": "Calidad",
        "settings_search_count": "Resultados", "settings_auto_load": "Auto Carga",
        "settings_clear_favorites": "Borrar Favoritos", "settings_clear_history": "Borrar Historial",
        "settings_clear_cache": "Borrar Cache", "settings_credits": "Créditos", "settings_execute": "[A] Ejecutar",
        "settings_on": "Si", "settings_off": "No", "msg_searching": "Buscando...",
        "msg_loading": "Cargando...", "msg_loading_video": "Cargando Video...",
        "msg_loading_videos": "Cargando videos...", "msg_no_results": "Sin resultados",
        "msg_press_search": "Pulsa X para buscar", "msg_no_ytdlp": "¡Falta yt-dlp!",
        "msg_no_player": "¡Falta reproductor!", "msg_install_ytdlp": "Instala: pip install yt-dlp",
        "msg_install_player": "Instala: mpv o ffplay", "msg_timeout": "Tiempo agotado",
        "msg_added_fav": "Añadido a favoritos", "msg_removed_fav": "Eliminado de favoritos",
        "msg_fav_cleared": "Favoritos borrados", "msg_history_cleared": "Historial borrado",
        "msg_cache_cleared": "Cache borrada", "msg_videos": "videos",
        "help_keyboard": "A:Escribir B:Cerrar START:Ir",
        "help_main": "A:Sel B:Atrás X:Buscar Y:Fav",
        "kb_space": "ESPACIO", "kb_go": "IR", "kb_search_placeholder": "Escribe para buscar...",
        "time_today": "Hoy", "time_live": "VIVO",
        "exit_confirm_title": "¿Seguro que quieres salir?", "exit_confirm_yes": "Si",
        "exit_confirm_no": "No", "exit_confirm_help": "[<>] Seleccionar [A] Confirmar",
        "credits_title": "Créditos", "credits_dev": "Dev: Ronax", "credits_lib": "Basado en r36swiki.com, con yt-dlp & SDL2"
    },
    "Francais": {
        "nav_home": "Accueil", "nav_search": "Chercher", "nav_favorites": "Favoris",
        "nav_history": "Historique", "nav_settings": "Paramètres", "settings_title": "Paramètres",
        "settings_language": "Langue", "settings_quality": "Qualité Vidéo",
        "settings_search_count": "Nb. Résultats", "settings_auto_load": "Chargement Auto",
        "settings_clear_favorites": "Vider Favoris", "settings_clear_history": "Vider Historique",
        "settings_clear_cache": "Vider Cache", "settings_credits": "Crédits", "settings_execute": "[A] Exécuter",
        "settings_on": "Oui", "settings_off": "Non", "msg_searching": "Recherche...",
        "msg_loading": "Chargement...", "msg_loading_video": "Chargement Vidéo...",
        "msg_loading_videos": "Chargement vidéos...", "msg_no_results": "Aucun résultat",
        "msg_press_search": "Appuyez sur X", "msg_no_ytdlp": "yt-dlp introuvable!",
        "msg_no_player": "Aucun lecteur!", "msg_install_ytdlp": "Installez: pip install yt-dlp",
        "msg_install_player": "Installez: mpv ou ffplay", "msg_timeout": "Délai dépassé",
        "msg_added_fav": "Ajouté aux favoris", "msg_removed_fav": "Retiré des favoris",
        "msg_fav_cleared": "Favoris effacés", "msg_history_cleared": "Historique effacé",
        "msg_cache_cleared": "Cache effacé", "msg_videos": "vidéos",
        "help_keyboard": "A:Entrée B:Fermer START:Go",
        "help_main": "A:Sel B:Retour X:Chercher Y:Fav",
        "kb_space": "ESPACE", "kb_go": "GO", "kb_search_placeholder": "Tapez pour chercher...",
        "time_today": "Auj.", "time_live": "LIVE",
        "exit_confirm_title": "Voulez-vous vraiment quitter?", "exit_confirm_yes": "Oui",
        "exit_confirm_no": "Non", "exit_confirm_help": "[<>] Choisir [A] Confirmer",
        "credits_title": "Crédits", "credits_dev": "Dev: Ronax", "credits_lib": "Basé sur r36swiki.com, via yt-dlp & SDL2"
    },
    "Deutsch": {
        "nav_home": "Start", "nav_search": "Suche", "nav_favorites": "Favoriten",
        "nav_history": "Verlauf", "nav_settings": "Einstellungen", "settings_title": "Einstellungen",
        "settings_language": "Sprache", "settings_quality": "Qualität",
        "settings_search_count": "Anzahl", "settings_auto_load": "Auto-Start",
        "settings_clear_favorites": "Favoriten leeren", "settings_clear_history": "Verlauf leeren",
        "settings_clear_cache": "Cache leeren", "settings_credits": "Credits", "settings_execute": "[A] Ausführen",
        "settings_on": "An", "settings_off": "Aus", "msg_searching": "Suchen...",
        "msg_loading": "Laden...", "msg_loading_video": "Lade Video...",
        "msg_loading_videos": "Lade Videos...", "msg_no_results": "Keine Ergebnisse",
        "msg_press_search": "Drücke X zum Suchen", "msg_no_ytdlp": "yt-dlp fehlt!",
        "msg_no_player": "Kein Player!", "msg_install_ytdlp": "Installiere: pip install yt-dlp",
        "msg_install_player": "Installiere: mpv oder ffplay", "msg_timeout": "Zeitüberschreitung",
        "msg_added_fav": "Zu Favoriten hinzugefügt", "msg_removed_fav": "Aus Favoriten entfernt",
        "msg_fav_cleared": "Favoriten geleert", "msg_history_cleared": "Verlauf geleert",
        "msg_cache_cleared": "Cache geleert", "msg_videos": "Videos",
        "help_keyboard": "A:Tippen B:Zu START:Los",
        "help_main": "A:Wählen B:Zurück X:Suche Y:Fav",
        "kb_space": "LEER", "kb_go": "LOS", "kb_search_placeholder": "Suchbegriff eingeben...",
        "time_today": "Heute", "time_live": "LIVE",
        "exit_confirm_title": "Wirklich beenden?", "exit_confirm_yes": "Ja",
        "exit_confirm_no": "Nein", "exit_confirm_help": "[<>] Wählen [A] Bestätigen",
        "credits_title": "Credits", "credits_dev": "Dev: Ronax", "credits_lib": "Basierend auf r36swiki.com, mit yt-dlp & SDL2"
    },
    "Portugues": {
        "nav_home": "Início", "nav_search": "Buscar", "nav_favorites": "Favs",
        "nav_history": "Histórico", "nav_settings": "Config", "settings_title": "Configurações",
        "settings_language": "Idioma", "settings_quality": "Qualidade",
        "settings_search_count": "Contagem", "settings_auto_load": "Auto Carregar",
        "settings_clear_favorites": "Limpar Favoritos", "settings_clear_history": "Limpar Histórico",
        "settings_clear_cache": "Limpar Cache", "settings_credits": "Créditos", "settings_execute": "[A] Executar",
        "settings_on": "Sim", "settings_off": "Não", "msg_searching": "Buscando...",
        "msg_loading": "Carregando...", "msg_loading_video": "Carregando Vídeo...",
        "msg_loading_videos": "Carregando vídeos...", "msg_no_results": "Sem resultados",
        "msg_press_search": "Pressione X para buscar", "msg_no_ytdlp": "yt-dlp não encontrado!",
        "msg_no_player": "Sem player!", "msg_install_ytdlp": "Instale: pip install yt-dlp",
        "msg_install_player": "Instale: mpv ou ffplay", "msg_timeout": "Tempo esgotado",
        "msg_added_fav": "Adicionado aos favoritos", "msg_removed_fav": "Removido dos favoritos",
        "msg_fav_cleared": "Favoritos limpos", "msg_history_cleared": "Histórico limpo",
        "msg_cache_cleared": "Cache limpo", "msg_videos": "vídeos",
        "help_keyboard": "A:Digitar B:Fechar START:Ir",
        "help_main": "A:Sel B:Voltar X:Busca Y:Fav",
        "kb_space": "ESPAÇO", "kb_go": "IR", "kb_search_placeholder": "Digite para buscar...",
        "time_today": "Hoje", "time_live": "AO VIVO",
        "exit_confirm_title": "Tem certeza que deseja sair?", "exit_confirm_yes": "Sim",
        "exit_confirm_no": "Não", "exit_confirm_help": "[<>] Selecionar [A] Confirmar",
        "credits_title": "Créditos", "credits_dev": "Dev: Ronax", "credits_lib": "Baseado em r36swiki.com, com yt-dlp & SDL2"
    },
    "Turkce": {
        "nav_home": "Ana Sayfa", "nav_search": "Ara", "nav_favorites": "Favoriler",
        "nav_history": "Geçmiş", "nav_settings": "Ayarlar", "settings_title": "Ayarlar",
        "settings_language": "Dil", "settings_quality": "Kalite",
        "settings_search_count": "Sayı", "settings_auto_load": "Oto. Yükle",
        "settings_clear_favorites": "Fav. Temizle", "settings_clear_history": "Geçmişi Temizle",
        "settings_clear_cache": "Önbelleği Temizle", "settings_credits": "Emeği Geçenler", "settings_execute": "[A] Uygula",
        "settings_on": "Açık", "settings_off": "Kapalı", "msg_searching": "Aranıyor...",
        "msg_loading": "Yükleniyor...", "msg_loading_video": "Video Yükleniyor...",
        "msg_loading_videos": "Videolar Yükleniyor...", "msg_no_results": "Sonuç yok",
        "msg_press_search": "Aramak için X'e basın", "msg_no_ytdlp": "yt-dlp bulunamadı!",
        "msg_no_player": "Oynatıcı yok!", "msg_install_ytdlp": "Yükle: pip install yt-dlp",
        "msg_install_player": "Yükle: mpv veya ffplay", "msg_timeout": "Zaman aşımı",
        "msg_added_fav": "Favorilere eklendi", "msg_removed_fav": "Favorilerden çıkarıldı",
        "msg_fav_cleared": "Favoriler temizlendi", "msg_history_cleared": "Geçmiş temizlendi",
        "msg_cache_cleared": "Önbellek temizlendi", "msg_videos": "video",
        "help_keyboard": "A:Yaz B:Kapat START:Git",
        "help_main": "A:Seç B:Geri X:Ara Y:Fav",
        "kb_space": "BOŞLUK", "kb_go": "GİT", "kb_search_placeholder": "Aramak için yazın...",
        "time_today": "Bugün", "time_live": "CANLI",
        "exit_confirm_title": "Çıkmak istiyor musunuz?", "exit_confirm_yes": "Evet",
        "exit_confirm_no": "Hayır", "exit_confirm_help": "[<>] Seç [A] Onayla",
        "credits_title": "Emeği Geçenler", "credits_dev": "Dev: Ronax", "credits_lib": "r36swiki.com tabanlı, yt-dlp & SDL2 ile"
    },
    "Russian": {
        "nav_home": "Главная", "nav_search": "Поиск", "nav_favorites": "Избранное",
        "nav_history": "История", "nav_settings": "Настройки", "settings_title": "Настройки",
        "settings_language": "Язык", "settings_quality": "Качество",
        "settings_search_count": "Кол-во", "settings_auto_load": "Автозагрузка",
        "settings_clear_favorites": "Очистить избранное", "settings_clear_history": "Очистить историю",
        "settings_clear_cache": "Очистить кэш", "settings_credits": "О программе", "settings_execute": "[A] Выполнить",
        "settings_on": "Вкл", "settings_off": "Выкл", "msg_searching": "Поиск...",
        "msg_loading": "Загрузка...", "msg_loading_video": "Загрузка видео...",
        "msg_loading_videos": "Загрузка списка...", "msg_no_results": "Нет результатов",
        "msg_press_search": "Нажмите X для поиска", "msg_no_ytdlp": "yt-dlp не найден!",
        "msg_no_player": "Нет плеера!", "msg_install_ytdlp": "Установите: pip install yt-dlp",
        "msg_install_player": "Установите: mpv или ffplay", "msg_timeout": "Тайм-аут",
        "msg_added_fav": "Добавлено в избранное", "msg_removed_fav": "Удалено из избранного",
        "msg_fav_cleared": "Избранное очищено", "msg_history_cleared": "История очищена",
        "msg_cache_cleared": "Кэш очищен", "msg_videos": "видео",
        "help_keyboard": "A:Ввод B:Закр START:Поиск",
        "help_main": "A:Выбор B:Назад X:Поиск Y:Избр",
        "kb_space": "ПРОБЕЛ", "kb_go": "ГО", "kb_search_placeholder": "Введите запрос...",
        "time_today": "Сегодня", "time_live": "ЭФИР",
        "exit_confirm_title": "Вы уверены, что хотите выйти?", "exit_confirm_yes": "Да",
        "exit_confirm_no": "Нет", "exit_confirm_help": "[<>] Выбор [A] Подтвердить",
        "credits_title": "О программе", "credits_dev": "Разраб: Ronax", "credits_lib": "Основано на r36swiki.com, yt-dlp & SDL2"
    },
    "Ukrainian": {
        "nav_home": "Головна", "nav_search": "Пошук", "nav_favorites": "Улюблене",
        "nav_history": "Історія", "nav_settings": "Налаштування", "settings_title": "Налаштування",
        "settings_language": "Мова", "settings_quality": "Якість",
        "settings_search_count": "Кількість", "settings_auto_load": "Автозавантаження",
        "settings_clear_favorites": "Очистити улюблене", "settings_clear_history": "Очистити історію",
        "settings_clear_cache": "Очистити кеш", "settings_credits": "Про програму", "settings_execute": "[A] Виконати",
        "settings_on": "Увімк", "settings_off": "Вимк", "msg_searching": "Пошук...",
        "msg_loading": "Завантаження...", "msg_loading_video": "Завантаження відео...",
        "msg_loading_videos": "Завантаження списку...", "msg_no_results": "Немає результатів",
        "msg_press_search": "Натисніть X для пошуку", "msg_no_ytdlp": "yt-dlp не знайдено!",
        "msg_no_player": "Немає плеєра!", "msg_install_ytdlp": "Встановіть: pip install yt-dlp",
        "msg_install_player": "Встановіть: mpv або ffplay", "msg_timeout": "Час вичерпано",
        "msg_added_fav": "Додано в улюблене", "msg_removed_fav": "Видалено з улюбленого",
        "msg_fav_cleared": "Улюблене очищено", "msg_history_cleared": "Історію очищено",
        "msg_cache_cleared": "Кеш очищено", "msg_videos": "відео",
        "help_keyboard": "A:Ввід B:Закр START:Пошук",
        "help_main": "A:Вибір B:Назад X:Пошук Y:Улюб",
        "kb_space": "ПРОБІЛ", "kb_go": "ГО", "kb_search_placeholder": "Введіть запит...",
        "time_today": "Сьогодні", "time_live": "ЕФІР",
        "exit_confirm_title": "Ви впевнені, що хочете вийти?", "exit_confirm_yes": "Так",
        "exit_confirm_no": "Ні", "exit_confirm_help": "[<>] Вибір [A] Підтвердити",
        "credits_title": "Про програму", "credits_dev": "Розроб: Ronax", "credits_lib": "Засновано на r36swiki.com, yt-dlp & SDL2"
    }
}

LANGUAGES = ["English", "Espanol", "Francais", "Deutsch", "Portugues", "Turkce", "Russian", "Ukrainian"]
NAV_HOME, NAV_SEARCH, NAV_FAVORITES, NAV_HISTORY, NAV_DOWNLOADS, NAV_SETTINGS = range(6)
SEARCH_GENRES = ["Gaming", "Music", "Movies", "Trailers", "Sports", "News", "Technology", "Comedy", "Education"]

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

def find_ffplay():
    configured = os.environ.get("MUTUBE_FFPLAY")
    paths = [
        configured,
        os.path.join(SCRIPT_DIR, "ffplay"),
        "/mnt/mmc/MUOS/PortMaster/libs/ffplay",
        "/opt/system/Tools/PortMaster/libs/ffplay",
        "/opt/tools/PortMaster/libs/ffplay",
    ]
    for path in paths:
        if path and os.path.isfile(path):
            try: os.chmod(path, 0o755)
            except: pass
            return path
    try:
        result = subprocess.run(["which", "ffplay"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip(): return result.stdout.strip()
    except: pass
    return None

def find_ffmpeg():
    paths = [os.path.join(SCRIPT_DIR, "ffmpeg"), "/opt/system/Tools/PortMaster/libs/ffmpeg"]
    for path in paths:
        if os.path.isfile(path): return path
    try:
        result = subprocess.run(["which", "ffmpeg"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip(): return result.stdout.strip()
    except: pass
    return None

YTDLP_PATH = find_ytdlp()
VIDEO_PLAYER = find_video_player()
LOCAL_VIDEO_PLAYER = find_ffplay()
FFMPEG_PATH = find_ffmpeg()

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

        global SCREEN_WIDTH, SCREEN_HEIGHT
        if "APP_SCREEN_WIDTH" in os.environ and "APP_SCREEN_HEIGHT" in os.environ:
            self.screen_width = int(os.environ["APP_SCREEN_WIDTH"])
            self.screen_height = int(os.environ["APP_SCREEN_HEIGHT"])
            print(f"Using Script Resolution: {self.screen_width}x{self.screen_height}")

        else:
            display_mode = SDL_DisplayMode()
            if SDL_GetCurrentDisplayMode(0, ctypes.byref(display_mode)) == 0:
                self.screen_width = display_mode.w
                self.screen_height = display_mode.h
                print(f"Auto-Detected Resolution: {self.screen_width}x{self.screen_height}")
            else:
                self.screen_width = 640
                self.screen_height = 480
                print("Resolution detect failed, using 640x480")

        self.window = SDL_CreateWindow(b"YouTube", SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED, self.screen_width, self.screen_height, SDL_WINDOW_SHOWN)
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
        self.start_in_downloads = os.environ.get("MUTUBE_START_TAB") == "downloads"
        self.restart_to_downloads = False
        self.current_nav = NAV_DOWNLOADS if self.start_in_downloads else NAV_HOME
        self.selected = 0
        self.scroll = 0
        self.ytdlp_path = YTDLP_PATH
        self.video_player = VIDEO_PLAYER
        
        self.home_videos = []
        self.search_results = []
        self.favorites = self._load_json("yt_favorites.json")
        self.history = self._load_json("yt_history.json")
        self.downloaded_videos = []
        self.offline_mode = False
        self.load_downloads()
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

        self.credits_active = False
        self.action_popup_active = False
        self.action_popup_selection = 0
        self.action_popup_video = None
        self.file_details_active = False
        self.file_details_video = None
        self.a_button_down_at = None
        self.is_playing = False
        self.is_loading_video = False
        self.is_downloading = False
        self.is_updating = False
        self.update_progress = 0
        self.update_size_text = ""
        self.update_label = ""
        self.dependency_prompt_active = False
        self.active_process = None
        self.cancel_requested = False
        self.download_progress = 0
        self.download_size_text = ""
        self.is_searching = False
        self.player_process = None
        self.current_video = None
        self.player_paused = False
        self.mpv_socket = None
        self.restore_window_requested = False
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

    def load_downloads(self):
        """Refresh the locally saved-video list without requiring a network."""
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        supported_extensions = {".mp4", ".m4v", ".mkv", ".webm", ".avi", ".mov"}
        videos = []
        try:
            entries = sorted(
                (entry for entry in os.scandir(DOWNLOAD_DIR)
                 if entry.is_file() and os.path.splitext(entry.name)[1].lower() in supported_extensions),
                key=lambda entry: entry.stat().st_mtime,
                reverse=True
            )
            for entry in entries:
                stat = entry.stat()
                video = VideoItem({
                    "id": "local_" + entry.name,
                    "title": os.path.splitext(entry.name)[0],
                    "channel": f"{stat.st_size / (1024 * 1024):.1f} MB",
                    "upload_date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y%m%d"),
                    "url": entry.path,
                })
                # A successful download stores the original YouTube thumbnail
                # next to the video using the same base filename.
                thumbnail_path = os.path.splitext(entry.path)[0] + ".jpg"
                video.thumbnail = thumbnail_path if os.path.isfile(thumbnail_path) else ""
                video.is_local = True
                videos.append(video)
        except Exception as e:
            print(f"Could not scan downloads: {e}")
        self.downloaded_videos = videos

    def show_downloads_offline(self):
        self.offline_mode = True
        self.load_downloads()
        self.current_nav = NAV_DOWNLOADS
        self.selected = self.scroll = 0
        self.status = "Offline mode - showing downloads"
        self.status_type = "ok" if self.downloaded_videos else "error"
        self.need_redraw = True

    def _load_settings(self):
        try:
            path = os.path.join(SCRIPT_DIR, "yt_settings.json")
            if os.path.exists(path):
                with open(path) as f: return json.load(f)
        except: pass
        return {
            "quality": "720p", "search_count": "10", "auto_load": "On",
            "language": "English", "a_button_action": "Play", "media_target": "MMC"
        }

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
            (tr["settings_quality"], "quality", ["360p", "480p", "720p", "1080p"]),
            (tr["settings_search_count"], "search_count", ["10", "15", "20", "25"]),
            (tr["settings_auto_load"], "auto_load", on_off),
            ("A Button", "a_button_action", ["Play", "Download"]),
            ("Media destination", "media_target", ["MMC", "SD Card"]),
            ("Install / Update yt-dlp", "update_ytdlp", None),
            ("Install / Update FFmpeg", "update_ffmpeg", None),
            ("Install / Update both", "update_all", None),
            (tr.get("settings_refresh_home", "Refresh Home"), "refresh_home", None),
            (tr.get("settings_credits", "Credits"), "show_credits", None),
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
                # Force H.264 (MP4) and Split Stream
                height = self.settings.get("quality", "720p").replace("p", "")
                
                # UPDATED FORMAT STRING:
                # 1. Best video (H.264) <= requested height + Best M4A Audio
                # 2. Fallback: ANY video <= requested height + Best Audio (Allows VP9 if H264 missing)
                # 3. Fallback: Pre-muxed MP4 (usually 360p)
                format_str = f"bv*[height<={height}][vcodec^=avc]+ba[ext=m4a]/bv*[height<={height}]+ba/b[height<={height}][ext=mp4]/best[height<={height}]"
                
                cmd = [
                    self.ytdlp_path, 
                    "-f", format_str, 
                    query, 
                    "--flat-playlist", 
                    "--dump-json", 
                    "--no-warnings", 
                    "--ignore-errors", 
                    "--no-check-certificates",
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
                if list_type == "home" and batch_num == 1 and not target_list:
                    self.is_loading = False
                    self.show_downloads_offline()
                    return
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
                if list_type == "home" and batch_num == 1:
                    self.show_downloads_offline()
                self.need_redraw = True
            except Exception as e:
                if batch_num == 1:
                    self.status, self.status_type, self.is_loading = f"Error: {str(e)[:20]}", "error", False
                    if list_type == "search": self.is_searching = False
                if list_type == "search": self.search_batch_loading = False
                else: self.home_batch_loading = False
                if list_type == "home" and batch_num == 1:
                    self.show_downloads_offline()
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
    
    def render_credits_popup(self):
        # Semi-transparent overlay
        self.draw_rect(0, 0, self.screen_width, self.screen_height, (0, 0, 0), 180)
        
        # Box Dimensions
        box_w, box_h = 420, 220
        box_x = (self.screen_width - box_w) // 2
        box_y = (self.screen_height - box_h) // 2
        
        # Draw Box
        self.draw_rect(box_x, box_y, box_w, box_h, Colors.BG_SECONDARY)
        self.draw_rect(box_x, box_y, box_w, 2, Colors.YT_RED)
        self.draw_rect(box_x, box_y + box_h - 2, box_w, 2, Colors.YT_RED)
        
        # Content
        title = self.t("credits_title")
        self.draw_text(title, self.screen_width // 2 - len(title) * 6, box_y + 20, Colors.TEXT_PRIMARY, self.font_large)
        
        dev = self.t("credits_dev")
        self.draw_text(dev, self.screen_width // 2 - len(dev) * 4, box_y + 80, Colors.TEXT_SECONDARY, self.font)
        
        lib = self.t("credits_lib")
        if len(lib) > 40:  
             self.draw_text("Based on r36swiki.com work", self.screen_width // 2 - 130, box_y + 115, Colors.TEXT_TERTIARY, self.font_small)
             self.draw_text("Powered by yt-dlp & SDL2", self.screen_width // 2 - 110, box_y + 135, Colors.TEXT_TERTIARY, self.font_small)
        else:
             self.draw_text(lib, self.screen_width // 2 - len(lib) * 3, box_y + 120, Colors.TEXT_TERTIARY, self.font_small)
        
        close = "[ A / B ] Close"
        self.draw_text(close, self.screen_width // 2 - len(close) * 3, box_y + box_h - 30, Colors.YT_RED, self.font_tiny)

    def render_action_popup(self):
        self.draw_rect(0, 0, self.screen_width, self.screen_height, (0, 0, 0), 180)
        box_w, box_h = 360, 310
        box_x = (self.screen_width - box_w) // 2
        box_y = (self.screen_height - box_h) // 2
        self.draw_rect(box_x, box_y, box_w, box_h, Colors.BG_SECONDARY)
        self.draw_rect(box_x, box_y, box_w, 2, Colors.YT_RED)
        self.draw_text("Choose action", box_x + 110, box_y + 18, Colors.TEXT_PRIMARY, self.font_large)
        choices = self._popup_choices()
        for index, choice in enumerate(choices):
            y = box_y + 62 + index * 40
            selected = index == self.action_popup_selection
            self.draw_rect(box_x + 22, y, box_w - 44, 32, Colors.YT_RED if selected else Colors.CARD_BG)
            self.draw_text(choice, box_x + 40, y + 8, Colors.TEXT_PRIMARY if selected else Colors.TEXT_SECONDARY, self.font)
        help_text = "Up/Down: Select   A: Confirm   B: Cancel"
        self.draw_text(help_text, box_x + 22, box_y + box_h - 28, Colors.TEXT_TERTIARY, self.font_tiny)

    def render_file_details_popup(self):
        video = self.file_details_video
        if not video: return
        self.draw_rect(0, 0, self.screen_width, self.screen_height, (0, 0, 0), 180)
        box_w, box_h = 500, 270
        box_x, box_y = (self.screen_width - box_w) // 2, (self.screen_height - box_h) // 2
        self.draw_rect(box_x, box_y, box_w, box_h, Colors.BG_SECONDARY)
        self.draw_rect(box_x, box_y, box_w, 2, Colors.YT_RED)
        path = video.url
        try:
            stat = os.stat(path)
            size = f"{stat.st_size / (1024 * 1024):.1f} MB"
            created = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
        except:
            size, created = "Unknown", "Unknown"
        resolution = self._local_video_resolution(path)
        fields = [("Name", os.path.basename(path)), ("Size", size), ("Resolution", resolution), ("Created", created), ("Path", path)]
        self.draw_text("File details", box_x + 180, box_y + 18, Colors.TEXT_PRIMARY, self.font_large)
        for index, (label, value) in enumerate(fields):
            text = f"{label}: {value}"
            self.draw_text(text[:58], box_x + 22, box_y + 64 + index * 30, Colors.TEXT_SECONDARY, self.font_small)
        self.draw_text("[ A / B ] Back", box_x + 22, box_y + box_h - 28, Colors.YT_RED, self.font_tiny)

    def render_loading_screen(self, title="Loading...", subtitle=""):
        SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255)
        SDL_RenderClear(self.renderer)
        logo_x, logo_y = self.screen_width // 2 - 17, self.screen_height // 2 - 80
        logo_w, logo_h = 34, 24
        self.draw_rect(logo_x + 2, logo_y, logo_w - 4, logo_h, Colors.YT_RED)
        self.draw_rect(logo_x, logo_y + 2, logo_w, logo_h - 4, Colors.YT_RED)
        self.draw_rect(logo_x + 1, logo_y + 1, logo_w - 2, logo_h - 2, Colors.YT_RED)
        tri_x, tri_y, tri_size = logo_x + 12, logo_y + 6, 12
        for row in range(tri_size):
            w = row + 1 if row < tri_size // 2 else tri_size - row
            self.draw_rect(tri_x, tri_y + row, w, 1, Colors.TEXT_PRIMARY)
        self.draw_text(title, self.screen_width // 2 - len(title) * 5, self.screen_height // 2 - 20, Colors.TEXT_PRIMARY, self.font_large)
        if subtitle:
            short_title = subtitle[:40] + "..." if len(subtitle) > 40 else subtitle
            self.draw_text(short_title, self.screen_width // 2 - len(short_title) * 4, self.screen_height // 2 + 20, Colors.TEXT_SECONDARY, self.font_small)
        # A compact circular loader avoids the old line-progress appearance
        # while a video URL is being resolved.
        cx, cy, radius = self.screen_width // 2, self.screen_height // 2 + 68, 12
        phase = (self.frame_count // 3) % 12
        for index in range(12):
            angle = (index * 30) * 3.14159 / 180
            x, y = int(cx + radius * math.cos(angle)), int(cy + radius * math.sin(angle))
            color = Colors.YT_RED if index == phase else Colors.PROGRESS_BG
            self.draw_rect(x - 2, y - 2, 4, 4, color)
        self.draw_text("B: Back", self.screen_width // 2 - 22, cy + 26, Colors.TEXT_TERTIARY, self.font_tiny)
        SDL_RenderPresent(self.renderer)
        self.frame_count += 1

    def render_download_progress(self, title, subtitle, percent, size_text=""):
        SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255)
        SDL_RenderClear(self.renderer)
        self.draw_text(title, self.screen_width // 2 - len(title) * 5, self.screen_height // 2 - 52, Colors.TEXT_PRIMARY, self.font_large)
        short = subtitle[:42] + "..." if len(subtitle) > 42 else subtitle
        self.draw_text(short, self.screen_width // 2 - len(short) * 4, self.screen_height // 2 - 20, Colors.TEXT_SECONDARY, self.font_small)
        bar_w, bar_h = 300, 16
        bar_x, bar_y = self.screen_width // 2 - bar_w // 2, self.screen_height // 2 + 18
        self.draw_rect(bar_x, bar_y, bar_w, bar_h, Colors.PROGRESS_BG)
        self.draw_rect(bar_x, bar_y, int(bar_w * max(0, min(100, percent)) / 100), bar_h, Colors.YT_RED)
        detail = f"{percent}%" + (f"  {size_text}" if size_text else "")
        self.draw_text(detail, self.screen_width // 2 - len(detail) * 4, bar_y + 28, Colors.TEXT_PRIMARY, self.font_small)
        self.draw_text("B: Cancel", self.screen_width // 2 - 28, bar_y + 54, Colors.TEXT_TERTIARY, self.font_tiny)
        SDL_RenderPresent(self.renderer)
        self.frame_count += 1

    def render_dependency_prompt(self):
        self.draw_rect(0, 0, self.screen_width, self.screen_height, Colors.BG_PRIMARY)
        box_w, box_h = 520, 190
        box_x, box_y = (self.screen_width - box_w) // 2, (self.screen_height - box_h) // 2
        self.draw_rect(box_x, box_y, box_w, box_h, Colors.BG_SECONDARY)
        self.draw_rect(box_x, box_y, box_w, 2, Colors.YT_RED)
        self.draw_text("Download required components?", box_x + 95, box_y + 24, Colors.TEXT_PRIMARY, self.font_large)
        self.draw_text("yt-dlp and FFmpeg are not included in MuTube.", box_x + 36, box_y + 68, Colors.TEXT_SECONDARY, self.font_small)
        self.draw_text("A: Download now     B: Continue offline", box_x + 68, box_y + 128, Colors.YT_RED, self.font_small)
        SDL_RenderPresent(self.renderer)

    def render_exit_confirm(self):
        self.draw_rect(0, 0, self.screen_width, self.screen_height, (0, 0, 0), 180)
        box_w, box_h = 400, 160
        box_x = (self.screen_width - box_w) // 2
        box_y = (self.screen_height - box_h) // 2
        self.draw_rect(box_x, box_y, box_w, box_h, Colors.BG_SECONDARY)
        self.draw_rect(box_x, box_y, box_w, 2, Colors.YT_RED)
        self.draw_rect(box_x, box_y + box_h - 2, box_w, 2, Colors.YT_RED)
        icon_y = box_y + 20
        icon_size, icon_x = 40, self.screen_width // 2 - 20
        self.draw_rect(icon_x, icon_y, icon_size, icon_size, Colors.YT_RED)
        for i in range(24):
            for t in range(4):
                self.draw_rect(icon_x + 8 + i, icon_y + 8 + i + t, 1, 1, Colors.TEXT_PRIMARY)
                self.draw_rect(icon_x + 32 - i, icon_y + 8 + i + t, 1, 1, Colors.TEXT_PRIMARY)
        title = self.t("exit_confirm_title")
        self.draw_text(title, self.screen_width // 2 - len(title) * 4.5, icon_y + 55, Colors.TEXT_PRIMARY, self.font)
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
        self.draw_text(help_txt, self.screen_width // 2 - len(help_txt) * 3, box_y + box_h - 12, Colors.TEXT_TERTIARY, self.font_tiny)

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
        
        # NOTE: Default to 720p if settings are missing or old
        quality = self.settings.get("quality", "720p")
        print(f"Requesting Quality: {quality}")
        height = quality.replace("p", "")
        
        def worker():
            try:
                # Force H.264 (MP4) and Split Stream
                format_str = f"bv*[height<={height}]+ba/b[height<={height}]"
                
                cmd = [
                    self.ytdlp_path, 
                    "-f", format_str, 
                    "-S", "res,vcodec:avc",
                    "-g", 
                    "--no-warnings", 
                    "--no-check-certificates", 
                    "--no-playlist", 
                    video.url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    self.status, self.status_type, self.is_loading_video, self.need_redraw = "Failed to get URL", "error", False, True
                    return
                
                urls = [line.strip() for line in result.stdout.split('\n') if line.strip()]
                
                if not urls:
                    self.status, self.status_type, self.is_loading_video, self.need_redraw = "No stream URL", "error", False, True
                    return
                
                video_url = urls[0]
                audio_url = urls[1] if len(urls) > 1 else None
                
                self.is_loading_video = False
                SDL_HideWindow(self.window)
                self.is_playing = True
                self.player_paused = False
                player = self.video_player
                player_name = os.path.basename(player)
                self.mpv_socket = f"/tmp/mpv_{os.getpid()}"
                
                if player_name == "mpv":
                    player_cmd = [player, "--fs", "--no-terminal", "--really-quiet", f"--log-file={MPV_LOG_PATH}", f"--input-ipc-server={self.mpv_socket}", "--osd-level=1", "--osd-duration=1500", "--cache=yes", "--demuxer-max-bytes=50M"]
                    if audio_url:
                        player_cmd.append(f"--audio-file={audio_url}")
                    player_cmd.append(video_url)
                elif player_name == "ffplay":
                    player_cmd = [player, "-fs", "-autoexit", "-noborder", "-framedrop", "-exitonkeydown"]
                    if height and int(height) <= 480: player_cmd.extend(["-lowres", "1"])
                    player_cmd.extend(["-infbuf", "-threads", "4", "-sync", "video", video_url])
                elif player_name == "vlc":
                    player_cmd = [player, "--fullscreen", "--play-and-exit", "-q", video_url]
                    if audio_url:
                        player_cmd.extend(["--input-slave", audio_url])
                else:
                    player_cmd = [player, video_url]
                
                env = os.environ.copy()
                if 'DISPLAY' not in env: env['DISPLAY'] = ':0'
                
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

    def play_local_video(self, video):
        """Play a local download with MPV, then restart into Downloads."""
        if not self.video_player:
            self.status, self.status_type = "No video player found!", "error"
            return
        if not os.path.isfile(video.url):
            self.load_downloads()
            self.status, self.status_type = "Downloaded file is missing", "error"
            self.need_redraw = True
            return

        self.current_video = video
        self.is_loading_video = True
        self.status, self.status_type = "Opening downloaded video...", "loading"
        self.need_redraw = True

        def worker():
            try:
                player = self.video_player
                player_name = os.path.basename(player)
                self.mpv_socket = f"/tmp/mpv_{os.getpid()}"
                if player_name == "mpv":
                    player_cmd = [player, "--fs", "--no-terminal", "--really-quiet",
                                  f"--log-file={MPV_LOG_PATH}", f"--input-ipc-server={self.mpv_socket}", "--osd-level=1", "--osd-duration=1500",
                                  "--cache=yes", "--demuxer-max-bytes=50M", video.url]
                elif player_name == "ffplay":
                    player_cmd = [player, "-fs", "-autoexit", "-noborder", "-framedrop", "-exitonkeydown", video.url]
                elif player_name == "vlc":
                    player_cmd = [player, "--fullscreen", "--play-and-exit", "-q", video.url]
                else:
                    player_cmd = [player, video.url]

                env = os.environ.copy()
                if "DISPLAY" not in env: env["DISPLAY"] = ":0"
                self.is_loading_video = False
                SDL_HideWindow(self.window)
                self.is_playing = True
                self.player_paused = False
                proc = subprocess.Popen(
                    player_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL, env=env
                )
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
            except Exception as e:
                print(f"Local playback error: {e}")
                self.status, self.status_type = "Could not play downloaded video", "error"
            finally:
                self.is_loading_video = False
                self.is_playing = False
                self.player_process = None
                self.current_video = None
                self.player_paused = False
                try:
                    if self.mpv_socket and os.path.exists(self.mpv_socket): os.remove(self.mpv_socket)
                except: pass
                # Restarting releases the SDL/MPV display state completely,
                # then returns the user directly to the Downloads tab.
                if 'proc' in locals():
                    self.restart_to_downloads = True
                    self.running = False
                else:
                    SDL_ShowWindow(self.window)
                    SDL_RaiseWindow(self.window)
                    self.need_redraw = True

        threading.Thread(target=worker, daemon=True).start()

    def _save_download_thumbnail(self, video, saved_path):
        """Save the displayed YouTube thumbnail beside a completed download."""
        if not video.thumbnail or not saved_path:
            return
        thumbnail_path = os.path.splitext(saved_path)[0] + ".jpg"
        temp_path = thumbnail_path + ".part"
        try:
            # YouTube's stable JPG endpoint avoids saving a WebP file with a
            # .jpg extension on SDL builds that do not support WebP.
            thumbnail_url = f"https://i.ytimg.com/vi/{video.id}/hqdefault.jpg" if video.id else video.thumbnail
            thumbnail_url = "https:" + thumbnail_url if thumbnail_url.startswith("//") else thumbnail_url
            request = urllib.request.Request(thumbnail_url, headers={"User-Agent": "Mozilla/5.0"})
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            with urllib.request.urlopen(request, timeout=20, context=context) as response:
                with open(temp_path, "wb") as output:
                    output.write(response.read())
            os.replace(temp_path, thumbnail_path)
        except Exception as e:
            print(f"Could not save download thumbnail: {e}")
            try:
                if os.path.exists(temp_path): os.remove(temp_path)
            except: pass

    def download_video(self, video, quality=None):
        """Download the selected video as an MP4 when the source offers one."""
        if not self.ytdlp_path:
            self.status, self.status_type = "yt-dlp not found!", "error"
            return

        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        self.current_video = video
        self.is_downloading = True
        self.cancel_requested = False
        self.download_progress, self.download_size_text = 0, ""
        self.status, self.status_type = "Downloading...", "loading"
        self.need_redraw = True

        height = (quality or self.settings.get("quality", "720p")).replace("p", "")
        # YouTube's combined MP4 streams are commonly limited to 360p.
        # Higher qualities have separate video/audio tracks and must be merged.
        if FFMPEG_PATH:
            format_str = f"bv*[height<={height}][vcodec^=avc]+ba[ext=m4a]/bv*[height<={height}]+ba"
        else:
            if int(height) > 360:
                self.status, self.status_type = f"{height}p download needs ffmpeg", "error"
                self.current_video = None
                self.is_downloading = False
                self.need_redraw = True
                return
            format_str = "b[height<=360][ext=mp4]/b[height<=360]"
        output_template = os.path.join(DOWNLOAD_DIR, "%(title).120B [%(id)s].%(ext)s")

        def worker():
            try:
                cmd = [
                    self.ytdlp_path,
                    "--no-playlist",
                    "--no-check-certificates",
                    "--restrict-filenames",
                    "--newline",
                    "--progress-template", "download:%(progress._percent_str)s|%(progress._downloaded_bytes_str)s|%(progress._total_bytes_str)s",
                    "--print", "after_move:filepath",
                    "-f", format_str,
                    "-o", output_template,
                    video.url,
                ]
                if FFMPEG_PATH:
                    cmd[1:1] = ["--ffmpeg-location", FFMPEG_PATH, "--merge-output-format", "mp4"]
                self.active_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
                lines = []
                for line in self.active_process.stdout:
                    line = line.strip()
                    if line.startswith("download:"):
                        parts = line.split(":", 1)[1].split("|")
                        try: self.download_progress = int(float(parts[0].replace("%", "").strip()))
                        except: pass
                        self.download_size_text = " / ".join(part.strip() for part in parts[1:] if part.strip())
                    elif line: lines.append(line)
                result_code = self.active_process.wait(timeout=1800)
                self.active_process = None
                if result_code == 0 and not self.cancel_requested:
                    lines = [line for line in lines if not line.startswith("[download]")]
                    saved_path = lines[-1] if lines else ""
                    if saved_path: self._save_download_thumbnail(video, saved_path)
                    name = os.path.basename(saved_path) if saved_path else "complete"
                    self.status, self.status_type = f"Downloaded: {name}", "ok"
                else:
                    output = "\n".join(lines)
                    print("Download failed:", output)
                    if self.cancel_requested:
                        self.status = "Download cancelled"
                    elif "Too Many Requests" in output or "not a bot" in output:
                        self.status = "YouTube blocked request (429)"
                    elif "JavaScript runtime" in output:
                        self.status = "yt-dlp needs a JS runtime"
                    else:
                        self.status = "Download failed"
                    self.status_type = "error"
            except subprocess.TimeoutExpired:
                self.status, self.status_type = "Download timed out", "error"
            except Exception as e:
                print(f"Download error: {e}")
                self.status, self.status_type = "Download failed", "error"
            finally:
                self.active_process = None
                self.is_downloading = False
                self.current_video = None
                self.load_downloads()
                self.need_redraw = True

        threading.Thread(target=worker, daemon=True).start()

    def get_mpv_property(self, prop):
        if not self.is_playing or not hasattr(self, 'mpv_socket') or not self.mpv_socket: return "?"
        try:
            import socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.2)
            sock.connect(self.mpv_socket)
            cmd = {"command": ["get_property", prop]}
            sock.send((json.dumps(cmd) + "\n").encode())
            data = sock.recv(4096).decode()
            sock.close()
            for line in data.split('\n'):
                if line.strip():
                    resp = json.loads(line)
                    if "data" in resp: return str(resp["data"])
            return "?"
        except: return "?"

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
        self.restore_app_window()
        self.status, self.status_type, self.need_redraw = "Stopped", "ok", True

    def restore_app_window(self):
        """Restore SDL after MPV releases its fullscreen video surface."""
        self.restore_window_requested = False
        SDL_ShowWindow(self.window)
        SDL_SetWindowSize(self.window, self.screen_width, self.screen_height)
        SDL_SetWindowPosition(self.window, SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED)
        SDL_RaiseWindow(self.window)
        SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255)
        SDL_RenderClear(self.renderer)
        SDL_RenderPresent(self.renderer)
        self.need_redraw = True

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
        is_local_file = os.path.isfile(url)
        cache_path = url if is_local_file else self.get_thumb_path(url)
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
        if not is_local_file and url not in self.loading_images: self.download_thumbnail(url)
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
        self.draw_rect(0, 0, self.screen_width, 50, Colors.BG_PRIMARY)
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
        self.draw_rect(0, 49, self.screen_width, 1, Colors.DIVIDER)

    def render_navigation(self):
        nav_y = self.screen_height - 55
        help_y = nav_y - 18
        self.draw_rect(0, help_y, self.screen_width, 18, Colors.BG_SECONDARY)
        help_text = self.t("help_keyboard") if self.search_active else self.t("help_main")
        self.draw_text(help_text, self.screen_width//2 - len(help_text)*3, help_y + 3, Colors.TEXT_TERTIARY, self.font_tiny)
        self.draw_rect(0, nav_y, self.screen_width, 55, Colors.NAV_BG)
        self.draw_rect(0, nav_y, self.screen_width, 1, Colors.DIVIDER)
        items = [("home", self.t("nav_home"), NAV_HOME), ("search", self.t("nav_search"), NAV_SEARCH),
                 ("favorites", self.t("nav_favorites"), NAV_FAVORITES), ("history", self.t("nav_history"), NAV_HISTORY),
                 ("downloads", self.t("nav_downloads"), NAV_DOWNLOADS),
                 ("settings", self.t("nav_settings"), NAV_SETTINGS)]
        item_w = self.screen_width // len(items)
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
            elif icon_type == "downloads":
                self.draw_rect(cx - 1, icon_y, 2, 9, icon_color)
                self.draw_rect(cx - 4, icon_y + 6, 8, 2, icon_color)
                self.draw_rect(cx - 2, icon_y + 8, 4, 2, icon_color)
                self.draw_rect(cx - 7, icon_y + 12, 14, 2, icon_color)
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
        h = self.screen_height - 55 - 73
        if self.current_nav == NAV_SETTINGS: self.render_settings(y, h); return
        if self.is_searching: self.render_searching(y); return
        if self.current_nav == NAV_SEARCH and not self.search_results:
            self.render_genre_browser(y, h)
            return
        videos = self._get_list()
        if videos: self.render_video_list(videos, y, h)
        else: self.render_empty(y)

    def render_genre_browser(self, start_y, height):
        self.draw_text("Browse YouTube genres", 20, start_y + 12, Colors.TEXT_PRIMARY, self.font_large)
        self.draw_text("A: Today's trending   X: Text search", 20, start_y + 42, Colors.TEXT_TERTIARY, self.font_tiny)
        columns, gap, margin = 3, 10, 16
        button_w = (self.screen_width - margin * 2 - gap * (columns - 1)) // columns
        button_h = 54
        for index, genre in enumerate(SEARCH_GENRES):
            row, col = divmod(index, columns)
            x = margin + col * (button_w + gap)
            y = start_y + 68 + row * (button_h + gap)
            selected = index == self.selected
            self.draw_rect(x, y, button_w, button_h, Colors.YT_RED if selected else Colors.CARD_BG)
            if not selected:
                self.draw_rect(x, y, button_w, 1, Colors.DIVIDER)
                self.draw_rect(x, y + button_h - 1, button_w, 1, Colors.DIVIDER)
            self.draw_text(genre, x + button_w // 2 - len(genre) * 4, y + 18,
                           Colors.TEXT_PRIMARY if selected else Colors.TEXT_SECONDARY, self.font)

    def render_searching(self, y):
        msg = self.t("msg_searching")
        self.draw_text(msg, self.screen_width//2 - len(msg)*5, y + 100, Colors.TEXT_SECONDARY, self.font)
        if hasattr(self, 'last_search_query') and self.last_search_query:
            query_text = f'"{self.last_search_query}"'
            if len(query_text) > 35: query_text = query_text[:32] + '..."'
            self.draw_text(query_text, self.screen_width//2 - len(query_text)*4, y + 130, Colors.TEXT_TERTIARY, self.font_small)
        self.draw_spinner(self.screen_width // 2, y + 190, radius=14, dot_size=4)

    def render_empty(self, y):
        if self.current_nav == NAV_DOWNLOADS:
            msg = "No downloaded videos"
            detail = "Downloads are saved in MuTube/downloads"
            self.draw_text(msg, self.screen_width//2 - len(msg)*5, y + 100, Colors.TEXT_SECONDARY, self.font)
            self.draw_text(detail, self.screen_width//2 - len(detail)*3, y + 130, Colors.TEXT_TERTIARY, self.font_tiny)
            return
        msg = self.t("msg_press_search")
        if not self.ytdlp_path: msg = self.t("msg_no_ytdlp")
        elif not self.video_player: msg = self.t("msg_no_player")
        self.draw_text(msg, self.screen_width//2 - len(msg)*5, y + 100, Colors.TEXT_SECONDARY, self.font)
        if not self.ytdlp_path: self.draw_text(self.t("msg_install_ytdlp"), 150, y + 140, Colors.TEXT_TERTIARY, self.font_tiny)
        if not self.video_player: self.draw_text(self.t("msg_install_player"), 170, y + 160, Colors.TEXT_TERTIARY, self.font_tiny)
        if self.current_nav == NAV_HOME and (self.is_loading or self.home_batch_loading):
            self.draw_spinner(self.screen_width // 2, y + 200, radius=12, dot_size=3)
            self.draw_text(self.t("msg_loading_videos"), self.screen_width // 2 - 55, y + 230, Colors.TEXT_TERTIARY, self.font_small)

    def render_settings(self, start_y, height):
        self.draw_text(self.t("settings_title"), 20, start_y + 10, Colors.TEXT_PRIMARY, self.font_large)
        self.draw_text("By: Ronax", self.screen_width - 105, start_y + 12, Colors.TEXT_PRIMARY, self.font_small)
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
                self.draw_rect(15, y, self.screen_width - 30, item_h, Colors.CARD_SELECTED)
                self.draw_rect(15, y, 4, item_h, Colors.YT_RED)
            else: self.draw_rect(15, y, self.screen_width - 30, item_h, Colors.CARD_BG)
            self.draw_text(label, 30, y + 15, Colors.TEXT_PRIMARY if selected else Colors.TEXT_SECONDARY, self.font)
            if options is None: self.draw_text(self.t("settings_execute"), self.screen_width - 130, y + 15, Colors.YT_RED, self.font_small)
            else:
                current = self.settings.get(key, options[0])
                self.draw_text(f"< {current} >", self.screen_width - 130, y + 15, Colors.TEXT_PRIMARY if selected else Colors.TEXT_TERTIARY, self.font)
            y += item_h + margin
        if len(self.settings_items) > visible_count:
            sb_height = list_height
            thumb_height = max(20, int(sb_height * visible_count / len(self.settings_items)))
            thumb_y = list_start_y + int((sb_height - thumb_height) * self.settings_scroll / max(1, len(self.settings_items) - visible_count))
            self.draw_rect(self.screen_width - 8, list_start_y, 4, sb_height, Colors.PROGRESS_BG)
            self.draw_rect(self.screen_width - 8, thumb_y, 4, thumb_height, Colors.YT_RED)

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
        if key == "update_ytdlp":
            self.update_dependencies(["yt-dlp"])
        elif key == "update_ffmpeg":
            self.update_dependencies(["ffmpeg"])
        elif key == "update_all":
            self.update_dependencies(["yt-dlp", "ffmpeg"])
        elif key == "refresh_home":
            if self.ytdlp_path:
                self.current_nav = NAV_HOME
                self.selected = self.scroll = 0
                self.load_trending()
            else:
                self.status, self.status_type = "yt-dlp not found!", "error"
        elif key == "clear_favorites":
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
        elif key == "show_credits":
            self.credits_active = True
        self.need_redraw = True

    def _download_file(self, url, destination, label):
        """Download one dependency while exposing a device-friendly progress value."""
        request = urllib.request.Request(url, headers={"User-Agent": "MuTube/1.2"})
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(request, timeout=45, context=context) as response:
            total = int(response.headers.get("Content-Length", "0") or 0)
            received = 0
            with open(destination, "wb") as output:
                while True:
                    if self.cancel_requested:
                        raise RuntimeError("Update cancelled")
                    block = response.read(64 * 1024)
                    if not block: break
                    output.write(block)
                    received += len(block)
                    self.update_label = label
                    self.update_progress = int(received * 100 / total) if total else 0
                    self.update_size_text = f"{received / (1024 * 1024):.1f} MB" + (f" / {total / (1024 * 1024):.1f} MB" if total else "")

    def update_dependencies(self, requested):
        if self.is_updating: return
        self.is_updating, self.cancel_requested = True, False
        self.update_progress, self.update_size_text = 0, ""
        self.update_label = "Preparing update..."
        self.need_redraw = True

        def worker():
            global YTDLP_PATH, FFMPEG_PATH
            temp_files = []
            try:
                if "yt-dlp" in requested:
                    target = os.path.join(SCRIPT_DIR, "yt-dlp")
                    temporary = target + ".download"
                    temp_files.append(temporary)
                    self._download_file("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp_linux_aarch64", temporary, "Downloading yt-dlp")
                    os.replace(temporary, target)
                    os.chmod(target, 0o755)
                    YTDLP_PATH = self.ytdlp_path = find_ytdlp()
                if "ffmpeg" in requested:
                    archive = os.path.join(SCRIPT_DIR, "ffmpeg.download.tar.xz")
                    temp_files.append(archive)
                    self._download_file("https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-arm64-static.tar.xz", archive, "Downloading FFmpeg")
                    self.update_label, self.update_progress, self.update_size_text = "Installing FFmpeg", 100, ""
                    with tarfile.open(archive, "r:xz") as bundle:
                        member = next((item for item in bundle.getmembers() if item.name.endswith("/ffmpeg") and item.isfile()), None)
                        if not member: raise RuntimeError("FFmpeg binary was not found in the archive")
                        source = bundle.extractfile(member)
                        if source is None: raise RuntimeError("Could not unpack FFmpeg")
                        temporary = os.path.join(SCRIPT_DIR, "ffmpeg.download")
                        temp_files.append(temporary)
                        with open(temporary, "wb") as output: shutil.copyfileobj(source, output)
                    os.replace(temporary, os.path.join(SCRIPT_DIR, "ffmpeg"))
                    os.chmod(os.path.join(SCRIPT_DIR, "ffmpeg"), 0o755)
                    FFMPEG_PATH = find_ffmpeg()
                self.status, self.status_type = "Dependencies ready", "ok"
            except Exception as exc:
                print(f"Dependency update failed: {exc}")
                self.status, self.status_type = f"Update failed: {str(exc)[:28]}", "error"
            finally:
                for path in temp_files:
                    try:
                        if os.path.exists(path): os.remove(path)
                    except: pass
                self.is_updating = False
                self.dependency_prompt_active = False
                self.need_redraw = True
        threading.Thread(target=worker, daemon=True).start()

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
            self.draw_rect(10, y, self.screen_width - 20, card_h, Colors.CARD_SELECTED if selected else Colors.CARD_BG)
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
            self.draw_rect(10, spinner_card_y, self.screen_width - 20, card_h, Colors.BG_SECONDARY)
            self.draw_spinner(self.screen_width // 2, spinner_card_y + card_h // 2 - 5, radius=12, dot_size=3)
            self.draw_text(self.t("msg_loading"), self.screen_width // 2 - 35, spinner_card_y + card_h // 2 + 18, Colors.TEXT_TERTIARY, self.font_small)
        if len(videos) > base_visible:
            sb_h = height
            thumb = max(20, int(sb_h * visible / len(videos)))
            thumb_y = start_y + int((sb_h - thumb) * self.scroll / max(1, len(videos) - visible))
            self.draw_rect(self.screen_width - 8, start_y, 4, sb_h, Colors.PROGRESS_BG)
            self.draw_rect(self.screen_width - 8, thumb_y, 4, thumb, Colors.YT_RED)

    def render_keyboard(self):
        base_kb_y = self.screen_height - 260
        num_rows = len(self.keyboard_layout)
        if num_rows > 4: base_kb_y -= (num_rows - 4) * 38
        kb_y = base_kb_y
        self.draw_rect(0, kb_y - 45, self.screen_width, self.screen_height - kb_y + 45, (0, 0, 0), 240)
        input_y = kb_y - 38
        self.draw_rect(15, input_y, self.screen_width - 30, 32, Colors.BG_TERTIARY)
        self.draw_rect(15, input_y, self.screen_width - 30, 2, Colors.YT_RED)
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
        available_width = self.screen_width - (2 * side_margin)
        key_w = (available_width - (max_keys - 1) * gap) // max_keys
        key_h = 34
        for row_i, row in enumerate(layout):
            row_width = len(row) * key_w + (len(row) - 1) * gap
            row_offset = (self.screen_width - row_width) // 2
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
        ctrl_x = (self.screen_width - total_ctrl_w) // 2
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
        if self.current_nav == NAV_DOWNLOADS: return self.downloaded_videos
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
        if self.current_nav == NAV_SEARCH and not self.search_results and not self.search_active:
            self.selected = max(0, self.selected - 3)
            self.need_redraw = True
            return
        if self.selected > 0:
            self.selected -= 1
            self.need_redraw = True

    def action_down(self):
        if self.current_nav == NAV_SEARCH and not self.search_results and not self.search_active:
            self.selected = min(len(SEARCH_GENRES) - 1, self.selected + 3)
            self.need_redraw = True
            return
        videos = self._get_list()
        if self.selected < len(videos) - 1:
            self.selected += 1
            self.need_redraw = True
            self.check_load_next_batch()

    def action_left(self):
        if self.current_nav == NAV_SEARCH and not self.search_results and not self.search_active:
            self.selected = max(0, self.selected - 1)
            self.need_redraw = True
            return
        self.switch_tab(-1)

    def action_right(self):
        if self.current_nav == NAV_SEARCH and not self.search_results and not self.search_active:
            self.selected = min(len(SEARCH_GENRES) - 1, self.selected + 1)
            self.need_redraw = True
            return
        self.switch_tab(1)

    def switch_tab(self, direction):
        self.current_nav = (self.current_nav + direction) % 6
        if self.current_nav == NAV_DOWNLOADS: self.load_downloads()
        self.selected = self.scroll = 0
        self.loading_spinner_triggered = False
        self.need_redraw = True

    def action_select(self):
        if self.current_nav == NAV_SEARCH and not self.search_results:
            genre = SEARCH_GENRES[min(self.selected, len(SEARCH_GENRES) - 1)]
            self.search_youtube(f"{genre} trending videos today")
        else:
            videos = self._get_list()
            if videos and self.selected < len(videos):
                video = videos[self.selected]
                if getattr(video, "is_local", False):
                    self.play_local_video(video)
                elif self.settings.get("a_button_action", "Play") == "Download":
                    self.download_video(video)
                else:
                    self.play_video(video)
        self.need_redraw = True

    def action_back(self):
        if self.exit_confirm_active:
            self.exit_confirm_active = False
            self.exit_confirm_selection = 0
        elif self.search_active: self.search_active = False
        elif self.current_nav == NAV_SEARCH and self.search_results:
            self.search_results = []
            self.last_search_query = ""
            self.selected = self.scroll = 0
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

    def download_selected(self, quality=None):
        videos = self._get_list()
        if not videos or self.selected >= len(videos):
            return
        video = videos[self.selected]
        if getattr(video, "is_local", False):
            self.status, self.status_type, self.need_redraw = "This video is already downloaded", "ok", True
            return
        self.download_video(video, quality)

    def open_action_popup(self):
        videos = self._get_list()
        if not videos or self.selected >= len(videos):
            return
        self.action_popup_video = videos[self.selected]
        self.action_popup_selection = 0
        self.action_popup_active = True
        self.need_redraw = True

    def _popup_choices(self):
        if self.action_popup_video and getattr(self.action_popup_video, "is_local", False):
            return ["Play", "Delete", "Details", "Move to Media", "Copy to Media"]
        return ["Play", "Download 1080p", "Download 720p", "Download 480p", "Download 360p"]

    def _media_directory(self):
        preferred = "/mnt/sdcard" if self.settings.get("media_target") == "SD Card" else "/mnt/mmc"
        root = preferred if os.path.isdir(preferred) else "/mnt/mmc"
        return os.path.join(root, "ROMS", "Media")

    def _local_video_resolution(self, path):
        if not FFMPEG_PATH: return "Unknown"
        try:
            probe = subprocess.run([FFMPEG_PATH, "-i", path], capture_output=True, text=True, timeout=12)
            match = re.search(r"(\\d{3,5})x(\\d{3,5})", probe.stderr)
            return f"{match.group(1)}x{match.group(2)}" if match else "Unknown"
        except: return "Unknown"

    def _transfer_local_video(self, video, move=False):
        destination_dir = self._media_directory()
        try:
            os.makedirs(destination_dir, exist_ok=True)
            destination = os.path.join(destination_dir, os.path.basename(video.url))
            if os.path.exists(destination):
                self.status, self.status_type = "File already exists in Media", "error"
                return
            if move: shutil.move(video.url, destination)
            else: shutil.copy2(video.url, destination)
            thumbnail = os.path.splitext(video.url)[0] + ".jpg"
            if os.path.isfile(thumbnail):
                thumb_destination = os.path.splitext(destination)[0] + ".jpg"
                if move: shutil.move(thumbnail, thumb_destination)
                else: shutil.copy2(thumbnail, thumb_destination)
            self.status, self.status_type = ("Moved to Media" if move else "Copied to Media"), "ok"
            self.load_downloads()
        except Exception as e:
            print(f"Media transfer error: {e}")
            self.status, self.status_type = "Media transfer failed", "error"

    def _delete_local_video(self, video):
        try:
            os.remove(video.url)
            thumbnail = os.path.splitext(video.url)[0] + ".jpg"
            if os.path.isfile(thumbnail): os.remove(thumbnail)
            self.status, self.status_type = "Deleted", "ok"
            self.load_downloads()
        except Exception as e:
            print(f"Delete error: {e}")
            self.status, self.status_type = "Delete failed", "error"

    def confirm_action_popup(self):
        video = self.action_popup_video
        choice = self.action_popup_selection
        self.action_popup_active = False
        self.action_popup_video = None
        if not video:
            return
        if getattr(video, "is_local", False):
            if choice == 0: self.play_local_video(video)
            elif choice == 1: self._delete_local_video(video)
            elif choice == 2:
                self.file_details_video = video
                self.file_details_active = True
            elif choice == 3: self._transfer_local_video(video, move=True)
            elif choice == 4: self._transfer_local_video(video, move=False)
        elif choice == 0:
            self.play_video(video)
        else:
            self.download_video(video, ["1080p", "720p", "480p", "360p"][choice - 1])
        self.need_redraw = True

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
        if self.is_loading_video or self.is_downloading or self.is_updating:
            cancelled = ((event.type == SDL_CONTROLLERBUTTONDOWN and event.cbutton.button == SDL_CONTROLLER_BUTTON_B) or
                         (event.type == SDL_KEYDOWN and event.key.keysym.sym in (SDLK_ESCAPE, SDLK_x)))
            if cancelled:
                self.cancel_requested = True
                if self.active_process:
                    try: self.active_process.terminate()
                    except: pass
                self.is_loading_video = self.is_downloading = False
                self.status, self.status_type, self.need_redraw = "Cancelled", "ok", True
            return

        if self.dependency_prompt_active:
            if event.type == SDL_CONTROLLERBUTTONDOWN:
                if event.cbutton.button == SDL_CONTROLLER_BUTTON_A: self.update_dependencies(["yt-dlp", "ffmpeg"])
                elif event.cbutton.button == SDL_CONTROLLER_BUTTON_B: self.dependency_prompt_active = False
                self.need_redraw = True
            elif event.type == SDL_KEYDOWN:
                if event.key.keysym.sym in (SDLK_RETURN, SDLK_z): self.update_dependencies(["yt-dlp", "ffmpeg"])
                elif event.key.keysym.sym in (SDLK_ESCAPE, SDLK_x): self.dependency_prompt_active = False
                self.need_redraw = True
            return

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
        if self.credits_active:
            if event.type == SDL_CONTROLLERBUTTONDOWN:
                self.credits_active = False
                self.need_redraw = True
            elif event.type == SDL_KEYDOWN:
                self.credits_active = False
                self.need_redraw = True
            return
        if self.file_details_active:
            if event.type == SDL_CONTROLLERBUTTONDOWN:
                if event.cbutton.button in (SDL_CONTROLLER_BUTTON_A, SDL_CONTROLLER_BUTTON_B):
                    self.file_details_active = False
                    self.file_details_video = None
                    self.need_redraw = True
            elif event.type == SDL_KEYDOWN:
                if event.key.keysym.sym in (SDLK_RETURN, SDLK_z, SDLK_ESCAPE, SDLK_x):
                    self.file_details_active = False
                    self.file_details_video = None
                    self.need_redraw = True
            return
        if self.action_popup_active:
            if event.type == SDL_CONTROLLERBUTTONDOWN:
                btn = event.cbutton.button
                if btn == SDL_CONTROLLER_BUTTON_DPAD_UP:
                    self.action_popup_selection = (self.action_popup_selection - 1) % len(self._popup_choices())
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_DOWN:
                    self.action_popup_selection = (self.action_popup_selection + 1) % len(self._popup_choices())
                elif btn == SDL_CONTROLLER_BUTTON_A:
                    self.confirm_action_popup()
                elif btn == SDL_CONTROLLER_BUTTON_B:
                    self.action_popup_active = False
                    self.action_popup_video = None
                self.need_redraw = True
            elif event.type == SDL_KEYDOWN:
                key = event.key.keysym.sym
                if key in (SDLK_UP, SDLK_w): self.action_popup_selection = (self.action_popup_selection - 1) % len(self._popup_choices())
                elif key in (SDLK_DOWN, SDLK_s): self.action_popup_selection = (self.action_popup_selection + 1) % len(self._popup_choices())
                elif key in (SDLK_RETURN, SDLK_z): self.confirm_action_popup()
                elif key in (SDLK_ESCAPE, SDLK_x):
                    self.action_popup_active = False
                    self.action_popup_video = None
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
                
                elif btn == SDL_CONTROLLER_BUTTON_X:
                    w = self.get_mpv_property("width")
                    h = self.get_mpv_property("height")
                    fmt = self.get_mpv_property("video-format")
                    if w != "?" and h != "?":
                        msg = f"Res: {w}x{h} ({fmt})"
                        self.send_mpv_command(["show-text", msg, "3000"])
                    else:
                        self.send_mpv_command(["script-binding", "stats/display-stats-toggle"])

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
                elif btn == SDL_CONTROLLER_BUTTON_LEFTSHOULDER: self.switch_tab(-1)
                elif btn == SDL_CONTROLLER_BUTTON_RIGHTSHOULDER: self.switch_tab(1)
                return

            if btn == SDL_CONTROLLER_BUTTON_A:
                # Defer the short-press action until button release so a long
                # press can open the quality chooser instead.
                self.a_button_down_at = now
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
            elif btn == SDL_CONTROLLER_BUTTON_LEFTSHOULDER: self.switch_tab(-1)
            elif btn == SDL_CONTROLLER_BUTTON_RIGHTSHOULDER: self.switch_tab(1)
            elif btn == SDL_CONTROLLER_BUTTON_START: self.download_selected()
        elif event.type == SDL_CONTROLLERBUTTONUP:
            if event.cbutton.button == SDL_CONTROLLER_BUTTON_A and self.a_button_down_at is not None:
                held_ms = now - self.a_button_down_at
                self.a_button_down_at = None
                if held_ms >= 600: self.open_action_popup()
                else: self.action_select()
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
        self.draw_rect(0, 0, self.screen_width, self.screen_height, Colors.BG_PRIMARY)
        self.render_header()
        
        if self.dependency_prompt_active:
            self.render_dependency_prompt()
            self.need_redraw = False
            return
        if self.exit_confirm_active:
            self.render_content()
            self.render_navigation()
            self.render_exit_confirm()
        elif self.credits_active:
            self.render_content()
            self.render_navigation()
            self.render_credits_popup()
        elif self.action_popup_active:
            self.render_content()
            self.render_navigation()
            self.render_action_popup()
        elif self.file_details_active:
            self.render_content()
            self.render_navigation()
            self.render_file_details_popup()
        elif self.search_active:
            self.render_keyboard()
        else:
            self.render_content()
        
        self.render_navigation()
        SDL_RenderPresent(self.renderer)
        self.need_redraw = False
        self.frame_count += 1

    def run(self):
        if self.start_in_downloads:
            self.load_downloads()
            self.status, self.status_type = "Downloads", "ok"
            # Stay on Downloads after local playback, while the Home feed is
            # rebuilt asynchronously for when the user returns to it.
            if self.ytdlp_path:
                self.load_trending()
        elif self.ytdlp_path:
            self.load_trending()
        else:
            # The app remains useful without a network/downloader when it has
            # locally saved videos.
            self.show_downloads_offline()
        if not self.ytdlp_path or not FFMPEG_PATH:
            self.dependency_prompt_active = True
        event = SDL_Event()
        last_render_time = 0
        while self.running:
            if self.restore_window_requested:
                self.restore_app_window()
            while SDL_PollEvent(event):
                if event.type == SDL_QUIT: self.running = False
                else: self.handle_event(event)
            self.process_repeat()
            current_time = SDL_GetTicks()
            if self.is_loading_video: self.render_loading_screen(self.t("msg_loading_video"), self.current_video.title if self.current_video else "")
            elif self.is_downloading: self.render_download_progress("Downloading...", self.current_video.title if self.current_video else "", self.download_progress, self.download_size_text)
            elif self.is_updating: self.render_download_progress(self.update_label or "Updating...", "", self.update_progress, self.update_size_text)
            elif not self.is_playing:
                is_batch_loading = self.home_batch_loading or self.search_batch_loading
                force_render = (current_time - last_render_time) >= 100
                if self.need_redraw or self.is_loading or self.loading_images or is_batch_loading or self.is_searching or force_render:
                    self.render()
                    last_render_time = current_time
            SDL_Delay(16)
        self.cleanup()
        if self.restart_to_downloads:
            restart_env = os.environ.copy()
            restart_env["MUTUBE_START_TAB"] = "downloads"
            os.execvpe(sys.executable, [sys.executable, os.path.abspath(__file__)], restart_env)

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
    
    if "APP_SCREEN_WIDTH" in os.environ:
        try:
            SCREEN_WIDTH = int(os.environ["APP_SCREEN_WIDTH"])
            print(f"Overriding SCREEN_WIDTH from env: {SCREEN_WIDTH}")
        except ValueError:
            print(f"Invalid APP_SCREEN_WIDTH in env: {os.environ['APP_SCREEN_WIDTH']}")

    if "APP_SCREEN_HEIGHT" in os.environ:
        try:
            SCREEN_HEIGHT = int(os.environ["APP_SCREEN_HEIGHT"])
            print(f"Overriding SCREEN_HEIGHT from env: {SCREEN_HEIGHT}")
        except ValueError:
            print(f"Invalid APP_SCREEN_HEIGHT in env: {os.environ['APP_SCREEN_HEIGHT']}")

    try:
        app = YouTubeApp()
        app.run()
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
