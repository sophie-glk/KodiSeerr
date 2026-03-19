import xbmcplugin
import xbmcgui
from utils.url_handling import build_url
from utils.utils import make_art
from utils.utils import make_art
from utils.utils import set_info_tag
from utils.utils import get_media_status
from utils.utils import get_status_label
from utils.utils import make_info

def list_collections(page, jellyseer_client, image_base, addon_handle):
    """List movie collections"""
    xbmcplugin.setContent(addon_handle, 'sets')
    try:
        page = int(page)
    except:
        page = 1
    
    data = jellyseer_client.api_request("/discover/movies", params={"page": page, "sortBy": "popularity.desc"})
    
    if data:
        items = data.get('results', [])
        collections_seen = set()
        
        for item in items:
            if item.get('belongsToCollection'):
                coll = item['belongsToCollection']
                coll_id = coll.get('id')
                if coll_id not in collections_seen:
                    collections_seen.add(coll_id)
                    name = coll.get('name', 'Unknown Collection')
                    url = build_url({'mode': 'collection_details', 'collection_id': coll_id})
                    list_item = xbmcgui.ListItem(label=name)
                    if coll.get('posterPath'):
                        list_item.setArt({'poster': image_base + coll['posterPath'], 'thumb': image_base + coll['posterPath']})
                    xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)
    
    xbmcplugin.endOfDirectory(addon_handle)

def show_collection_details(collection_id, settings, jellyseer_client, addon_handle):
    """Show movies in a collection"""
    xbmcplugin.setContent(addon_handle, 'movies')
    data = jellyseer_client.api_request(f"/collection/{collection_id}")
    
    if data:
        parts = data.get('parts', [])
        for item in parts:
            media_type = 'movie'
            title = item.get('title') or item.get('name')
            release_date = item.get('releaseDate')
            year = int(release_date.split("-")[0]) if release_date and release_date.split("-")[0].isdigit() else None
            
            label = f"{title} ({year})" if year else title
            
            if settings.show_request_status():
                status = get_media_status(media_type, item.get('id'), jellyseer_client)
                status_label = get_status_label(status)
                if status_label:
                    label += f" {status_label}"
            
            id = item.get('id')
            
            context_menu = []
            context_menu.append(('Show Details', f'RunPlugin({build_url({"mode": "show_details", "type": media_type, "id": id})})'))
            context_menu.append(('Add to Favorites', f'RunPlugin({build_url({"mode": "add_favorite", "type": media_type, "id": id})})'))
            
            url = build_url({'mode': 'request', 'type': media_type, 'id': id})
            list_item = xbmcgui.ListItem(label=label)
            list_item.addContextMenuItems(context_menu)
            info = make_info(item, media_type)
            art = make_art(item)
            set_info_tag(list_item, info)
            list_item.setArt(art)
            xbmcplugin.addDirectoryItem(addon_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(addon_handle)