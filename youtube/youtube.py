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
        # Navigation
        "nav_home": "Home",
        "nav_search": "Search",
        "nav_favorites": "Favs",
        "nav_history": "History",
        "nav_settings": "Settings",
        # Settings
        "settings_title": "Settings",
        "settings_language": "Language",
        "settings_quality": "Video Quality",
        "settings_search_count": "Search Count",
        "settings_auto_load": "Auto Load Home",
        "settings_clear_favorites": "Clear Favorites",
        "settings_clear_history": "Clear History",
        "settings_clear_cache": "Clear Thumb Cache",
        "settings_execute": "[A] Execute",
        "settings_on": "On",
        "settings_off": "Off",
        # Messages
        "msg_searching": "Searching videos...",
        "msg_loading": "Loading...",
        "msg_loading_video": "Loading Video...",
        "msg_loading_videos": "Loading videos...",
        "msg_no_results": "No results",
        "msg_press_search": "Press X to search",
        "msg_no_ytdlp": "yt-dlp not found!",
        "msg_no_player": "No video player!",
        "msg_install_ytdlp": "Install: pip install yt-dlp",
        "msg_install_player": "Install: mpv or ffplay",
        "msg_timeout": "Timeout",
        "msg_added_fav": "Added to favorites",
        "msg_removed_fav": "Removed from favorites",
        "msg_fav_cleared": "Favorites cleared",
        "msg_history_cleared": "History cleared",
        "msg_cache_cleared": "Cache cleared",
        "msg_videos": "videos",
        # Help
        "help_keyboard": "A:Type  B:Close  START:Search",
        "help_main": "A:Select  B:Back  X:Search  Y:Fav  L/R:Tab",
        # Keyboard
        "kb_space": "SPACE",
        "kb_go": "GO",
        "kb_search_placeholder": "Type to search...",
        # Time
        "time_today": "Today",
        "time_live": "LIVE",
        "exit_confirm_title": "Are you sure you want to exit?",
        "exit_confirm_yes": "Yes",
        "exit_confirm_no": "No",
        "exit_confirm_help": "[<>] Select [A] Confirm [B] Cancel",
    },
    "Turkce": {
        # Navigation
        "nav_home": "Ana",
        "nav_search": "Ara",
        "nav_favorites": "Fav",
        "nav_history": "Gecmis",
        "nav_settings": "Ayarlar",
        # Settings
        "settings_title": "Ayarlar",
        "settings_language": "Dil",
        "settings_quality": "Video Kalitesi",
        "settings_search_count": "Arama Sayisi",
        "settings_auto_load": "Otomatik Yukle",
        "settings_clear_favorites": "Favorileri Temizle",
        "settings_clear_history": "Gecmisi Temizle",
        "settings_clear_cache": "Onbellek Temizle",
        "settings_execute": "[A] Calistir",
        "settings_on": "Acik",
        "settings_off": "Kapali",
        # Messages
        "msg_searching": "Videolar araniyor...",
        "msg_loading": "Yukleniyor...",
        "msg_loading_video": "Video Yukleniyor...",
        "msg_loading_videos": "Videolar yukleniyor...",
        "msg_no_results": "Sonuc yok",
        "msg_press_search": "Aramak icin X'e bas",
        "msg_no_ytdlp": "yt-dlp bulunamadi!",
        "msg_no_player": "Video oynatici yok!",
        "msg_install_ytdlp": "Kur: pip install yt-dlp",
        "msg_install_player": "Kur: mpv veya ffplay",
        "msg_timeout": "Zaman asimi",
        "msg_added_fav": "Favorilere eklendi",
        "msg_removed_fav": "Favorilerden cikarildi",
        "msg_fav_cleared": "Favoriler temizlendi",
        "msg_history_cleared": "Gecmis temizlendi",
        "msg_cache_cleared": "Onbellek temizlendi",
        "msg_videos": "video",
        # Help
        "help_keyboard": "A:Yaz  B:Kapat  START:Ara",
        "help_main": "A:Sec  B:Geri  X:Ara  Y:Fav  L/R:Sekme",
        # Keyboard
        "kb_space": "BOSLUK",
        "kb_go": "GIT",
        "kb_search_placeholder": "Aramak icin yaz...",
        # Time
        "time_today": "Bugun",
        "time_live": "CANLI",
        "exit_confirm_title": "Cikmak istediginize emin misiniz?",
        "exit_confirm_yes": "Evet",
        "exit_confirm_no": "Hayir",
        "exit_confirm_help": "[<>] Sec [A] Onayla [B] Iptal",
    },
    "Espanol": {
        # Navigation
        "nav_home": "Inicio",
        "nav_search": "Buscar",
        "nav_favorites": "Favs",
        "nav_history": "Historial",
        "nav_settings": "Ajustes",
        # Settings
        "settings_title": "Ajustes",
        "settings_language": "Idioma",
        "settings_quality": "Calidad Video",
        "settings_search_count": "Cant. Busqueda",
        "settings_auto_load": "Carga Auto",
        "settings_clear_favorites": "Borrar Favoritos",
        "settings_clear_history": "Borrar Historial",
        "settings_clear_cache": "Borrar Cache",
        "settings_execute": "[A] Ejecutar",
        "settings_on": "Si",
        "settings_off": "No",
        # Messages
        "msg_searching": "Buscando videos...",
        "msg_loading": "Cargando...",
        "msg_loading_video": "Cargando Video...",
        "msg_loading_videos": "Cargando videos...",
        "msg_no_results": "Sin resultados",
        "msg_press_search": "Pulsa X para buscar",
        "msg_no_ytdlp": "yt-dlp no encontrado!",
        "msg_no_player": "Sin reproductor!",
        "msg_install_ytdlp": "Instalar: pip install yt-dlp",
        "msg_install_player": "Instalar: mpv o ffplay",
        "msg_timeout": "Tiempo agotado",
        "msg_added_fav": "Agregado a favoritos",
        "msg_removed_fav": "Quitado de favoritos",
        "msg_fav_cleared": "Favoritos borrados",
        "msg_history_cleared": "Historial borrado",
        "msg_cache_cleared": "Cache borrado",
        "msg_videos": "videos",
        # Help
        "help_keyboard": "A:Escribir  B:Cerrar  START:Buscar",
        "help_main": "A:Elegir  B:Atras  X:Buscar  Y:Fav  L/R:Tab",
        # Keyboard
        "kb_space": "ESPACIO",
        "kb_go": "IR",
        "kb_search_placeholder": "Escribe para buscar...",
        # Time
        "time_today": "Hoy",
        "time_live": "VIVO",
        "exit_confirm_title": "Seguro que quieres salir?",
        "exit_confirm_yes": "Si",
        "exit_confirm_no": "No",
        "exit_confirm_help": "[<>] Elegir [A] Confirmar [B] Cancelar",
    },
    "Portugues": {
        # Navigation
        "nav_home": "Inicio",
        "nav_search": "Buscar",
        "nav_favorites": "Favs",
        "nav_history": "Historico",
        "nav_settings": "Config",
        # Settings
        "settings_title": "Configuracoes",
        "settings_language": "Idioma",
        "settings_quality": "Qualidade Video",
        "settings_search_count": "Qtd. Busca",
        "settings_auto_load": "Carregar Auto",
        "settings_clear_favorites": "Limpar Favoritos",
        "settings_clear_history": "Limpar Historico",
        "settings_clear_cache": "Limpar Cache",
        "settings_execute": "[A] Executar",
        "settings_on": "Sim",
        "settings_off": "Nao",
        # Messages
        "msg_searching": "Buscando videos...",
        "msg_loading": "Carregando...",
        "msg_loading_video": "Carregando Video...",
        "msg_loading_videos": "Carregando videos...",
        "msg_no_results": "Sem resultados",
        "msg_press_search": "Aperte X para buscar",
        "msg_no_ytdlp": "yt-dlp nao encontrado!",
        "msg_no_player": "Sem reprodutor!",
        "msg_install_ytdlp": "Instalar: pip install yt-dlp",
        "msg_install_player": "Instalar: mpv ou ffplay",
        "msg_timeout": "Tempo esgotado",
        "msg_added_fav": "Adicionado aos favoritos",
        "msg_removed_fav": "Removido dos favoritos",
        "msg_fav_cleared": "Favoritos limpos",
        "msg_history_cleared": "Historico limpo",
        "msg_cache_cleared": "Cache limpo",
        "msg_videos": "videos",
        # Help
        "help_keyboard": "A:Digitar  B:Fechar  START:Buscar",
        "help_main": "A:Escolher  B:Voltar  X:Buscar  Y:Fav  L/R:Aba",
        # Keyboard
        "kb_space": "ESPACO",
        "kb_go": "IR",
        "kb_search_placeholder": "Digite para buscar...",
        # Time
        "time_today": "Hoje",
        "time_live": "AO VIVO",
        "exit_confirm_title": "Tem certeza que deseja sair?",
        "exit_confirm_yes": "Sim",
        "exit_confirm_no": "Nao",
        "exit_confirm_help": "[<>] Escolher [A] Confirmar [B] Cancelar",
    },
    "Deutsch": {
        # Navigation
        "nav_home": "Start",
        "nav_search": "Suche",
        "nav_favorites": "Favs",
        "nav_history": "Verlauf",
        "nav_settings": "Einst.",
        # Settings
        "settings_title": "Einstellungen",
        "settings_language": "Sprache",
        "settings_quality": "Videoqualitat",
        "settings_search_count": "Suchanzahl",
        "settings_auto_load": "Auto Laden",
        "settings_clear_favorites": "Favoriten loschen",
        "settings_clear_history": "Verlauf loschen",
        "settings_clear_cache": "Cache loschen",
        "settings_execute": "[A] Ausfuhren",
        "settings_on": "An",
        "settings_off": "Aus",
        # Messages
        "msg_searching": "Videos suchen...",
        "msg_loading": "Laden...",
        "msg_loading_video": "Video laden...",
        "msg_loading_videos": "Videos laden...",
        "msg_no_results": "Keine Ergebnisse",
        "msg_press_search": "X fur Suche drucken",
        "msg_no_ytdlp": "yt-dlp nicht gefunden!",
        "msg_no_player": "Kein Videoplayer!",
        "msg_install_ytdlp": "Installieren: pip install yt-dlp",
        "msg_install_player": "Installieren: mpv oder ffplay",
        "msg_timeout": "Zeituberschreitung",
        "msg_added_fav": "Zu Favoriten hinzugefugt",
        "msg_removed_fav": "Aus Favoriten entfernt",
        "msg_fav_cleared": "Favoriten geloscht",
        "msg_history_cleared": "Verlauf geloscht",
        "msg_cache_cleared": "Cache geloscht",
        "msg_videos": "Videos",
        # Help
        "help_keyboard": "A:Tippen  B:Schliessen  START:Suchen",
        "help_main": "A:Wahlen  B:Zuruck  X:Suche  Y:Fav  L/R:Tab",
        # Keyboard
        "kb_space": "LEER",
        "kb_go": "LOS",
        "kb_search_placeholder": "Zum Suchen tippen...",
        # Time
        "time_today": "Heute",
        "time_live": "LIVE",
        "exit_confirm_title": "Mochten Sie wirklich beenden?",
        "exit_confirm_yes": "Ja",
        "exit_confirm_no": "Nein",
        "exit_confirm_help": "[<>] Wahlen [A] Bestatigen [B] Abbrechen",
    },
    "Francais": {
        # Navigation
        "nav_home": "Accueil",
        "nav_search": "Chercher",
        "nav_favorites": "Favs",
        "nav_history": "Historique",
        "nav_settings": "Params",
        # Settings
        "settings_title": "Parametres",
        "settings_language": "Langue",
        "settings_quality": "Qualite Video",
        "settings_search_count": "Nb. Recherche",
        "settings_auto_load": "Charg. Auto",
        "settings_clear_favorites": "Effacer Favoris",
        "settings_clear_history": "Effacer Historique",
        "settings_clear_cache": "Effacer Cache",
        "settings_execute": "[A] Executer",
        "settings_on": "Oui",
        "settings_off": "Non",
        # Messages
        "msg_searching": "Recherche videos...",
        "msg_loading": "Chargement...",
        "msg_loading_video": "Chargement Video...",
        "msg_loading_videos": "Chargement videos...",
        "msg_no_results": "Aucun resultat",
        "msg_press_search": "Appuyez X pour chercher",
        "msg_no_ytdlp": "yt-dlp non trouve!",
        "msg_no_player": "Pas de lecteur!",
        "msg_install_ytdlp": "Installer: pip install yt-dlp",
        "msg_install_player": "Installer: mpv ou ffplay",
        "msg_timeout": "Delai depasse",
        "msg_added_fav": "Ajoute aux favoris",
        "msg_removed_fav": "Retire des favoris",
        "msg_fav_cleared": "Favoris effaces",
        "msg_history_cleared": "Historique efface",
        "msg_cache_cleared": "Cache efface",
        "msg_videos": "videos",
        # Help
        "help_keyboard": "A:Taper  B:Fermer  START:Chercher",
        "help_main": "A:Choisir  B:Retour  X:Chercher  Y:Fav  L/R:Onglet",
        # Keyboard
        "kb_space": "ESPACE",
        "kb_go": "ALLER",
        "kb_search_placeholder": "Tapez pour chercher...",
        # Time
        "time_today": "Aujourd'hui",
        "time_live": "DIRECT",
        "exit_confirm_title": "Voulez-vous vraiment quitter?",
        "exit_confirm_yes": "Oui",
        "exit_confirm_no": "Non",
        "exit_confirm_help": "[<>] Choix [A] Confirmer [B] Annuler",
    },
    "Russian": {
        "nav_home": "Главная",
        "nav_search": "Поиск",
        "nav_favorites": "Избр.",
        "nav_history": "История",
        "nav_settings": "Настройки",
        "settings_title": "Настройки",
        "settings_language": "Язык",
        "settings_quality": "Качество видео",
        "settings_search_count": "Кол-во поиска",
        "settings_auto_load": "Автозагрузка",
        "settings_clear_favorites": "Очистить избр.",
        "settings_clear_history": "Очистить историю",
        "settings_clear_cache": "Очистить кэш",
        "settings_execute": "[A] Выполнить",
        "settings_on": "Вкл",
        "settings_off": "Выкл",
        "msg_searching": "Поиск видео...",
        "msg_loading": "Загрузка...",
        "msg_loading_video": "Загрузка видео...",
        "msg_loading_videos": "Загрузка видео...",
        "msg_no_results": "Нет результатов",
        "msg_press_search": "Нажмите X для поиска",
        "msg_no_ytdlp": "yt-dlp не найден!",
        "msg_no_player": "Нет плеера!",
        "msg_install_ytdlp": "Уст.: pip install yt-dlp",
        "msg_install_player": "Уст.: mpv или ffplay",
        "msg_timeout": "Тайм-аут",
        "msg_added_fav": "Добавлено в избр.",
        "msg_removed_fav": "Удалено из избр.",
        "msg_fav_cleared": "Избранное очищено",
        "msg_history_cleared": "История очищена",
        "msg_cache_cleared": "Кэш очищен",
        "msg_videos": "видео",
        "help_keyboard": "A:Ввод B:Закр START:Поиск",
        "help_main": "A:Выбор B:Назад X:Поиск Y:Избр",
        "kb_space": "ПРОБЕЛ",
        "kb_go": "ИСКАТЬ",
        "kb_search_placeholder": "Введите для поиска...",
        "time_today": "Сегодня",
        "time_live": "ЭФИР",
        "exit_confirm_title": "Вы уверены, что хотите выйти?",
        "exit_confirm_yes": "Да",
        "exit_confirm_no": "Нет",
        "exit_confirm_help": "[<>] Выбор [A] Подтв [B] Отмена",
    },
    "Ukrainian": {
        "nav_home": "Головна",
        "nav_search": "Пошук",
        "nav_favorites": "Улюбл.",
        "nav_history": "Історія",
        "nav_settings": "Налашт.",
        "settings_title": "Налаштування",
        "settings_language": "Мова",
        "settings_quality": "Якість відео",
        "settings_search_count": "Кільк. пошуку",
        "settings_auto_load": "Автозавант.",
        "settings_clear_favorites": "Очист. улюбл.",
        "settings_clear_history": "Очист. історію",
        "settings_clear_cache": "Очистити кеш",
        "settings_execute": "[A] Виконати",
        "settings_on": "Увімк",
        "settings_off": "Вимк",
        "msg_searching": "Пошук відео...",
        "msg_loading": "Завантаження...",
        "msg_loading_video": "Завантаження...",
        "msg_loading_videos": "Завантаження...",
        "msg_no_results": "Немає результатів",
        "msg_press_search": "Натисніть X",
        "msg_no_ytdlp": "yt-dlp не знайдено!",
        "msg_no_player": "Немає плеєра!",
        "msg_install_ytdlp": "Вст.: pip install yt-dlp",
        "msg_install_player": "Вст.: mpv або ffplay",
        "msg_timeout": "Час вийшов",
        "msg_added_fav": "Додано в улюбл.",
        "msg_removed_fav": "Видалено з улюбл.",
        "msg_fav_cleared": "Улюблені очищені",
        "msg_history_cleared": "Історія очищена",
        "msg_cache_cleared": "Кеш очищено",
        "msg_videos": "відео",
        "help_keyboard": "A:Ввід B:Закр START:Пошук",
        "help_main": "A:Вибір B:Назад X:Пошук Y:Улюбл",
        "kb_space": "ПРОБІЛ",
        "kb_go": "ПУСК",
        "kb_search_placeholder": "Введіть для пошуку...",
        "time_today": "Сьогодні",
        "time_live": "ЕФІР",
        "exit_confirm_title": "Ви впевнені, що хочете вийти?",
        "exit_confirm_yes": "Так",
        "exit_confirm_no": "Ні",
        "exit_confirm_help": "[<>] Вибір [A] Підтв [B] Скас",
    },
}

