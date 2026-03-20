import sys
from cache import load_cache, save_cache, clean_cache
from Settings import Settings
from utils.url_handling import set_base_url
import xbmcvfs
import xbmcaddon
import urllib
from apis.create_client import create_client
from apis.jellyseerr_api import JellyseerrClient
from apis.radarr_api import RadarrClient
from apis.sonarr_api import SonarrClient
load_cache()
image_base = "https://image.tmdb.org/t/p/w500"
addon = xbmcaddon.Addon()
favorites_path = xbmcvfs.translatePath(f"special://profile/addon_data/{addon.getAddonInfo('id')}/favorites.json")
addon_data_path = xbmcvfs.translatePath(f"special://profile/addon_data/{addon.getAddonInfo('id')}")
settings = Settings(addon_data_path , addon)
addon_handle = int(sys.argv[1])
addon_path = addon.getAddonInfo('path')
base_url = sys.argv[0]
set_base_url(base_url)
args = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
jellyseer_client = create_client(JellyseerrClient)

radarr_client = None
sonarr_client = None
enable_radarr = settings.enable_radarr()
enable_sonarr = settings.enable_sonarr()
if enable_radarr:
 radarr_client = create_client(RadarrClient)
if enable_sonarr:
 sonarr_client = create_client(SonarrClient)

mode = args.get('mode')
page = int(args.get('page', 1))

if args.get("handle_empty_directory") == "True":
    from utils.utils import handle_empty_directory
    handle_empty_directory(addon_handle)

if not mode:
    from main_menu import main_menu
    main_menu(addon_handle)
elif mode == "test_connection":
    from test_connection import test_connection
    test_connection()
elif mode == "clear_cache":
    from cache import clear_cache
    clear_cache()
elif mode == "statistics":
    from statistics import show_statistics
    show_statistics(jellyseer_client)
elif mode == "favorites":
    from favorites import list_favorites
    list_favorites(favorites_path, jellyseer_client, addon_handle)
elif mode == "add_favorite":
    from favorites import add_to_favorites
    add_to_favorites(args.get('type'), args.get('id'), favorites_path)
elif mode == "remove_favorite":
    from favorites import remove_from_favorites
    remove_from_favorites(args.get('type'), args.get('id'),  favorites_path)
elif mode == "show_details":
    from show_details import show_details
    show_details(args.get('type'), args.get('id'), jellyseer_client)
elif mode == "report_issue":
    from report_issue import report_issue
    report_issue(args.get('type'), args.get('id'))
elif mode == "cancel_request":
    from monitor_requests.monitor_requests import cancel_request
    cancel_request(args.get('request_id', -1), jellyseer_client, args.get("type"))
elif mode == "jump_to_page":
    from utils.utils import jump_to_page
    jump_to_page(args)
elif mode == "collections":
    from list_collections import list_collections
    list_collections(page, jellyseer_client, image_base, addon_handle)
elif mode == "collection_details":
    from list_collections import show_collection_details
    show_collection_details(args.get('collection_id'), settings, jellyseer_client, addon_handle)
elif mode == "recently_added":
    from list_recently_added import list_recently_added
    list_recently_added(page, jellyseer_client, addon_handle)
elif mode == "search":
    from search import search
    search_string = args.get("query")
    external_keyboard = args.get("ext_keyboard", False)
    search(search_string, jellyseer_client, settings, addon_handle, page=page, external_keyboard=bool(external_keyboard))
elif mode == "browse_menu":
    from browse import browse_menu
    browse_menu(args.get("type"), args.get("id"), jellyseer_client, sonarr_client, settings, addon_handle, args.get("season", -1), args.get("episode", -1))
elif mode == "browse_handle_episodes":
    from browse import browse_handle_episodes
    browse_handle_episodes(args.get("id"), args.get("season"), jellyseer_client, addon_handle)  
elif mode == "request":
    from do_request.request_main import do_request
    media_type = args.get("type")
    id = args.get("id")
    season = int(args.get("season", -1))
    episode = int(args.get("episode", -1))
    skip_dialog = args.get("skip_dialog", False)
    do_request(media_type, id, settings, jellyseer_client, addon_handle, sonarr_client, season, episode, skip_dialog)
elif mode == "requests":
    from monitor_requests.monitor_requests import show_requests
    show_requests( page, jellyseer_client, radarr_client, sonarr_client, addon_handle, settings)
elif mode == "show_requested_seasons":
    from monitor_requests.monitor_shows import show_requested_seasons
    show_requested_seasons( args.get("id"), args.get("request_id"), jellyseer_client, addon_handle, enable_sonarr)
elif mode == "show_requested_episodes_by_season":
    from monitor_requests.monitor_shows import show_requested_episodes_by_season
    id = args.get("id")
    season = args.get("season")
    show_requested_episodes_by_season(id=id, season=season, jellyseer_client=jellyseer_client, sonarr_client=sonarr_client, addon_handle=addon_handle)
elif mode == "show_requested_episodes":
    from monitor_requests.monitor_shows import show_requested_episodes
    show_requested_episodes(jellyseer_client, sonarr_client, settings, addon_handle)
elif mode == "play_local_file":
    from play_local_file import play_local_file
    play_local_file(args.get("id", 0), args.get("type"), jellyseer_client, addon_handle, args.get("season"), args.get("episode"))
elif mode == "delete_file":
    from delete_file import delete_file
    delete_file(args.get("id"), args.get("type"), jellyseer_client, sonarr_client, settings, season = args.get("season"), episode_nr=args.get("episode"), episode_id = args.get("episode_id"))
elif mode == "refresh":
    import xbmc
    xbmc.executebuiltin('Container.Refresh')
elif mode == "trakt":
    from trakt import trakt
    trakt(args.get("trakt_mode" ,""), addon_handle, addon_data_path, page)

clean_cache()
save_cache()
        