import xbmcplugin
import xbmcgui
import xbmc
from utils import add_next_page_button, get_status_label, make_art
from utils import make_info
from utils import get_media_status
from utils import build_url
from utils import set_info_tag
def search(search_string, jellyseer_client, settings, addon_handle, page = 1, external_keyboard = False):
    #make sure we get new search item by avoiding caching
    if not search_string and not external_keyboard:
       search_string = xbmcgui.Dialog().input('Search for Movie or TV Show')
    if search_string:
        xbmcplugin.setContent(addon_handle, 'videos')
        data = jellyseer_client.api_request('/search', params={'query': search_string, "page": page})
        results = data.get('results', []) if data else []
        total_pages = data.get("totalPages", 1)
        for item in results:
            media_type = item.get('mediaType', 'movie')
            title = item.get('title') or item.get('name')
            release_date = item.get('releaseDate') or item.get('firstAirDate')
            year = int(release_date.split("-")[0]) if release_date and release_date.split("-")[0].isdigit() else None
            type_label = "(Movie)" if media_type == "movie" else "(TV Show)"
            full_title = f"{title} ({year}) {type_label}" if year else f"{title} {type_label}"
            
            if settings.show_request_status():
                status = get_media_status(media_type, item.get('id'), jellyseer_client)
                status_label = get_status_label(status)
                if status_label:
                    full_title += f" {status_label}"
            
            context_menu = []
            context_menu.append(('Show Details', f'RunPlugin({build_url({"mode": "show_details", "type": media_type, "id": item.get("id")})})'))
            context_menu.append(('Add to Favorites', f'RunPlugin({build_url({"mode": "add_favorite", "type": media_type, "id": item.get("id")})})'))
            
            url = build_url({'mode': 'handle_search_item', 'type': media_type, 'id': item.get('id')})
            list_item = xbmcgui.ListItem(label=full_title)
            list_item.addContextMenuItems(context_menu)
            info = make_info(item, media_type)
            art = make_art(item)
            set_info_tag(list_item, info)
            list_item.setArt(art)
            xbmcplugin.addDirectoryItem(addon_handle, url, list_item, False)
        xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        add_next_page_button({"mode": "search", "query": search_string}, page, total_pages, addon_handle)
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
    else:
        xbmcplugin.setContent(addon_handle, 'files')
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        xbmc.executebuiltin('Action(Back)')
 
def handle_search_item(media_type, id, jellyseer_client):
    if media_type != "tv":
        xbmc.executebuiltin(f'RunPlugin({build_url({"mode": "request", "type": media_type, "id": id})})')
        return
    name = jellyseer_client.api_request(f"/tv/{id}").get("name")
    selected = xbmcgui.Dialog().select(name, ["Request", "Browse"])
    if selected == -1:
        return
    elif selected == 0:
        xbmc.executebuiltin(f'RunPlugin({build_url({"mode": "request", "type": media_type, "id": id})})')
        return
    xbmc.executebuiltin(f'Container.Update({build_url({"mode": "handle_search_season", "type": media_type, "id": id})})')

def handle_search_season(id, jellyseer_client, addon_handle):
    seasons = jellyseer_client.api_request(f"/tv/{id}").get("seasons")
    xbmcplugin.setContent(addon_handle, 'seasons')
    for season in seasons:
        list_item = xbmcgui.ListItem(label = season.get("name"))
        list_item.setInfo("video",  {'title': season.get("name"), "season": season.get("seasonNumber"), 'mediatype': 'season'})
        xbmcplugin.addDirectoryItem(addon_handle, build_url({"mode": "handle_search_episode", "id": id, "season": season.get("seasonNumber")}) , list_item, True)
    xbmcplugin.endOfDirectory(addon_handle)  

def handle_search_episodes(id, season, jellyseer_client, addon_handle):
    episodes = jellyseer_client.api_request(f"/tv/{id}/season/{season}").get("episodes", [])
    xbmcplugin.setContent(addon_handle, 'seasons')
    for ep in episodes:
        list_item = xbmcgui.ListItem(label=ep.get("name"))
        list_item.setInfo("video",  {'title': ep.get("name"), "episode": ep.get("episodeNumber"), "season": season,  'plot': ep.get("overview"), 'mediatype': 'episode'})
        list_item.setArt({'icon': ep.get("stillPath")})
        xbmcplugin.addDirectoryItem(addon_handle, build_url({"mode": "request", "season": season, "type": "tv", "episode": ep.get("episodeNumber"), "id": id, "go_back": True }), list_item, False)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_EPISODE)
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)    
    