LANGUAGES = ["English", "Turkce", "Espanol", "Portugues", "Deutsch", "Francais", "Russian", "Ukrainian"]

NAV_HOME = 0
NAV_SEARCH = 1
NAV_FAVORITES = 2
NAV_HISTORY = 3
NAV_SETTINGS = 4


def find_ytdlp():
    """yt-dlp binary'sini bul"""
    paths = [
        os.path.join(SCRIPT_DIR, "yt-dlp"),
        os.path.expanduser("~/.local/bin/yt-dlp"),
        "/home/ark/.local/bin/yt-dlp",
        "/usr/local/bin/yt-dlp",
        "/usr/bin/yt-dlp",
    ]
    
    for p in paths:
        if os.path.exists(p):
            try:
                os.chmod(p, 0o755)
            except:
                pass
            return p
    
    # PATH'te ara
    try:
        result = subprocess.run(["which", "yt-dlp"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass
    
    return None


def find_video_player():
    """Video player bul"""
    players = ["mpv", "ffplay", "vlc", "mplayer"]
    
    for player in players:
        try:
            result = subprocess.run(["which", player], capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                return player
        except:
            continue
    
    # PortMaster'da ffplay ara
    pm_ffplay = "/opt/system/Tools/PortMaster/libs/ffplay"
    if os.path.exists(pm_ffplay):
        return pm_ffplay
    
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
            
            # Thumbnail URL - en iyi kaliteyi seç
            self.thumbnail = ''
            if data.get('thumbnail'):
                self.thumbnail = data.get('thumbnail')
            elif data.get('thumbnails'):
                thumbs = data.get('thumbnails', [])
                if thumbs:
                    # En küçük boyutlu thumbnail'i seç (daha hızlı yüklensin)
                    for t in thumbs:
                        if t.get('url'):
                            self.thumbnail = t.get('url')
                            break
            
            # YouTube default thumbnail
            if not self.thumbnail and self.id:
                self.thumbnail = f"https://i.ytimg.com/vi/{self.id}/mqdefault.jpg"
        else:
            self.id = ''
            self.title = ''
            self.channel = ''
            self.duration = 0
            self.views = 0
            self.thumbnail = ''
            self.upload_date = ''
            self.url = ''
    
    def format_duration(self):
        if not self.duration:
            return "LIVE"
        mins, secs = divmod(int(self.duration), 60)
        hours, mins = divmod(mins, 60)
        if hours:
            return f"{hours}:{mins:02d}:{secs:02d}"
        return f"{mins}:{secs:02d}"
    
    def format_views(self):
        if not self.views:
            return ""
        if self.views >= 1000000:
            return f"{self.views/1000000:.1f}M"
        if self.views >= 1000:
            return f"{self.views/1000:.1f}K"
        return str(self.views)
    
    def format_date(self):
        if not self.upload_date:
            return ""
        try:
            date = datetime.strptime(self.upload_date, "%Y%m%d")
            delta = datetime.now() - date
            if delta.days < 1:
                return "Today"
            if delta.days < 7:
                return f"{delta.days}d"
            if delta.days < 30:
                return f"{delta.days // 7}w"
            if delta.days < 365:
                return f"{delta.days // 30}mo"
            return f"{delta.days // 365}y"
        except:
            return ""
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'channel': self.channel,
            'duration': self.duration,
            'view_count': self.views,
            'thumbnail': self.thumbnail,
            'upload_date': self.upload_date,
            'url': self.url
        }


class YouTubeApp:
    def __init__(self):
        SDL_Init(SDL_INIT_VIDEO | SDL_INIT_JOYSTICK | SDL_INIT_GAMECONTROLLER)
        ttf.TTF_Init()
        
        self.window = SDL_CreateWindow(
            b"YouTube",
            SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
            SCREEN_WIDTH, SCREEN_HEIGHT,
            SDL_WINDOW_SHOWN
        )
        self.renderer = SDL_CreateRenderer(self.window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC)
        SDL_SetRenderDrawBlendMode(self.renderer, SDL_BLENDMODE_BLEND)
        
        # Controller
        self.controller = None
        self.joystick = None
        if SDL_NumJoysticks() > 0:
            if SDL_IsGameController(0):
                self.controller = SDL_GameControllerOpen(0)
            else:
                self.joystick = SDL_JoystickOpen(0)
        
        # Font
        font_path = self._find_font()
        self.font = self.font_large = self.font_small = self.font_tiny = None
        if font_path:
            self.font = ttf.TTF_OpenFont(font_path.encode(), 18)
            self.font_large = ttf.TTF_OpenFont(font_path.encode(), 24)
            self.font_small = ttf.TTF_OpenFont(font_path.encode(), 14)
            self.font_tiny = ttf.TTF_OpenFont(font_path.encode(), 12)
        
        # Caches
        self.text_cache = {}
        self.image_cache = {}
        self.failed_images = set()
        self.loading_images = set()
        self.image_cache_dir = os.path.join(SCRIPT_DIR, ".thumb_cache")
        os.makedirs(self.image_cache_dir, exist_ok=True)
        
        if SDL_IMAGE_AVAILABLE:
            try:
                sdlimage.IMG_Init(sdlimage.IMG_INIT_JPG | sdlimage.IMG_INIT_PNG)
            except:
                pass
        
        # State
        self.running = True
        self.need_redraw = True
        self.frame_count = 0
        
        self.current_nav = NAV_HOME
        self.selected = 0
        self.scroll = 0
        
        self.ytdlp_path = YTDLP_PATH
        self.video_player = VIDEO_PLAYER
        
        # Data
        self.home_videos = []
        self.search_results = []
        self.favorites = self._load_json("yt_favorites.json")
        self.history = self._load_json("yt_history.json")
        self.last_search_query = ""
        self.home_page = 0
        self.search_page = 0
        self.max_videos = 50  # Maksimum video sayısı
        
        # Batch tracking
        self.home_batch = 1
        self.search_batch = 1
        self.home_batch_loading = False
        self.search_batch_loading = False
        self.home_first_batch_count = 0
        self.search_first_batch_count = 0
        self.home_existing_ids = set()
        self.search_existing_ids = set()
        
        # Settings
        self.settings = self._load_settings()
        self._update_settings_items()
        self.settings_selected = 0
        self.settings_scroll = 0
        
        # Status
        status_parts = []
        if self.ytdlp_path:
            status_parts.append("yt-dlp OK")
        else:
            status_parts.append("NO yt-dlp!")
        if self.video_player:
            status_parts.append(f"Player: {os.path.basename(self.video_player)}")
        else:
            status_parts.append("NO player!")
        
        self.status = " | ".join(status_parts)
        self.status_type = "ok" if self.ytdlp_path else "error"
        self.is_loading = False
        
        # Keyboard
        self.search_active = False
        self.search_query = ""
        self.keyboard_row = 0
        self.keyboard_col = 0
        self.caps_lock = False
        self.alphabet_mode = 'Cyrillic'
        self.keyboard_layout = self._get_keyboard_layout()

        # Exit Confirm
        self.exit_confirm_active = False
        self.exit_confirm_selection = 0

        # Input
        self.key_held = None
        self.key_hold_start = 0
        self.last_repeat = 0
        
        # Playback
        self.is_playing = False
        self.is_loading_video = False
        self.is_searching = False
        self.player_process = None
        self.current_video = None
        self.player_paused = False
        self.mpv_socket = None
        
        # Loading spinner sticky flag
        self.loading_spinner_triggered = False
        
        print(f"yt-dlp: {self.ytdlp_path}")
        print(f"Player: {self.video_player}")
    
    def _find_font(self):
        paths = [
            os.path.join(SCRIPT_DIR, "font.ttf"),
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/opt/system/Tools/PortMaster/themes/default.ttf",
        ]
        for p in paths:
            if os.path.exists(p):
                return p
        return None
    
    def _load_json(self, filename):
        try:
            path = os.path.join(SCRIPT_DIR, filename)
            if os.path.exists(path):
                with open(path) as f:
                    return [VideoItem(v) for v in json.load(f)]
        except Exception as e:
            print(f"Load {filename} error: {e}")
        return []
    
    def _save_json(self, filename, items):
        try:
            path = os.path.join(SCRIPT_DIR, filename)
            with open(path, 'w') as f:
                json.dump([v.to_dict() for v in items[:50]], f)
        except Exception as e:
            print(f"Save {filename} error: {e}")
    
    def _load_settings(self):
        try:
            path = os.path.join(SCRIPT_DIR, "yt_settings.json")
            if os.path.exists(path):
                with open(path) as f:
                    return json.load(f)
        except:
            pass
        return {
            "quality": "480p",
            "search_count": "10",
            "auto_load": "On",
            "language": "English"
        }
    
    def _save_settings(self):
        try:
            path = os.path.join(SCRIPT_DIR, "yt_settings.json")
            with open(path, 'w') as f:
                json.dump(self.settings, f)
        except:
            pass
    
    def t(self, key):
        """Get translated string for current language"""
        lang = self.settings.get("language", "English")
        if lang in TRANSLATIONS and key in TRANSLATIONS[lang]:
            return TRANSLATIONS[lang][key]
        # Fallback to English
        return TRANSLATIONS["English"].get(key, key)
    
    def _update_settings_items(self):
        """Update settings items with current language"""
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
                if alphabet_mode == 'Cyrillic':
                    return [
                        list("1234567890"),
                        list("йцукенгшщзхї"),
                        list("фівапролджєґ"),
                        list("ячсмитьбюъ"),
                    ]
                else:
                    return [
                        list("1234567890"),
                        list("qwertyuiop"),
                        list("asdfghjkl"),
                        list("zxcvbnm"),
                    ]

            elif lang == "Russian":
                if alphabet_mode == 'Cyrillic':
                    return [
                        list("1234567890"),
                        list("йцукенгшщзхъ"),
                        list("фывапролджэ"),
                        list("ячсмитьбюё"),
                    ]
                else:
                    return [
                        list("1234567890"),
                        list("qwertyuiop"),
                        list("asdfghjkl"),
                        list("zxcvbnm"),
                    ]

        layouts = {
            "English": [
                list("1234567890"),
                list("qwertyuiop"),
                list("asdfghjkl"),
                list("zxcvbnm"),
            ],
            "Turkce": [
                list("1234567890"),
                list("qwertyuıopğü"),
                list("asdfghjklşi"),
                list("zxcvbnmöç"),
            ],
            "Deutsch": [
                list("1234567890"),
                list("qwertzuiopü"),
                list("asdfghjklöä"),
                list("yxcvbnmß"),
            ],
            "Francais": [
                list("1234567890"),
                list("azertyuiop"),
                list("qsdfghjklm"),
                list("wxcvbn"),
                list("àçéèêëîïôùûü"),
            ],
            "Espanol": [
                list("1234567890"),
                list("qwertyuiop"),
                list("asdfghjklñ"),
                list("zxcvbnm"),
                list("áéíóúü"),
            ],
            "Portugues": [
                list("1234567890"),
                list("qwertyuiop"),
                list("asdfghjklç"),
                list("zxcvbnm"),
                list("ãõâêôáéíóú"),
            ],
        }

        return layouts.get(lang, layouts["English"])

    def add_to_history(self, video):
        self.history = [v for v in self.history if v.id != video.id]
        self.history.insert(0, video)
        self._save_json("yt_history.json", self.history)
    
    # === YouTube API ===
    def search_youtube(self, query):
        if not self.ytdlp_path:
            self.status = "yt-dlp not found!"
            self.status_type = "error"
            return
        
        count = int(self.settings.get("search_count", "8"))
        self.last_search_query = query
        self.search_batch = 1
        self.search_existing_ids = set()
        self.search_first_batch_count = 0
        
        # Listeyi temizle ve hemen search sayfasına geç
        self.search_results = []
        self.selected = 0
        self.scroll = 0
        self.current_nav = NAV_SEARCH
        self.search_active = False
        
        self.is_loading = True
        self.is_searching = True  # Searching loading ekranı için
        self.status = "Searching..."
        self.status_type = "loading"
        self.need_redraw = True
        
        # İlk batch'i yükle
        self._load_batch("search", 1)
    
    def _load_batch(self, list_type, batch_num):
        """Belirli bir batch'i yükle"""
        count = int(self.settings.get("search_count", "8"))
        
        if list_type == "search":
            if self.search_batch_loading:
                return
            self.search_batch_loading = True
            target_list = self.search_results
            existing_ids = self.search_existing_ids
            
            # Her batch için farklı arama terimi
            if batch_num == 1:
                query = f"ytsearch{count}:{self.last_search_query}"
            elif batch_num == 2:
                query = f"ytsearch{count}:{self.last_search_query} music"
            else:
                query = f"ytsearch{count}:{self.last_search_query} video {batch_num}"
        else:
            if self.home_batch_loading:
                return
            self.home_batch_loading = True
            target_list = self.home_videos
            existing_ids = self.home_existing_ids
            
            # Her batch için farklı arama terimi
            if batch_num == 1:
                query = f"ytsearch{count}:trending music"
            elif batch_num == 2:
                query = f"ytsearch{count}:popular music 2024"
            else:
                query = f"ytsearch{count}:top hits music {batch_num}"
        
        def worker():
            try:
                cmd = [
                    self.ytdlp_path,
                    query,
                    "--flat-playlist",
                    "--dump-json",
                    "--no-warnings",
                    "--ignore-errors",
                    "--no-check-certificates",
                    "--extractor-args", "youtube:skip=dash,hls",
                    "--socket-timeout", "15",
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
                
                added = 0
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            vid_id = data.get('id')
                            if vid_id and vid_id not in existing_ids:
                                video = VideoItem(data)
                                target_list.append(video)
                                existing_ids.add(vid_id)
                                added += 1
                        except:
                            continue
                
                # Batch numarasını güncelle
                if list_type == "search":
                    self.search_batch = batch_num
                    self.search_batch_loading = False
                    if batch_num == 1:
                        self.search_first_batch_count = len(target_list)
                else:
                    self.home_batch = batch_num
                    self.home_batch_loading = False
                    if batch_num == 1:
                        self.home_first_batch_count = len(target_list)
                
                # Yükleme bittiğinde spinner flag'ini sıfırla
                self.loading_spinner_triggered = False
                
                if target_list:
                    self.status = f"{len(target_list)} videos"
                    self.status_type = "ok"
                else:
                    self.status = "No results" if list_type == "search" else "Press X to search"
                    self.status_type = "error" if list_type == "search" else "ok"
                
                # İlk batch ise loading'i kapat
                if batch_num == 1:
                    self.is_loading = False
                    if list_type == "search":
                        self.is_searching = False  # Arama loading ekranını kapat
                    # 1 saniye sonra ikinci batch'i yükle
                    if target_list:
                        threading.Timer(1.0, lambda: self._load_batch(list_type, 2)).start()
                
                self.need_redraw = True
                
            except subprocess.TimeoutExpired:
                if batch_num == 1:
                    self.status = "Timeout"
                    self.status_type = "error"
                    self.is_loading = False
                    if list_type == "search":
                        self.is_searching = False
                if list_type == "search":
                    self.search_batch_loading = False
                else:
                    self.home_batch_loading = False
                self.need_redraw = True
            except Exception as e:
                if batch_num == 1:
                    self.status = f"Error: {str(e)[:20]}"
                    self.status_type = "error"
                    self.is_loading = False
                    if list_type == "search":
                        self.is_searching = False
                if list_type == "search":
                    self.search_batch_loading = False
                else:
                    self.home_batch_loading = False
                self.need_redraw = True
        
        threading.Thread(target=worker, daemon=True).start()
    
    def check_load_next_batch(self):
        """Kullanıcı scroll yaptığında sonraki batch'i yükle"""
        if self.current_nav == NAV_HOME:
            # İkinci batch'in ilk videosuna ulaşıldı mı?
            if (self.home_batch == 2 and 
                self.selected >= self.home_first_batch_count and 
                not self.home_batch_loading and
                len(self.home_videos) < self.max_videos):
                self._load_batch("home", 3)
            # 3. batch'ten sonra her batch için
            elif (self.home_batch >= 3 and
                  self.selected >= len(self.home_videos) - 3 and
                  not self.home_batch_loading and
                  len(self.home_videos) < self.max_videos):
                self._load_batch("home", self.home_batch + 1)
                
        elif self.current_nav == NAV_SEARCH:
            # İkinci batch'in ilk videosuna ulaşıldı mı?
            if (self.search_batch == 2 and
                self.selected >= self.search_first_batch_count and
                not self.search_batch_loading and
                len(self.search_results) < self.max_videos):
                self._load_batch("search", 3)
            # 3. batch'ten sonra her batch için
            elif (self.search_batch >= 3 and
                  self.selected >= len(self.search_results) - 3 and
                  not self.search_batch_loading and
                  len(self.search_results) < self.max_videos):
                self._load_batch("search", self.search_batch + 1)
    
    def load_trending(self):
        if not self.ytdlp_path:
            return
        
        if self.settings.get("auto_load") == "Off":
            return
        
        self.home_batch = 1
        self.home_existing_ids = set()
        self.home_first_batch_count = 0
        self.home_videos = []  # Listeyi temizle
        self.is_loading = True
        self.status = "Loading..."
        self.status_type = "loading"
        self.need_redraw = True
        self.render()
        
        # İlk batch'i yükle
        self._load_batch("home", 1)
    
    def render_loading_screen(self, title="Loading...", subtitle=""):
        """Siyah ekran üzerinde loading göstergesi çiz"""
        # Siyah arka plan
        SDL_SetRenderDrawColor(self.renderer, 0, 0, 0, 255)
        SDL_RenderClear(self.renderer)
        
        # YouTube logosu (küçük, ortada üstte)
        logo_x = SCREEN_WIDTH // 2 - 17
        logo_y = SCREEN_HEIGHT // 2 - 80
        logo_w, logo_h = 34, 24
        
        # Kırmızı arka plan
        self.draw_rect(logo_x + 2, logo_y, logo_w - 4, logo_h, Colors.YT_RED)
        self.draw_rect(logo_x, logo_y + 2, logo_w, logo_h - 4, Colors.YT_RED)
        self.draw_rect(logo_x + 1, logo_y + 1, logo_w - 2, logo_h - 2, Colors.YT_RED)
        
        # Beyaz play üçgeni
        tri_x = logo_x + 12
        tri_y = logo_y + 6
        tri_size = 12
        for row in range(tri_size):
            if row < tri_size // 2:
                w = row + 1
            else:
                w = tri_size - row
            self.draw_rect(tri_x, tri_y + row, w, 1, Colors.TEXT_PRIMARY)
        
        # Loading yazısı
        self.draw_text(title, SCREEN_WIDTH // 2 - len(title) * 5, SCREEN_HEIGHT // 2 - 20, Colors.TEXT_PRIMARY, self.font_large)
        
        # Alt yazı (video başlığı)
        if subtitle:
            short_title = subtitle[:40] + "..." if len(subtitle) > 40 else subtitle
            self.draw_text(short_title, SCREEN_WIDTH // 2 - len(short_title) * 4, SCREEN_HEIGHT // 2 + 20, Colors.TEXT_SECONDARY, self.font_small)
        
        # Progress bar (animasyonlu)
        bar_width = 200
        bar_height = 4
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = SCREEN_HEIGHT // 2 + 60
        
        # Arka plan
        self.draw_rect(bar_x, bar_y, bar_width, bar_height, Colors.PROGRESS_BG)
        
        # Animasyonlu progress
        progress_width = 60
        offset = (self.frame_count * 3) % (bar_width + progress_width)
        start_x = bar_x + offset - progress_width
        
        # Clipping için sadece bar içinde çiz
        if start_x < bar_x:
            draw_start = bar_x
            draw_width = progress_width - (bar_x - start_x)
        else:
            draw_start = start_x
            draw_width = min(progress_width, bar_x + bar_width - start_x)
        
        if draw_width > 0 and draw_start < bar_x + bar_width:
            self.draw_rect(int(draw_start), bar_y, int(draw_width), bar_height, Colors.YT_RED)
        
        SDL_RenderPresent(self.renderer)
        self.frame_count += 1
    
    def play_video(self, video):
        if not self.ytdlp_path:
            self.status = "yt-dlp not found!"
            self.status_type = "error"
            return
        
        if not self.video_player:
            self.status = "No video player found!"
            self.status_type = "error"
            return
        
        self.add_to_history(video)
        self.current_video = video
        self.is_loading_video = True
        self.status = "Loading video..."
        self.status_type = "loading"
        self.need_redraw = True
        
        # Loading ekranını göster
        self.render_loading_screen(self.t("msg_loading_video"), video.title)
        
        # Kalite ayarını al
        quality = self.settings.get("quality", "480p")
        height = quality.replace("p", "")
        
        def worker():
            try:
                # Video URL al
                cmd = [
                    self.ytdlp_path,
                    "-f", f"best[height<={height}]/best",
                    "-g",
                    "--no-warnings",
                    "--no-check-certificates",
                    "--no-playlist",
                    video.url
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    self.status = "Failed to get URL"
                    self.status_type = "error"
                    self.is_loading_video = False
                    self.need_redraw = True
                    return
                
                stream_url = result.stdout.strip().split('\n')[0]
                
                if not stream_url:
                    self.status = "No stream URL"
                    self.status_type = "error"
                    self.is_loading_video = False
                    self.need_redraw = True
                    return
                
                self.is_loading_video = False
                
                # SDL penceresini gizle
                SDL_HideWindow(self.window)
                
                self.is_playing = True
                self.player_paused = False
                
                player = self.video_player
                player_name = os.path.basename(player)
                
                # mpv için IPC socket
                self.mpv_socket = f"/tmp/mpv_{os.getpid()}"
                
                if player_name == "mpv":
                    player_cmd = [
                        player,
                        "--fs",
                        "--no-terminal",
                        "--really-quiet",
                        f"--input-ipc-server={self.mpv_socket}",
                        "--osd-level=1",
                        "--osd-duration=1500",
                        "--cache=yes",
                        "--demuxer-max-bytes=50M",
                        stream_url
                    ]
                elif player_name == "ffplay":
                    player_cmd = [
                        player,
                        "-fs",
                        "-autoexit",
                        "-noborder",
                        "-framedrop",
                        "-exitonkeydown",
                    ]
                    if height and int(height) <= 480:
                        player_cmd.extend(["-lowres", "1"])
                    player_cmd.extend([
                        "-infbuf",
                        "-threads", "4",
                        "-sync", "video",
                        stream_url
                    ])
                elif player_name == "vlc":
                    player_cmd = [player, "--fullscreen", "--play-and-exit", "-q", stream_url]
                else:
                    player_cmd = [player, stream_url]
                
                env = os.environ.copy()
                if 'DISPLAY' not in env:
                    env['DISPLAY'] = ':0'

                self.player_process = subprocess.Popen(
                    player_cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    env=env
                )

                last_button_check = time.time()

                while self.player_process.poll() is None:
                    # FFplay volume controls with D-Pad
                    if self.controller and (time.time() - last_button_check > 0.15):
                        SDL_GameControllerUpdate()
                        dpad_up = SDL_GameControllerGetButton(self.controller, SDL_CONTROLLER_BUTTON_DPAD_UP)
                        dpad_down = SDL_GameControllerGetButton(self.controller, SDL_CONTROLLER_BUTTON_DPAD_DOWN)

                        if dpad_up:
                            subprocess.run(["amixer", "set", "Playback", "5%+"], capture_output=True)
                        if dpad_down:
                            subprocess.run(["amixer", "set", "Playback", "5%-"], capture_output=True)

                        last_button_check = time.time()
                    time.sleep(0.05)
                
            except Exception as e:
                print(f"Play error: {e}")
            finally:
                self.is_playing = False
                self.player_process = None
                self.current_video = None
                self.player_paused = False
                
                # Socket temizle
                try:
                    if hasattr(self, 'mpv_socket') and self.mpv_socket and os.path.exists(self.mpv_socket):
                        os.remove(self.mpv_socket)
                except:
                    pass
                
                # SDL penceresini göster
                SDL_ShowWindow(self.window)
                SDL_RaiseWindow(self.window)
                
                self.status = "Ready"
                self.status_type = "ok"
                self.need_redraw = True
        
        threading.Thread(target=worker, daemon=True).start()
    
    def send_mpv_command(self, command):
        """mpv'ye IPC komutu gönder - sessizce"""
        if not self.is_playing or not hasattr(self, 'mpv_socket') or not self.mpv_socket:
            return False
        
        try:
            import socket
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect(self.mpv_socket)
            sock.send((json.dumps({"command": command}) + "\n").encode())
            sock.close()
            return True
        except:
            return False
    
    def player_seek(self, seconds):
        """Video'da ileri/geri sar - render tetiklemeden"""
        if self.is_playing:
            self.send_mpv_command(["seek", str(seconds), "relative"])
    
    def player_toggle_pause(self):
        """Duraklat/devam - render tetiklemeden"""
        if self.is_playing:
            self.send_mpv_command(["cycle", "pause"])
    
    def player_brightness(self, delta):
        """Parlaklık ayarla"""
        if self.is_playing:
            self.send_mpv_command(["add", "brightness", str(delta)])
    
    def stop_playback(self):
        if self.player_process:
            try:
                self.player_process.terminate()
                self.player_process.wait(timeout=2)
            except:
                try:
                    self.player_process.kill()
                except:
                    pass
        
        self.is_playing = False
        self.player_process = None
        self.current_video = None
        
        # SDL penceresini göster
        SDL_ShowWindow(self.window)
        SDL_RaiseWindow(self.window)
        
        self.status = "Stopped"
        self.status_type = "ok"
        self.need_redraw = True
    
    # === Thumbnail ===
    def get_thumb_path(self, url):
        h = hashlib.md5(url.encode()).hexdigest()
        return os.path.join(self.image_cache_dir, f"{h}.jpg")
    
    def download_thumbnail(self, url):
        if not url or url in self.failed_images or url in self.loading_images:
            return
        
        # Aynı anda maksimum 3 indirme
        if len(self.loading_images) >= 3:
            return
        
        self.loading_images.add(url)
        
        def worker():
            try:
                cache_path = self.get_thumb_path(url)
                
                if os.path.exists(cache_path):
                    self.loading_images.discard(url)
                    self.need_redraw = True
                    return
                
                # URL'yi düzelt
                download_url = url
                if download_url.startswith("//"):
                    download_url = "https:" + download_url
                
                req = urllib.request.Request(download_url, headers={
                    'User-Agent': 'Mozilla/5.0'
                })
                
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                
                with urllib.request.urlopen(req, timeout=5, context=ctx) as resp:
                    data = resp.read()
                    if len(data) > 500:
                        with open(cache_path, 'wb') as f:
                            f.write(data)
                    else:
                        self.failed_images.add(url)
                
            except:
                self.failed_images.add(url)
            finally:
                self.loading_images.discard(url)
                self.need_redraw = True
        
        threading.Thread(target=worker, daemon=True).start()
    
    def load_thumbnail(self, url):
        if not url:
            return None
        
        # Cache'de var mı?
        if url in self.image_cache:
            return self.image_cache[url]
        
        # Başarısız mı?
        if url in self.failed_images:
            return None
        
        # Dosya var mı?
        cache_path = self.get_thumb_path(url)
        if os.path.exists(cache_path) and SDL_IMAGE_AVAILABLE:
            try:
                surface = sdlimage.IMG_Load(cache_path.encode())
                if surface:
                    texture = SDL_CreateTextureFromSurface(self.renderer, surface)
                    w, h = surface.contents.w, surface.contents.h
                    SDL_FreeSurface(surface)
                    if texture:
                        # Cache limit
                        if len(self.image_cache) > 30:
                            old_key = next(iter(self.image_cache))
                            old_tex = self.image_cache.pop(old_key)
                            if old_tex and old_tex[0]:
                                SDL_DestroyTexture(old_tex[0])
                        
                        self.image_cache[url] = (texture, w, h)
                        return (texture, w, h)
            except Exception as e:
                print(f"Load thumbnail error: {e}")
        
        # İndir
        if url not in self.loading_images:
            self.download_thumbnail(url)
        
        return None
    
    def draw_thumbnail(self, x, y, width, height, url):
        # Background
        self.draw_rect(x, y, width, height, Colors.THUMB_BG)
        
        if not url:
            return
        
        result = self.load_thumbnail(url)
        if result:
            texture, img_w, img_h = result
            if texture:
                # Aspect fit
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
                
                dst = SDL_Rect(int(draw_x), int(draw_y), int(draw_w), int(draw_h))
                SDL_RenderCopy(self.renderer, texture, None, dst)
                return
        
        # Loading indicator
        if url in self.loading_images:
            dots = "." * ((self.frame_count // 20) % 4)
            self.draw_text(dots, x + width//2 - 10, y + height//2 - 5, Colors.TEXT_SECONDARY, self.font_small)
    
    # === Drawing ===
    def draw_rect(self, x, y, w, h, color, alpha=255):
        SDL_SetRenderDrawColor(self.renderer, color[0], color[1], color[2], alpha)
        SDL_RenderFillRect(self.renderer, SDL_Rect(int(x), int(y), int(w), int(h)))
    
    def draw_spinner(self, center_x, center_y, radius=12, dot_size=3):
        """Dönen nokta animasyonu çiz - saat yönünde 8 pozisyon"""
        # 8 pozisyon (saat yönünde: 12, 1:30, 3, 4:30, 6, 7:30, 9, 10:30)
        import math
        positions = []
        for i in range(8):
            angle = math.pi / 2 - (i * math.pi / 4)  # 12'den başla, saat yönünde
            px = center_x + int(radius * math.cos(angle))
            py = center_y - int(radius * math.sin(angle))
            positions.append((px, py))
        
        # Aktif nokta indeksi (animasyon)
        active_index = (self.frame_count // 6) % 8
        
        # Noktaları çiz
        for i, (px, py) in enumerate(positions):
            if i == active_index:
                # Aktif nokta - büyük ve parlak kırmızı
                self.draw_rect(px - dot_size, py - dot_size, dot_size * 2, dot_size * 2, Colors.YT_RED)
            else:
                # Pasif nokta - küçük ve soluk
                self.draw_rect(px - 1, py - 1, 2, 2, Colors.TEXT_TERTIARY)
    
    def draw_text(self, text, x, y, color=Colors.TEXT_PRIMARY, font=None):
        if not font:
            font = self.font
        if not font:
            return 0
        
        text = str(text)[:80]
        key = (text, color, id(font))
        
        if key not in self.text_cache:
            if len(self.text_cache) > 150:
                for tex, _, _ in self.text_cache.values():
                    if tex:
                        SDL_DestroyTexture(tex)
                self.text_cache.clear()
            
            sdl_color = SDL_Color(color[0], color[1], color[2], 255)
            surface = ttf.TTF_RenderUTF8_Blended(font, text.encode('utf-8'), sdl_color)
            if not surface:
                return 0
            w, h = surface.contents.w, surface.contents.h
            texture = SDL_CreateTextureFromSurface(self.renderer, surface)
            SDL_FreeSurface(surface)
            self.text_cache[key] = (texture, w, h)
        
        tex, w, h = self.text_cache[key]
        if tex:
            SDL_RenderCopy(self.renderer, tex, None, SDL_Rect(int(x), int(y), w, h))
        return w
    
    # === Render ===
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
    
    def render_exit_confirm(self):
        self.draw_rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0), 180)
        
        box_w, box_h = 400, 160
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = (SCREEN_HEIGHT - box_h) // 2
        
        # Background
        self.draw_rect(box_x, box_y, box_w, box_h, Colors.BG_SECONDARY)
        self.draw_rect(box_x, box_y, box_w, 2, Colors.YT_RED)
        self.draw_rect(box_x, box_y + box_h - 2, box_w, 2, Colors.YT_RED)
        
        # Icon
        icon_y = box_y + 20
        icon_size = 40
        icon_x = SCREEN_WIDTH // 2 - icon_size // 2
        
        self.draw_rect(icon_x, icon_y, icon_size, icon_size, Colors.YT_RED)
        
        # X Icon
        x_color = Colors.TEXT_PRIMARY
        x_thickness = 4
        x_padding = 8
        
        for i in range(icon_size - x_padding * 2):
            for t in range(x_thickness):
                px = icon_x + x_padding + i
                py = icon_y + x_padding + i + t
                self.draw_rect(px, py, 1, 1, x_color)
                
        for i in range(icon_size - x_padding * 2):
            for t in range(x_thickness):
                px = icon_x + icon_size - x_padding - i
                py = icon_y + x_padding + i + t
                self.draw_rect(px, py, 1, 1, x_color)
        
        # Title
        title = self.t("exit_confirm_title")
        self.draw_text(title, SCREEN_WIDTH // 2 - len(title) * 4.5, icon_y + 55, Colors.TEXT_PRIMARY, self.font)
        
        # Buttons
        button_y = box_y + box_h - 50
        button_w = 140
        button_h = 36
        button_spacing = 20
        
        no_x = box_x + (box_w - button_w * 2 - button_spacing) // 2
        no_selected = self.exit_confirm_selection == 0
        no_bg = Colors.YT_RED if no_selected else Colors.CARD_BG
        
        self.draw_rect(no_x, button_y, button_w, button_h, no_bg)
        if not no_selected:
            self.draw_rect(no_x, button_y, button_w, 2, Colors.TEXT_TERTIARY)
            self.draw_rect(no_x, button_y + button_h - 2, button_w, 2, Colors.TEXT_TERTIARY)
            self.draw_rect(no_x, button_y, 2, button_h, Colors.TEXT_TERTIARY)
            self.draw_rect(no_x + button_w - 2, button_y, 2, button_h, Colors.TEXT_TERTIARY)
            
        no_text = self.t("exit_confirm_no")
        self.draw_text(no_text, no_x + button_w // 2 - len(no_text) * 4.5, button_y + 10, Colors.TEXT_PRIMARY, self.font)
        
        yes_x = no_x + button_w + button_spacing
        yes_selected = self.exit_confirm_selection == 1
        yes_bg = Colors.YT_RED if yes_selected else Colors.CARD_BG
        
        self.draw_rect(yes_x, button_y, button_w, button_h, yes_bg)
        if not yes_selected:
            self.draw_rect(yes_x, button_y, button_w, 2, Colors.TEXT_TERTIARY)
            self.draw_rect(yes_x, button_y + button_h - 2, button_w, 2, Colors.TEXT_TERTIARY)
            self.draw_rect(yes_x, button_y, 2, button_h, Colors.TEXT_TERTIARY)
            self.draw_rect(yes_x + button_w - 2, button_y, 2, button_h, Colors.TEXT_TERTIARY)
            
        yes_text = self.t("exit_confirm_yes")
        self.draw_text(yes_text, yes_x + button_w // 2 - len(yes_text) * 4.5, button_y + 10, Colors.TEXT_PRIMARY, self.font)
        
        help_text = self.t("exit_confirm_help")
        self.draw_text(help_text, SCREEN_WIDTH // 2 - len(help_text) * 3, box_y + box_h - 12, Colors.TEXT_TERTIARY, self.font_tiny)

    def draw_play_triangle(self, x, y, size, color):
        """Üçgen play butonu çiz"""
        # Üçgeni yatay çizgilerle doldur
        for i in range(size):
            # Üçgenin genişliği yukarıdan aşağıya artar sonra azalır
            half = size // 2
            if i <= half:
                width = (i * 2) // 3 + 1
            else:
                width = ((size - i) * 2) // 3 + 1
            
            start_x = x + (size - width) // 4
            self.draw_rect(start_x, y + i, width, 1, color)
    
    def render_header(self):
        # Background
        self.draw_rect(0, 0, SCREEN_WIDTH, 50, Colors.BG_PRIMARY)
        
        # YouTube Logo - Kırmızı yuvarlatılmış dikdörtgen
        logo_x, logo_y = 15, 12
        logo_w, logo_h = 34, 24
        
        # Kırmızı arka plan
        self.draw_rect(logo_x + 2, logo_y, logo_w - 4, logo_h, Colors.YT_RED)
        self.draw_rect(logo_x, logo_y + 2, logo_w, logo_h - 4, Colors.YT_RED)
        self.draw_rect(logo_x + 1, logo_y + 1, logo_w - 2, logo_h - 2, Colors.YT_RED)
        
        # Beyaz play üçgeni
        tri_x = logo_x + 12
        tri_y = logo_y + 6
        tri_size = 12
        
        for row in range(tri_size):
            if row < tri_size // 2:
                w = row + 1
            else:
                w = tri_size - row
            self.draw_rect(tri_x, tri_y + row, w, 1, Colors.TEXT_PRIMARY)
        
        # YouTube yazısı
        self.draw_text("YouTube", 55, 13, Colors.TEXT_PRIMARY, self.font_large)
        
        self.draw_rect(0, 49, SCREEN_WIDTH, 1, Colors.DIVIDER)
    
    def render_navigation(self):
        nav_y = SCREEN_HEIGHT - 55
        
        # Yardım metni - navbar üstünde
        help_y = nav_y - 18
        self.draw_rect(0, help_y, SCREEN_WIDTH, 18, Colors.BG_SECONDARY)
        
        # Klavye açıkken farklı yardım metni göster
        if self.search_active:
            help_text = self.t("help_keyboard")
        else:
            help_text = self.t("help_main")
        self.draw_text(help_text, SCREEN_WIDTH//2 - len(help_text)*3, help_y + 3, Colors.TEXT_TERTIARY, self.font_tiny)
        
        # Navigation bar
        self.draw_rect(0, nav_y, SCREEN_WIDTH, 55, Colors.NAV_BG)
        self.draw_rect(0, nav_y, SCREEN_WIDTH, 1, Colors.DIVIDER)
        
        items = [
            ("home", self.t("nav_home"), NAV_HOME),
            ("search", self.t("nav_search"), NAV_SEARCH),
            ("favorites", self.t("nav_favorites"), NAV_FAVORITES),
            ("history", self.t("nav_history"), NAV_HISTORY),
            ("settings", self.t("nav_settings"), NAV_SETTINGS)
        ]
        item_w = SCREEN_WIDTH // len(items)
        
        for i, (icon_type, label, nav_id) in enumerate(items):
            x = i * item_w
            cx = x + item_w // 2
            active = self.current_nav == nav_id
            
            # Active indicator
            if active:
                self.draw_rect(cx - 20, nav_y + 2, 40, 3, Colors.YT_RED)
            
            icon_color = Colors.NAV_ACTIVE if active else Colors.NAV_INACTIVE
            icon_y = nav_y + 12
            
            # İkonları çiz
            if icon_type == "home":
                # Ev ikonu - daha güzel versiyon
                # Çatı (üçgen)
                self.draw_rect(cx - 1, icon_y, 2, 2, icon_color)
                self.draw_rect(cx - 3, icon_y + 2, 6, 2, icon_color)
                self.draw_rect(cx - 5, icon_y + 4, 10, 2, icon_color)
                self.draw_rect(cx - 7, icon_y + 6, 14, 2, icon_color)
                # Gövde
                self.draw_rect(cx - 6, icon_y + 8, 12, 8, icon_color)
                # Kapı (boşluk)
                self.draw_rect(cx - 2, icon_y + 10, 4, 6, Colors.NAV_BG if active else Colors.BG_PRIMARY)
                # Baca
                self.draw_rect(cx + 3, icon_y - 1, 2, 4, icon_color)
            
            elif icon_type == "search":
                # Büyüteç ikonu - daha yuvarlak ve güzel
                # Daire (dış çerçeve)
                self.draw_rect(cx - 3, icon_y, 6, 2, icon_color)
                self.draw_rect(cx - 5, icon_y + 2, 2, 2, icon_color)
                self.draw_rect(cx + 3, icon_y + 2, 2, 2, icon_color)
                self.draw_rect(cx - 6, icon_y + 4, 2, 4, icon_color)
                self.draw_rect(cx + 4, icon_y + 4, 2, 4, icon_color)
                self.draw_rect(cx - 5, icon_y + 8, 2, 2, icon_color)
                self.draw_rect(cx + 3, icon_y + 8, 2, 2, icon_color)
                self.draw_rect(cx - 3, icon_y + 10, 6, 2, icon_color)
                # Sap (çapraz)
                self.draw_rect(cx + 4, icon_y + 11, 3, 2, icon_color)
                self.draw_rect(cx + 6, icon_y + 13, 3, 2, icon_color)
            
            elif icon_type == "favorites":
                # Kalp ikonu - favoriler için
                # Kalp üst kısmı (iki yarım daire)
                self.draw_rect(cx - 5, icon_y + 2, 4, 4, icon_color)
                self.draw_rect(cx + 1, icon_y + 2, 4, 4, icon_color)
                self.draw_rect(cx - 6, icon_y + 3, 2, 3, icon_color)
                self.draw_rect(cx + 4, icon_y + 3, 2, 3, icon_color)
                self.draw_rect(cx - 4, icon_y + 1, 2, 2, icon_color)
                self.draw_rect(cx + 2, icon_y + 1, 2, 2, icon_color)
                # Kalp alt kısmı (üçgen)
                self.draw_rect(cx - 6, icon_y + 5, 12, 3, icon_color)
                self.draw_rect(cx - 5, icon_y + 8, 10, 2, icon_color)
                self.draw_rect(cx - 4, icon_y + 10, 8, 2, icon_color)
                self.draw_rect(cx - 3, icon_y + 12, 6, 1, icon_color)
                self.draw_rect(cx - 2, icon_y + 13, 4, 1, icon_color)
                self.draw_rect(cx - 1, icon_y + 14, 2, 1, icon_color)
            
            elif icon_type == "history":
                # Saat ikonu - daha yuvarlak ve detaylı
                # Dış daire
                self.draw_rect(cx - 3, icon_y, 6, 2, icon_color)
                self.draw_rect(cx - 5, icon_y + 2, 2, 2, icon_color)
                self.draw_rect(cx + 3, icon_y + 2, 2, 2, icon_color)
                self.draw_rect(cx - 6, icon_y + 4, 2, 6, icon_color)
                self.draw_rect(cx + 4, icon_y + 4, 2, 6, icon_color)
                self.draw_rect(cx - 5, icon_y + 10, 2, 2, icon_color)
                self.draw_rect(cx + 3, icon_y + 10, 2, 2, icon_color)
                self.draw_rect(cx - 3, icon_y + 12, 6, 2, icon_color)
                # Merkez nokta
                self.draw_rect(cx - 1, icon_y + 6, 2, 2, icon_color)
                # Akrep (yukarı)
                self.draw_rect(cx - 1, icon_y + 3, 2, 3, icon_color)
                # Yelkovan (sağa)
                self.draw_rect(cx + 1, icon_y + 6, 3, 2, icon_color)
                # Geri ok işareti (sol tarafta)
                self.draw_rect(cx - 8, icon_y + 5, 2, 4, icon_color)
                self.draw_rect(cx - 10, icon_y + 7, 2, 2, icon_color)
                self.draw_rect(cx - 8, icon_y + 9, 2, 2, icon_color)
            
            elif icon_type == "settings":
                # Dişli ikonu - daha detaylı ve güzel
                # Merkez daire daire (iç boşluk)
                self.draw_rect(cx - 3, icon_y + 4, 6, 6, icon_color)
                # İç boşluk (daire efekti için)
                self.draw_rect(cx - 1, icon_y + 6, 2, 2, Colors.NAV_BG if active else Colors.BG_PRIMARY)
                # Üst diş
                self.draw_rect(cx - 2, icon_y, 4, 4, icon_color)
                # Alt diş
                self.draw_rect(cx - 2, icon_y + 10, 4, 4, icon_color)
                # Sol diş
                self.draw_rect(cx - 7, icon_y + 5, 4, 4, icon_color)
                # Sağ diş
                self.draw_rect(cx + 3, icon_y + 5, 4, 4, icon_color)
                # Sol üst çapraz diş
                self.draw_rect(cx - 6, icon_y + 1, 3, 3, icon_color)
                # Sağ üst çapraz diş
                self.draw_rect(cx + 3, icon_y + 1, 3, 3, icon_color)
                # Sol alt çapraz diş
                self.draw_rect(cx - 6, icon_y + 10, 3, 3, icon_color)
                # Sağ alt çapraz diş
                self.draw_rect(cx + 3, icon_y + 10, 3, 3, icon_color)
            
            # Label
            label_color = Colors.TEXT_PRIMARY if active else Colors.TEXT_TERTIARY
            self.draw_text(label, cx - len(label)*3, nav_y + 35, label_color, self.font_tiny)
    
    def render_content(self):
        y = 55
        h = SCREEN_HEIGHT - 55 - 73  # Header + nav + help text
        
        if self.current_nav == NAV_SETTINGS:
            self.render_settings(y, h)
            return
        
        # Arama yapılıyorsa searching ekranı göster
        if self.is_searching:
            self.render_searching(y)
            return
        
        videos = self._get_list()
        if videos:
            self.render_video_list(videos, y, h)
        else:
            self.render_empty(y)
    
    def render_searching(self, y):
        """Arama yapılırken gösterilecek ekran"""
        # Searching video yazısı
        msg = self.t("msg_searching")
        self.draw_text(msg, SCREEN_WIDTH//2 - len(msg)*5, y + 100, Colors.TEXT_SECONDARY, self.font)
        
        # Arama terimi
        if hasattr(self, 'last_search_query') and self.last_search_query:
            query_text = f'"{self.last_search_query}"'
            if len(query_text) > 35:
                query_text = query_text[:32] + '..."'
            self.draw_text(query_text, SCREEN_WIDTH//2 - len(query_text)*4, y + 130, Colors.TEXT_TERTIARY, self.font_small)
        
        # Loading spinner
        self.draw_spinner(SCREEN_WIDTH // 2, y + 190, radius=14, dot_size=4)
    
    def render_empty(self, y):
        msg = self.t("msg_press_search")
        if not self.ytdlp_path:
            msg = self.t("msg_no_ytdlp")
        elif not self.video_player:
            msg = self.t("msg_no_player")
        
        self.draw_text(msg, SCREEN_WIDTH//2 - len(msg)*5, y + 100, Colors.TEXT_SECONDARY, self.font)
        
        if not self.ytdlp_path:
            self.draw_text(self.t("msg_install_ytdlp"), 150, y + 140, Colors.TEXT_TERTIARY, self.font_tiny)
        if not self.video_player:
            self.draw_text(self.t("msg_install_player"), 170, y + 160, Colors.TEXT_TERTIARY, self.font_tiny)
        
        # Home sayfasında yükleme devam ediyorsa loading göster
        if self.current_nav == NAV_HOME and (self.is_loading or self.home_batch_loading):
            self.draw_spinner(SCREEN_WIDTH // 2, y + 200, radius=12, dot_size=3)
            self.draw_text(self.t("msg_loading_videos"), SCREEN_WIDTH // 2 - 55, y + 230, Colors.TEXT_TERTIARY, self.font_small)
    
    def render_settings(self, start_y, height):
        # Title ve r36swiki.com branding - aynı satırda
        self.draw_text(self.t("settings_title"), 20, start_y + 10, Colors.TEXT_PRIMARY, self.font_large)
        
        # r36swiki.com yazısı - sağ üst köşede, Settings ile aynı hizada
        brand_x = SCREEN_WIDTH - 105
        brand_y = start_y + 12
        self.draw_text("r36swiki.com", brand_x, brand_y, Colors.TEXT_PRIMARY, self.font_small)
        
        item_h = 50
        margin = 5
        list_start_y = start_y + 50
        list_height = height - 60  # Alt kısım için boşluk bırak
        visible_count = list_height // (item_h + margin)
        
        # Scroll kontrolü
        if self.settings_selected < self.settings_scroll:
            self.settings_scroll = self.settings_selected
        elif self.settings_selected >= self.settings_scroll + visible_count:
            self.settings_scroll = self.settings_selected - visible_count + 1
        
        # Görünür öğeleri çiz
        y = list_start_y
        for i in range(self.settings_scroll, min(self.settings_scroll + visible_count, len(self.settings_items))):
            label, key, options = self.settings_items[i]
            selected = i == self.settings_selected
            
            # Background
            if selected:
                self.draw_rect(15, y, SCREEN_WIDTH - 30, item_h, Colors.CARD_SELECTED)
                self.draw_rect(15, y, 4, item_h, Colors.YT_RED)
            else:
                self.draw_rect(15, y, SCREEN_WIDTH - 30, item_h, Colors.CARD_BG)
            
            # Label
            self.draw_text(label, 30, y + 15, Colors.TEXT_PRIMARY if selected else Colors.TEXT_SECONDARY, self.font)
            
            # Value or action
            if options is None:
                # Action button
                self.draw_text(self.t("settings_execute"), SCREEN_WIDTH - 130, y + 15, Colors.YT_RED, self.font_small)
            else:
                # Current value with arrows
                current = self.settings.get(key, options[0])
                self.draw_text(f"< {current} >", SCREEN_WIDTH - 130, y + 15, Colors.TEXT_PRIMARY if selected else Colors.TEXT_TERTIARY, self.font)
            
            y += item_h + margin
        
        # Scrollbar (eğer gerekiyorsa)
        if len(self.settings_items) > visible_count:
            sb_height = list_height
            thumb_height = max(20, int(sb_height * visible_count / len(self.settings_items)))
            thumb_y = list_start_y + int((sb_height - thumb_height) * self.settings_scroll / max(1, len(self.settings_items) - visible_count))
            self.draw_rect(SCREEN_WIDTH - 8, list_start_y, 4, sb_height, Colors.PROGRESS_BG)
            self.draw_rect(SCREEN_WIDTH - 8, thumb_y, 4, thumb_height, Colors.YT_RED)
    
    def change_setting(self, direction):
        """Ayar değerini değiştir (sadece seçenekli ayarlar için)"""
        if self.settings_selected >= len(self.settings_items):
            return
        
        label, key, options = self.settings_items[self.settings_selected]
        
        if options is None:
            # Action item - left/right ile değiştirilemez, sadece A tuşu ile çalışır
            # Bu fonksiyon hiçbir şey yapmamalı
            return
        
        current = self.settings.get(key, options[0])
        try:
            idx = options.index(current)
        except:
            idx = 0
        
        if direction > 0:
            idx = (idx + 1) % len(options)
        else:
            idx = (idx - 1) % len(options)
        
        self.settings[key] = options[idx]
        self._save_settings()
        
        # Dil değiştiğinde settings items'ı ve text cache'i güncelle
        if key == "language":
            self._update_settings_items()
            self.text_cache.clear()
            self.keyboard_layout = self._get_keyboard_layout()
            
            # Reset alphabet mode if switching to/from Cyrillic languages
            lang = self.settings.get("language", "English")
            if lang in ["Ukrainian", "Russian"]:
                self.alphabet_mode = 'Cyrillic'
            else:
                self.alphabet_mode = 'Latin' # Reset for others if needed, though they don't use it explicitly
            
            # Reset keyboard selection to avoid out of bounds
            self.keyboard_row = 0
            self.keyboard_col = 0
        
        self.status = f"{label}: {options[idx]}"
        self.status_type = "ok"
        self.need_redraw = True
    
    def execute_setting_action(self, key):
        """Ayar aksiyonunu çalıştır"""
        if key == "clear_favorites":
            self.favorites = []
            self._save_json("yt_favorites.json", [])
            self.status = self.t("msg_fav_cleared")
            self.status_type = "ok"
        elif key == "clear_history":
            self.history = []
            self._save_json("yt_history.json", [])
            self.status = self.t("msg_history_cleared")
            self.status_type = "ok"
        elif key == "clear_cache":
            try:
                import shutil
                if os.path.exists(self.image_cache_dir):
                    shutil.rmtree(self.image_cache_dir)
                    os.makedirs(self.image_cache_dir, exist_ok=True)
                self.image_cache.clear()
                self.failed_images.clear()
                self.status = self.t("msg_cache_cleared")
                self.status_type = "ok"
            except Exception as e:
                self.status = f"Error: {str(e)[:20]}"
                self.status_type = "error"
        self.need_redraw = True
    
    def render_video_list(self, videos, start_y, height):
        card_h = 80
        margin = 6
        thumb_w = 142
        thumb_h = 70
        
        # Loading durumunu kontrol et
        is_batch_loading = (self.current_nav == NAV_HOME and self.home_batch_loading) or \
                          (self.current_nav == NAV_SEARCH and self.search_batch_loading)
        
        # Sticky loading spinner mantığı:
        # 1. En alta inildiğinde tetikle
        # 2. Son 3 video içinde kaldıkça görünür kalsın
        # 3. 3. videodan yukarı çıkılırsa veya yükleme biterse sıfırla
        is_at_bottom = self.selected >= len(videos) - 1 if len(videos) > 0 else False
        is_near_end = self.selected >= len(videos) - 3 if len(videos) >= 3 else True
        
        # En alta inildiğinde flag'i aktifleştir
        if is_at_bottom and is_batch_loading:
            self.loading_spinner_triggered = True
        
        # Son 3 videodan çıkıldığında veya yükleme bittiğinde sıfırla
        if not is_near_end or not is_batch_loading:
            self.loading_spinner_triggered = False
        
        show_loading_card = self.loading_spinner_triggered and is_batch_loading and len(videos) > 0
        
        # Görünür video sayısı - loading kartı için bir azalt
        base_visible = height // (card_h + margin)
        visible = base_visible - 1 if show_loading_card and base_visible > 1 else base_visible
        
        # Scroll
        if self.selected >= len(videos):
            self.selected = max(0, len(videos) - 1)
        if self.selected < self.scroll:
            self.scroll = self.selected
        elif self.selected >= self.scroll + visible:
            self.scroll = self.selected - visible + 1
        
        for i, video in enumerate(videos[self.scroll:self.scroll + visible]):
            idx = self.scroll + i
            y = start_y + i * (card_h + margin)
            selected = idx == self.selected
            
            # Card
            self.draw_rect(10, y, SCREEN_WIDTH - 20, card_h, Colors.CARD_SELECTED if selected else Colors.CARD_BG)
            if selected:
                self.draw_rect(10, y, 4, card_h, Colors.YT_RED)
            
            # Thumbnail
            self.draw_thumbnail(18, y + 5, thumb_w, thumb_h, video.thumbnail)
            
            # Duration
            if video.duration:
                dur = video.format_duration()
                dur_w = len(dur) * 7 + 6
                self.draw_rect(18 + thumb_w - dur_w - 4, y + thumb_h - 13, dur_w, 14, (0, 0, 0), 200)
                self.draw_text(dur, 18 + thumb_w - dur_w, y + thumb_h - 11, Colors.TEXT_PRIMARY, self.font_tiny)
            
            # Info
            info_x = 18 + thumb_w + 10
            title = video.title[:32] + "..." if len(video.title) > 32 else video.title
            self.draw_text(title, info_x, y + 8, Colors.TEXT_PRIMARY if selected else Colors.TEXT_SECONDARY, self.font_small)
            
            channel = video.channel[:25] if video.channel else ""
            self.draw_text(channel, info_x, y + 28, Colors.TEXT_TERTIARY, self.font_tiny)
            
            meta = " - ".join(filter(None, [video.format_views(), video.format_date()]))
            self.draw_text(meta[:30], info_x, y + 44, Colors.TEXT_TERTIARY, self.font_tiny)
        
        # Listenin sonunda ve yükleme devam ediyorsa loading kartı göster
        if show_loading_card:
            # Görünen video sayısının hemen altına loading kartı çiz
            displayed_count = min(len(videos) - self.scroll, visible)
            spinner_card_y = start_y + displayed_count * (card_h + margin)
            
            # Loading kartı arka planı (video kartı gibi)
            self.draw_rect(10, spinner_card_y, SCREEN_WIDTH - 20, card_h, Colors.BG_SECONDARY)
            
            # Spinner'ı ortala
            self.draw_spinner(SCREEN_WIDTH // 2, spinner_card_y + card_h // 2 - 5, radius=12, dot_size=3)
            self.draw_text(self.t("msg_loading"), SCREEN_WIDTH // 2 - 35, spinner_card_y + card_h // 2 + 18, Colors.TEXT_TERTIARY, self.font_small)
        
        # Scrollbar
        if len(videos) > base_visible:
            sb_h = height
            thumb = max(20, int(sb_h * visible / len(videos)))
            thumb_y = start_y + int((sb_h - thumb) * self.scroll / max(1, len(videos) - visible))
            self.draw_rect(SCREEN_WIDTH - 8, start_y, 4, sb_h, Colors.PROGRESS_BG)
            self.draw_rect(SCREEN_WIDTH - 8, thumb_y, 4, thumb, Colors.YT_RED)
    
    def render_keyboard(self):
        # Calculate base kb_y
        base_kb_y = SCREEN_HEIGHT - 260
        
        # Adjust for extra rows
        num_rows = len(self.keyboard_layout)
        if num_rows > 4:
            base_kb_y -= (num_rows - 4) * 38
            
        kb_y = base_kb_y
        
        self.draw_rect(0, kb_y - 45, SCREEN_WIDTH, SCREEN_HEIGHT - kb_y + 45, (0, 0, 0), 240)
        
        # Input
        input_y = kb_y - 38
        self.draw_rect(15, input_y, SCREEN_WIDTH - 30, 32, Colors.BG_TERTIARY)
        self.draw_rect(15, input_y, SCREEN_WIDTH - 30, 2, Colors.YT_RED)
        
        query = self.search_query or self.t("kb_search_placeholder")
        color = Colors.TEXT_PRIMARY if self.search_query else Colors.TEXT_TERTIARY
        
        # Yazıyı çiz ve gerçek genişliği al
        display_query = query[:35]
        text_width = self.draw_text(display_query, 25, input_y + 7, color, self.font)
        
        # Cursor - gerçek metin genişliğine göre konumlandır
        if self.search_query and (self.frame_count // 15) % 2:
            cursor_x = 25 + text_width + 2
            self.draw_rect(cursor_x, input_y + 5, 2, 20, Colors.YT_RED)
        
        # Layout preparation
        layout = self.keyboard_layout.copy()
        if self.caps_lock:
            # Sadece harfleri büyüt (satır 1, 2, 3 - rakamlar satır 0)
            layout = [layout[0]] + [[c.upper() for c in row] for row in layout[1:4]]
        
        # Calculate dynamic key width
        max_keys = max(len(row) for row in layout)
        gap = 4
        side_margin = 10
        available_width = SCREEN_WIDTH - (2 * side_margin)
        key_w = (available_width - (max_keys - 1) * gap) // max_keys
        key_h = 34
        
        def get_row_offset(row_len, k_w, g_s):
            row_width = row_len * k_w + (row_len - 1) * g_s
            return (SCREEN_WIDTH - row_width) // 2
        
        for row_i, row in enumerate(layout):
            row_offset = get_row_offset(len(row), key_w, gap)
            for col_i, char in enumerate(row):
                x = row_offset + col_i * (key_w + gap)
                y = kb_y + row_i * (key_h + gap)
                selected = self.keyboard_row == row_i and self.keyboard_col == col_i
                
                self.draw_rect(x, y, key_w, key_h, Colors.YT_RED if selected else Colors.BG_TERTIARY)
                self.draw_text(char, x + key_w//2 - 5, y + 7, Colors.TEXT_PRIMARY, self.font)
        
        # Controls
        control_row_index = len(layout)
        ctrl_y = kb_y + control_row_index * (key_h + gap)
        
        lang = self.settings.get("language", "English")
        if lang in ["Ukrainian", "Russian"]:
            toggle_label = "Кир" if getattr(self, 'alphabet_mode', 'Cyrillic') == 'Cyrillic' else "Lat"
            ctrls = [
                ("ABC" if self.caps_lock else "abc", 55),
                (toggle_label, 55),
                (self.t("kb_space"), 170),
                ("<-", 55),
                (self.t("kb_go"), 80)
            ]
        else:
            ctrls = [
                ("ABC" if self.caps_lock else "abc", 55),
                (self.t("kb_space"), 180),
                ("<-", 55),
                (self.t("kb_go"), 80)
            ]

        total_ctrl_w = sum(c[1] for c in ctrls) + gap * (len(ctrls) - 1)
        ctrl_x = (SCREEN_WIDTH - total_ctrl_w) // 2
        
        for i, (label, w) in enumerate(ctrls):
            selected = self.keyboard_row == control_row_index and self.keyboard_col == i
            
            # Highlight logic
            is_go_btn = (lang in ["Ukrainian", "Russian"] and i == 4) or (lang not in ["Ukrainian", "Russian"] and i == 3)
            bg = Colors.YT_RED if (selected or is_go_btn) else Colors.BG_TERTIARY
            
            self.draw_rect(ctrl_x, ctrl_y, w, key_h, bg if not selected else Colors.YT_RED)
            self.draw_text(label, ctrl_x + w//2 - len(label)*4, ctrl_y + 7, Colors.TEXT_PRIMARY, self.font_small)
            ctrl_x += w + gap
        
        self.draw_text(self.t("help_keyboard"), 140, ctrl_y + key_h + 8, Colors.TEXT_TERTIARY, self.font_tiny)
    
    # === Input ===
    def _get_list(self):
        if self.current_nav == NAV_HOME:
            return self.home_videos
        if self.current_nav == NAV_SEARCH:
            return self.search_results
        if self.current_nav == NAV_FAVORITES:
            return self.favorites
        if self.current_nav == NAV_HISTORY:
            return self.history
        return []
    
    def handle_keyboard_nav(self, d):
        lang = self.settings.get("language", "English")
        ctrl_len = 5 if lang in ["Ukrainian", "Russian"] else 4
        
        # Calculate lengths dynamically based on current layout
        lens = [len(row) for row in self.keyboard_layout] + [ctrl_len]
        max_row = len(self.keyboard_layout)
        
        if d == "up" and self.keyboard_row > 0:
            self.keyboard_row -= 1
            self.keyboard_col = min(self.keyboard_col, lens[self.keyboard_row] - 1)
        elif d == "down" and self.keyboard_row < max_row:
            self.keyboard_row += 1
            self.keyboard_col = min(self.keyboard_col, lens[self.keyboard_row] - 1)
        elif d == "left" and self.keyboard_col > 0:
            self.keyboard_col -= 1
        elif d == "right" and self.keyboard_col < lens[self.keyboard_row] - 1:
            self.keyboard_col += 1
        self.need_redraw = True
    
    def handle_keyboard_select(self):
        num_char_rows = len(self.keyboard_layout)
        
        if self.keyboard_row < num_char_rows:
            layout = self.keyboard_layout.copy()
            if self.caps_lock:
                # Apply caps lock only to letter rows (usually rows 1, 2, 3... but depends on layout)
                # Since we don't know exactly which rows are letters, let's try to uppercase strings
                # For safety, let's assume row 0 is numbers/symbols if it matches standard patterns, 
                # but simply uppercasing everything in character rows is usually safe for virtual keyboards 
                # unless they have numbers mixed in a way we don't expect.
                # The previous logic was hardcoded [1:4].
                # Let's keep it somewhat consistent but safer:
                new_layout = []
                for i, row in enumerate(layout):
                    if i == 0: # Usually numbers
                        new_layout.append(row)
                    else:
                        new_layout.append([c.upper() for c in row])
                layout = new_layout
                
            row = layout[self.keyboard_row]
            if self.keyboard_col < len(row) and len(self.search_query) < 50:
                self.search_query += row[self.keyboard_col]
        else:
            lang = self.settings.get("language", "English")
            if lang in ["Ukrainian", "Russian"]:
                if self.keyboard_col == 0:
                    self.caps_lock = not self.caps_lock
                elif self.keyboard_col == 1:
                    self.alphabet_mode = 'Latin' if getattr(self, 'alphabet_mode', 'Cyrillic') == 'Cyrillic' else 'Cyrillic'
                    self.keyboard_layout = self._get_keyboard_layout()
                    self.keyboard_row = min(self.keyboard_row, len(self.keyboard_layout))  # Klavye düzeni değişince row'u koru
                    self.keyboard_col = 0
                elif self.keyboard_col == 2 and len(self.search_query) < 50:
                    self.search_query += " "
                elif self.keyboard_col == 3 and self.search_query:
                    self.search_query = self.search_query[:-1]
                elif self.keyboard_col == 4 and self.search_query.strip():
                    self.search_youtube(self.search_query.strip())
            else:
                if self.keyboard_col == 0:
                    self.caps_lock = not self.caps_lock
                elif self.keyboard_col == 1 and len(self.search_query) < 50:
                    self.search_query += " "
                elif self.keyboard_col == 2 and self.search_query:
                    self.search_query = self.search_query[:-1]
                elif self.keyboard_col == 3 and self.search_query.strip():
                    self.search_youtube(self.search_query.strip())
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
            # Sonraki batch'i yükle gerekiyorsa
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
            if videos and self.selected < len(videos):
                self.play_video(videos[self.selected])
        self.need_redraw = True
    
    def action_back(self):
        if self.exit_confirm_active:
            self.exit_confirm_active = False
            self.exit_confirm_selection = 0
        elif self.search_active:
            self.search_active = False
        elif self.is_playing:
            self.stop_playback()
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
        """Seçili videoyu favorilere ekle veya çıkar"""
        videos = self._get_list()
        if not videos or self.selected >= len(videos):
            return
        
        video = videos[self.selected]
        
        # Favori listesinde var mı kontrol et
        is_favorite = any(v.id == video.id for v in self.favorites)
        
        if is_favorite:
            # Favorilerden çıkar
            self.favorites = [v for v in self.favorites if v.id != video.id]
            self.status = self.t("msg_removed_fav")
        else:
            # Favorilere ekle
            self.favorites.insert(0, video)
            self.status = self.t("msg_added_fav")
        
        self._save_json("yt_favorites.json", self.favorites)
        self.status_type = "ok"
        self.need_redraw = True
    
    def process_repeat(self):
        if not self.key_held:
            return
        now = SDL_GetTicks()
        if now - self.key_hold_start < 400:
            return
        if now - self.last_repeat >= 100:
            self.last_repeat = now
            if self.search_active:
                self.handle_keyboard_nav(self.key_held)
            elif self.key_held == "up":
                self.action_up()
            elif self.key_held == "down":
                self.action_down()
    
    def handle_event(self, event):
        now = SDL_GetTicks()
        
        # Video yüklenirken tüm input'ları devre dışı bırak
        if self.is_loading_video:
            return
            
        if self.exit_confirm_active:
            if event.type == SDL_CONTROLLERBUTTONDOWN:
                btn = event.cbutton.button
                if btn == SDL_CONTROLLER_BUTTON_DPAD_LEFT:
                    self.exit_confirm_selection = 0
                    self.need_redraw = True
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_RIGHT:
                    self.exit_confirm_selection = 1
                    self.need_redraw = True
                elif btn == SDL_CONTROLLER_BUTTON_A:
                    if self.exit_confirm_selection == 1:
                        self.running = False
                    else:
                        self.exit_confirm_active = False
                    self.need_redraw = True
                elif btn == SDL_CONTROLLER_BUTTON_B:
                    self.exit_confirm_active = False
                    self.need_redraw = True
            elif event.type == SDL_KEYDOWN:
                key = event.key.keysym.sym
                if key in (SDLK_LEFT, SDLK_a):
                    self.exit_confirm_selection = 0
                    self.need_redraw = True
                elif key in (SDLK_RIGHT, SDLK_d):
                    self.exit_confirm_selection = 1
                    self.need_redraw = True
                elif key in (SDLK_RETURN, SDLK_z):
                    if self.exit_confirm_selection == 1:
                        self.running = False
                    else:
                        self.exit_confirm_active = False
                    self.need_redraw = True
                elif key in (SDLK_ESCAPE, SDLK_x):
                    self.exit_confirm_active = False
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
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_LEFT:
                    self.handle_keyboard_nav("left")
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_RIGHT:
                    self.handle_keyboard_nav("right")
                elif btn == SDL_CONTROLLER_BUTTON_A:
                    self.handle_keyboard_select()
                elif btn == SDL_CONTROLLER_BUTTON_B:
                    self.search_active = False
                    self.need_redraw = True
                elif btn == SDL_CONTROLLER_BUTTON_START:
                    if self.search_query.strip():
                        self.search_youtube(self.search_query.strip())
                elif btn == SDL_CONTROLLER_BUTTON_Y:
                    if self.search_query:
                        self.search_query = self.search_query[:-1]
                        self.need_redraw = True
            elif event.type == SDL_CONTROLLERBUTTONUP:
                self.key_held = None
            elif event.type == SDL_JOYHATMOTION:
                hat = event.jhat.value
                if hat & SDL_HAT_UP:
                    self.handle_keyboard_nav("up")
                    self.key_held, self.key_hold_start = "up", now
                elif hat & SDL_HAT_DOWN:
                    self.handle_keyboard_nav("down")
                    self.key_held, self.key_hold_start = "down", now
                elif hat & SDL_HAT_LEFT:
                    self.handle_keyboard_nav("left")
                elif hat & SDL_HAT_RIGHT:
                    self.handle_keyboard_nav("right")
                else:
                    self.key_held = None
            return
        
        if event.type == SDL_CONTROLLERBUTTONDOWN:
            btn = event.cbutton.button
            
            # Video oynatılırken kontroller
            if self.is_playing:
                if btn == SDL_CONTROLLER_BUTTON_B:
                    # ffplay ise B tuşunu yoksay
                    player_name = os.path.basename(self.video_player) if self.video_player else ""
                    if "ffplay" in player_name:
                        return
                    self.stop_playback()
                elif btn == SDL_CONTROLLER_BUTTON_Y:
                    self.player_toggle_pause()
                elif btn == SDL_CONTROLLER_BUTTON_LEFTSHOULDER:
                    self.player_seek(-10)  # 10 saniye geri
                elif btn == SDL_CONTROLLER_BUTTON_RIGHTSHOULDER:
                    self.player_seek(10)   # 10 saniye ileri
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_LEFT:
                    self.player_seek(-5)   # 5 saniye geri
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_RIGHT:
                    self.player_seek(5)    # 5 saniye ileri
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_UP:
                    self.player_brightness(5)  # Parlaklık artır
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_DOWN:
                    self.player_brightness(-5)  # Parlaklık azalt
                return
            
            # Settings sayfasında kontroller
            if self.current_nav == NAV_SETTINGS:
                if btn == SDL_CONTROLLER_BUTTON_A:
                    # A tuşu ile seçili ayarı değiştir veya aksiyonu çalıştır
                    label, key, options = self.settings_items[self.settings_selected]
                    if options is None:
                        # Action item - çalıştır
                        self.execute_setting_action(key)
                    else:
                        # Seçenekli ayar - değeri değiştir
                        self.change_setting(1)
                elif btn == SDL_CONTROLLER_BUTTON_B:
                    self.action_back()
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_UP:
                    if self.settings_selected > 0:
                        self.settings_selected -= 1
                        self.need_redraw = True
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_DOWN:
                    if self.settings_selected < len(self.settings_items) - 1:
                        self.settings_selected += 1
                        self.need_redraw = True
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_LEFT:
                    # Action item'da (options=None) sekme değiştir, değilse ayarı değiştir
                    _, _, options = self.settings_items[self.settings_selected]
                    if options is None:
                        self.action_left()
                    else:
                        self.change_setting(-1)
                elif btn == SDL_CONTROLLER_BUTTON_DPAD_RIGHT:
                    # Action item'da (options=None) sekme değiştir, değilse ayarı değiştir
                    _, _, options = self.settings_items[self.settings_selected]
                    if options is None:
                        self.action_right()
                    else:
                        self.change_setting(1)
                elif btn == SDL_CONTROLLER_BUTTON_LEFTSHOULDER:
                    self.action_left()
                elif btn == SDL_CONTROLLER_BUTTON_RIGHTSHOULDER:
                    self.action_right()
                return
            
            if btn == SDL_CONTROLLER_BUTTON_A:
                self.action_select()
            elif btn == SDL_CONTROLLER_BUTTON_B:
                self.action_back()
            elif btn == SDL_CONTROLLER_BUTTON_X:
                self.action_search()
            elif btn == SDL_CONTROLLER_BUTTON_Y:
                self.toggle_favorite()  # Y tuşu ile favorilere ekle/çıkar
            elif btn == SDL_CONTROLLER_BUTTON_DPAD_UP:
                self.action_up()
                self.key_held, self.key_hold_start = "up", now
            elif btn == SDL_CONTROLLER_BUTTON_DPAD_DOWN:
                self.action_down()
                self.key_held, self.key_hold_start = "down", now
            elif btn == SDL_CONTROLLER_BUTTON_DPAD_LEFT:
                self.action_left()
            elif btn == SDL_CONTROLLER_BUTTON_DPAD_RIGHT:
                self.action_right()
            elif btn in (SDL_CONTROLLER_BUTTON_LEFTSHOULDER, SDL_CONTROLLER_BUTTON_RIGHTSHOULDER):
                if btn == SDL_CONTROLLER_BUTTON_LEFTSHOULDER:
                    self.action_left()
                else:
                    self.action_right()
            elif btn == SDL_CONTROLLER_BUTTON_START:
                self.action_search()
        elif event.type == SDL_CONTROLLERBUTTONUP:
            self.key_held = None
        elif event.type == SDL_JOYHATMOTION:
            hat = event.jhat.value
            
            # Video oynatılırken kontroller
            if self.is_playing:
                if hat & SDL_HAT_LEFT:
                    self.player_seek(-5)
                elif hat & SDL_HAT_RIGHT:
                    self.player_seek(5)
                elif hat & SDL_HAT_UP:
                    self.player_brightness(5)
                elif hat & SDL_HAT_DOWN:
                    self.player_brightness(-5)
                return
            
            # Settings sayfasında
            if self.current_nav == NAV_SETTINGS:
                if hat & SDL_HAT_UP:
                    if self.settings_selected > 0:
                        self.settings_selected -= 1
                        self.need_redraw = True
                elif hat & SDL_HAT_DOWN:
                    if self.settings_selected < len(self.settings_items) - 1:
                        self.settings_selected += 1
                        self.need_redraw = True
                elif hat & SDL_HAT_LEFT:
                    # Action item'da (options=None) sekme değiştir, değilse ayarı değiştir
                    _, _, options = self.settings_items[self.settings_selected]
                    if options is None:
                        self.action_left()
                    else:
                        self.change_setting(-1)
                elif hat & SDL_HAT_RIGHT:
                    # Action item'da (options=None) sekme değiştir, değilse ayarı değiştir
                    _, _, options = self.settings_items[self.settings_selected]
                    if options is None:
                        self.action_right()
                    else:
                        self.change_setting(1)
                else:
                    self.key_held = None
                return
            
            if hat & SDL_HAT_UP:
                self.action_up()
                self.key_held, self.key_hold_start = "up", now
            elif hat & SDL_HAT_DOWN:
                self.action_down()
                self.key_held, self.key_hold_start = "down", now
            elif hat & SDL_HAT_LEFT:
                self.action_left()
            elif hat & SDL_HAT_RIGHT:
                self.action_right()
            else:
                self.key_held = None
        elif event.type == SDL_KEYDOWN:
            key = event.key.keysym.sym
            if key in (SDLK_UP, SDLK_w):
                self.action_up()
            elif key in (SDLK_DOWN, SDLK_s):
                self.action_down()
            elif key in (SDLK_LEFT, SDLK_a):
                self.action_left()
            elif key in (SDLK_RIGHT, SDLK_d):
                self.action_right()
            elif key in (SDLK_RETURN, SDLK_z):
                self.action_select()
            elif key in (SDLK_ESCAPE, SDLK_x):
                self.action_back()
    
    def run(self):
        if self.ytdlp_path:
            self.load_trending()
        
        event = SDL_Event()
        last_render_time = 0
        while self.running:
            while SDL_PollEvent(event):
                if event.type == SDL_QUIT:
                    self.running = False
                else:
                    self.handle_event(event)
            
            self.process_repeat()
            
            current_time = SDL_GetTicks()
            
            # Video yüklenirken loading ekranı göster
            if self.is_loading_video:
                self.render_loading_screen(self.t("msg_loading_video"), self.current_video.title if self.current_video else "")
            # Video oynatılırken render yapma (pencere zaten gizli)
            elif not self.is_playing:
                # Batch loading veya arama sırasında da render yap (spinner animasyonu için)
                is_batch_loading = self.home_batch_loading or self.search_batch_loading
                # Her 100ms'de bir zorunlu render yap (thread'den gelen değişiklikleri yakalamak için)
                force_render = (current_time - last_render_time) >= 100
                if self.need_redraw or self.is_loading or self.loading_images or is_batch_loading or self.is_searching or force_render:
                    self.render()
                    last_render_time = current_time
            
            SDL_Delay(16)
        
        self.cleanup()
    
    def cleanup(self):
        self.stop_playback()
        
        for tex, _, _ in self.text_cache.values():
            if tex:
                SDL_DestroyTexture(tex)
        for tex, _, _ in self.image_cache.values():
            if tex:
                SDL_DestroyTexture(tex)
        
        if self.font:
            ttf.TTF_CloseFont(self.font)
        if self.font_large:
            ttf.TTF_CloseFont(self.font_large)
        if self.font_small:
            ttf.TTF_CloseFont(self.font_small)
        if self.font_tiny:
            ttf.TTF_CloseFont(self.font_tiny)
        
        if self.controller:
            SDL_GameControllerClose(self.controller)
        if self.joystick:
            SDL_JoystickClose(self.joystick)
        
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