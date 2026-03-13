import sys
from delete_file import delete_file
from favorites import add_to_favorites, list_favorites, remove_from_favorites
from list_collections import list_collections, show_collection_details
from list_recently_added import list_recently_added
from play_local_file import play_local_file
from request import do_request
from show_details import show_details
from test_connection import test_connection
from utils import build_url, jump_to_page
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import urllib.parse
from create_client import create_client
from jellyseerr_api import JellyseerrClient
from radarr_api import RadarrClient
from sonarr_api import SonarrClient
from cache import *
from monitor_requests import show_requested_episodes, show_requested_episodes_by_season
from monitor_requests import show_requests
from monitor_requests import show_requested_seasons
from monitor_requests import cancel_request
from search import handle_search_episodes, handle_search_item, handle_search_season, search
from statistics import show_statistics

load_cache()
image_base = "https://image.tmdb.org/t/p/w500"
favorites_path = xbmcvfs.translatePath(f"special://profile/addon_data/{addon.getAddonInfo('id')}/favorites.json")
preferences_path = xbmcvfs.translatePath(f"special://profile/addon_data/{addon.getAddonInfo('id')}/preferences.json")
addon = xbmcaddon.Addon()
addon_handle = int(sys.argv[1])
addon_path = addon.getAddonInfo('path')

base_url = sys.argv[0]
args = dict(urllib.parse.parse_qsl(sys.argv[2][1:]))
jellyseer_client = create_client(JellyseerrClient)
radarr_client = None
sonarr_client = None
enable_ask_4k = addon.getSettingBool('enable_ask_4k')
enable_radarr = addon.getSettingBool('radarr_enable')
enable_sonarr = addon.getSettingBool('sonarr_enable')
if enable_radarr:
 radarr_client = create_client(RadarrClient)
if enable_sonarr:
 sonarr_client = create_client(SonarrClient)

def list_main_menu():
    xbmcplugin.setContent(addon_handle, 'files')
    items = [
        ('recently_added', 'Recently Added', 'DefaultRecentlyAddedMovies.png', True),
        ('collections', 'Collections', 'DefaultSets.png', True),
        (None, None, None, False),
        ('favorites', 'My Favorites', 'DefaultFavourites.png', True),
        ('requests', 'Request Progress', 'DefaultInProgressShows.png', True),
        ('statistics', 'Statistics', 'DefaultAddonInfoProvider.png', False),
        (None, None, None, False),
        ('search', 'Search', 'DefaultAddonsSearch.png', True),
        ('test_connection', 'Test Connection', 'DefaultAddonService.png', False),
    ]
    
    for item in items:
        if item[0] is None:
            continue
        mode, label, icon, is_folder = item
        list_item = xbmcgui.ListItem(label)
        list_item.setArt({'icon': icon, 'thumb': icon})
        
        if mode == 'genres_movie':
            url = build_url({'mode': 'genres', 'media_type': 'movie'})
        elif mode == 'genres_tv':
            url = build_url({'mode': 'genres', 'media_type': 'tv'})
        else:
            url = build_url({'mode': mode})
        
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)
    
    xbmcplugin.endOfDirectory(addon_handle)

def report_issue(media_type, media_id):
    """Report an issue with media"""
    issue_types = ['Video Issue', 'Audio Issue', 'Subtitles Issue', 'Other']
    selected = xbmcgui.Dialog().select('Select Issue Type', issue_types)
    if selected < 0:
        return
    message = xbmcgui.Dialog().input('Describe the issue (optional)')
    try:
        payload = {
            "issueType": selected + 1,
            "message": message or ""
        }
        jellyseer_client.api_request(f"/{media_type}/{media_id}/issue", method="POST", data=payload)
        xbmcgui.Dialog().notification('KodiSeerr', 'Issue reported', xbmcgui.NOTIFICATION_INFO)
    except Exception as e:
        xbmc.log(f"[KodiSeerr] Issue report error: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('KodiSeerr', 'Failed to report issue', xbmcgui.NOTIFICATION_ERROR)

mode = args.get('mode')
page = int(args.get('page', 1))

if not mode:
    list_main_menu()
elif mode == "test_connection":
    test_connection()
elif mode == "clear_cache":
    clear_cache()
elif mode == "statistics":
    show_statistics(jellyseer_client)
elif mode == "favorites":
    list_favorites(favorites_path, jellyseer_client, addon_handle)
elif mode == "add_favorite":
    add_to_favorites(args.get('type'), args.get('id'), favorites_path)
elif mode == "remove_favorite":
    remove_from_favorites(args.get('type'), args.get('id'),  favorites_path)
elif mode == "show_details":
    show_details(args.get('type'), args.get('id'), jellyseer_client)
elif mode == "report_issue":
    report_issue(args.get('type'), args.get('id'))
elif mode == "cancel_request":
    cancel_request(args.get('request_id'), jellyseer_client)
elif mode == "jump_to_page":
    jump_to_page(args)
elif mode == "collections":
    list_collections(page, jellyseer_client, image_base, addon_handle)
elif mode == "collection_details":
    show_request_status = addon.getSettingBool('show_request_status')
    show_collection_details(args.get('collection_id'), show_request_status, jellyseer_client, addon_handle)
elif mode == "recently_added":
    list_recently_added(page, jellyseer_client, addon_handle)
elif mode == "search":
    search_string = args.get("query")
    show_status = addon.getSettingBool('show_request_status')
    external_keyboard = args.get("ext_keyboard", False)
    search(search_string, jellyseer_client, show_status, addon_handle, page=page, external_keyboard=bool(external_keyboard))
elif mode == "handle_search_item":
    handle_search_item( args.get("type"), args.get("id"), jellyseer_client)
elif mode == "handle_search_season":
    handle_search_season(args.get("id"), jellyseer_client, addon_handle)
elif mode == "handle_search_episode":
    handle_search_episodes(args.get("id"), args.get("season"), jellyseer_client, addon_handle)  
elif mode == "request":
    media_type = args.get("type")
    id = args.get("id")
    season = int(args.get("season", -1))
    episode = int(args.get("episode", -1))
    skip_dialog = args.get("skip_dialog", False)
    do_request(media_type, id, enable_ask_4k, jellyseer_client, addon, addon_handle, sonarr_client, season, episode, skip_dialog)
elif mode == "requests":
    show_requests(mode, page, jellyseer_client, radarr_client, sonarr_client, addon_handle, addon)
elif mode == "showrequestedseasons":
    id = args.get("id")
    show_requested_seasons(id, jellyseer_client, addon_handle, enable_sonarr)
elif mode == "show_requested_episodes_by_season":
    id = args.get("id")
    season = args.get("season")
    show_requested_episodes_by_season(id=id, season=season, jellyseer_client=jellyseer_client, sonarr_client=sonarr_client, addon_handle=addon_handle)
elif mode == "show_requested_episodes":
    show_requested_episodes(jellyseer_client, sonarr_client, addon, addon_handle)
elif mode == "play_local_file":
    play_local_file(args.get("id", 0), args.get("type"), jellyseer_client, addon_handle, args.get("season"), args.get("episode"))
elif mode == "delete_file":
    delete_file(args.get("id"), args.get("type"), jellyseer_client, sonarr_client, is_4k = False, season = -1, episode = -1)
clean_cache()
save_cache()
        