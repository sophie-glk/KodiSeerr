import xbmcplugin
import xbmcgui
from utils import add_next_page_button, get_status_label, handle_empty_directory, make_art
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
            
            url = build_url({'mode': 'browse_menu', 'type': media_type, 'id': item.get('id')})
            list_item = xbmcgui.ListItem(label=full_title)
            list_item.addContextMenuItems(context_menu)
            info = make_info(item, media_type)
            art = make_art(item)
            set_info_tag(list_item, info)
            list_item.setArt(art)
            isFolder = False
            if media_type != "movie":
                isFolder = True
            xbmcplugin.addDirectoryItem(addon_handle, url, list_item, isFolder)
        xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
        add_next_page_button({"mode": "search", "query": search_string}, page, total_pages, addon_handle)
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
    else:
        handle_empty_directory(addon_handle)
 
