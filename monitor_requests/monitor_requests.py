from utils.url_handling import build_url
import xbmcplugin
import xbmcgui
import xbmc
from utils.utils import add_next_page_button


def show_requests(page, jellyseer_client, radarr_client, sonarr_client, addon_handle, settings, pagesize = 25):
    """Display user's requests with pagination"""   
    try:
        data = jellyseer_client.api_request("/request", params={"take": pagesize, "skip": (page - 1) * pagesize, "sort": "added", "filter": "all"}, 
                                        use_cache = False)
    except:
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        return
    requested_items = data.get('results', []) if data else []

    xbmcplugin.setContent(addon_handle, 'videos')
    requests_data = settings.get_preferences("episode_requests")
    if requests_data.get("requests", {}):
        list_item = xbmcgui.ListItem(label="Single Episodes")
        icon = "DefaultSets.png"
        list_item.setArt({'icon': icon, 'thumb': icon})
        url = build_url({"mode": "show_requested_episodes"})
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)    
    
    for item in requested_items:
        media = item.get('media', {})
        tmdb_id = media.get('tmdbId')
        request_id = item.get("id", -1)
        seer_status = media.get('status')
        media_type = media.get('mediaType')
        try:
            mediaData = jellyseer_client.api_request(f"/{media_type}/{tmdb_id}", params={})
        except:
            continue
        if(media_type == "movie"):
          from monitor_requests.monitor_movies import show_movie_request
          show_movie_request(tmdb_id, request_id, mediaData, seer_status, item, radarr_client, addon_handle)
        elif(media_type == "tv"):
          from monitor_requests.monitor_shows import show_series_request
          show_series_request(tmdb_id, request_id, mediaData, seer_status, item, sonarr_client, addon_handle)
    
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
    total_pages = data.get('pageInfo', {}).get("pages", 1)
    add_next_page_button({"mode": "requests"}, page, total_pages, addon_handle)
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)    


def get_url_by_status(status, tmdb_id, request_id, media_type, season=-1, episode_number=-1):
        is_directory = False
        tmdb_type = media_type
        if media_type == "episode":
            tmdb_type = "tv"
        if media_type != "movie":
            is_directory = True
        if status in [2, 3]:
            url = build_url({"mode": "cancel_request", "request_id": request_id, "handle_empty_directory": is_directory, "type": media_type})
        elif status == 5:
            url = build_url({"mode": "play_local_file", "id": tmdb_id, "type": tmdb_type, "season": season, "episode": episode_number})
        else:
            url = build_url({'mode': 'request', 'type': media_type, 'id': tmdb_id, "season": season, "episode": episode_number, "handle_empty_directory": is_directory})
        return url

def get_context_menu_by_status(status, tmdb_id, request_id, media_type, season=-1, episode_nr=-1, episode_id=-1):
        context_menu = []
        if status in [2, 3] and media_type != "episode":
            url = build_url({"mode": "cancel_request", "request_id": request_id, "type": media_type}, )
            context_menu.append(('Cancel Request', f'RunPlugin({url})'))
        if  media_type != "movie":
            url = build_url({"mode": "request", "id": tmdb_id, "type": "tv", "season": season})
            context_menu.append(('Request more', f'RunPlugin({url})'))
        if status == 5:
            url = build_url({"mode": "delete_file", "id": tmdb_id, "type": media_type, "season": season, "episode": episode_nr, "episode_id": episode_id})
            context_menu.append(('Delete File', f'RunPlugin({url})'))  
        context_menu.append(('Show Details', f'RunPlugin({build_url({"mode": "show_details", "type": media_type, "id": tmdb_id})})'))
        context_menu.append(('Refresh', f'RunPlugin({build_url({"mode": "refresh"})})'))
        return context_menu

def is_directory(status):
    if status == 5:
        return False
    return True

def cancel_request(request_id, jellyseer_client, media_type):
    from utils.logging import notify_info, notify_error
    """Cancel a pending request"""
    if media_type == "episode":
        xbmcgui.Dialog().info('KodiSeerr', "Single episode requests can not be canceled.")
        return
    if not xbmcgui.Dialog().yesno('KodiSeerr', "Do you want to cancel this request?"):
        return
    if request_id != -1:    
        try:
            jellyseer_client.api_request(f"/request/{request_id}", method="DELETE")
        except:
            return
        notify_info("Request cancelled")
        xbmc.executebuiltin('Container.Refresh')
    else:
        notify_error("Could not find a matching request")