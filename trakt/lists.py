from trakt.trakt_main import display_response
from utils.url_handling import build_url
from utils.utils import add_next_page_button, set_info_tag
import xbmcplugin
import xbmcgui


def show_user_lists(trakt_client, addon_handle, page=1, number_of_items=25): 
    try:
        user_ids = trakt_client.api_request("GET", "/users/settings").get("user", {}).get("ids", {})
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    user_slug = user_ids.get("slug")
    try:
        user_lists, total_pages =  trakt_client.paginated_request("GET", f"/users/{user_slug}/lists?page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    show_lists(user_lists, addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "show_user_lists"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_popular_lists(trakt_client, addon_handle, page=1, number_of_items=25):
    try:
        popular_lists, total_pages = trakt_client.paginated_request("GET", f"/lists/popular?page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    show_lists([l.get("list") for l in popular_lists], addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "show_trending_lists"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_trending_lists(trakt_client, addon_handle, page = 1, number_of_items=25):
    try:
        trending_lists, total_pages = trakt_client.paginated_request("GET", f"/lists/trending?page={page}&limit={number_of_items}")

    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    show_lists([l.get("list") for l in trending_lists], addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "show_trending_lists"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_lists(trakt_lists, addon_handle):
    for li in trakt_lists:
        name = li.get("name")
        description = li.get("description")
        likes = li.get("likes")
        list_id = li.get("ids").get("trakt")
        user_slug = li.get("user").get("ids").get("slug")
        list_item = xbmcgui.ListItem(label=name)
        list_item.setLabel(name)
        info = {'title': name,  'mediatype': 'movie',  'plot': description,  'votes': likes}
        set_info_tag(list_item, info)
        xbmcplugin.addDirectoryItem(addon_handle, build_url({"mode": "trakt", "trakt_mode": "show_list_items", "user_slug": user_slug, "list_id": list_id}), list_item, True)
    

def show_list_items(user_slug, list_id, trakt_client, addon_handle, page=1, number_of_items=25, is_watchlist = False):
    endpoint_url = f"/users/{user_slug}/lists/{list_id}/items?page={page}&limit={number_of_items}&extended=full,images"
    if is_watchlist:
        endpoint_url = f"/users/{user_slug}/watchlist?page={page}&limit={number_of_items}&extended=full,images"
    try:
        list_items, total_pages = trakt_client.paginated_request("GET", endpoint_url)
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    for item in list_items:
         media_type = item.get("type")
         display_type = "tv"
         media_info = None
         season_nr = -1 
         episode_nr = -1
         if media_type == "movie":
            display_type = "movie"
            media_info = item.get(media_type)
         elif media_type == "show":
             media_info = item.get(media_type)
         elif media_type == "season":
             media_info = item.get("show")
             season_nr = item.get(media_type).get("number")
         elif media_type == "episode":
             media_info = item.get("show")
             episode_data = item.get(media_type)
             episode_nr = episode_data.get("number")
             season_nr = episode_data.get("season")
         #TODO 
         #Display notes   

         display_response([media_info], display_type, addon_handle, season=season_nr, episode=episode_nr)
    add_next_page_button({"mode": "trakt", "trakt_mode": "show_list_items", "user_slug": user_slug, "list_id": list_id}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)    


def show_watchlist(trakt_client, addon_handle, page=1, number_of_items=25):
    try:
        user_ids = trakt_client.api_request("GET", "/users/settings").get("user", {}).get("ids", {})
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    user_slug = user_ids.get("slug")
    show_list_items(user_slug, -1, trakt_client, page, number_of_items, is_watchlist=True) 