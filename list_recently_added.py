from utils import build_url, make_art, make_info, set_info_tag
import xbmcplugin
import xbmcgui
def list_recently_added(page, jellyseer_client, addon_handle):
    """Show recently added content to the server"""
    xbmcplugin.setContent(addon_handle, 'videos')
    
    recent_movies = jellyseer_client.api_request("/discover/movies", params={"sortBy": "mediaAdded", "page": page})
    recent_tv = jellyseer_client.api_request("/discover/tv", params={"sortBy": "mediaAdded", "page": page})
    
    all_items = []
    if recent_movies:
        all_items.extend(recent_movies.get('results', []))
    if recent_tv:
        all_items.extend(recent_tv.get('results', []))
    
    for item in all_items[:20]:
        media_type = item.get('mediaType')
        title = item.get('title') or item.get('name')
        release_date = item.get('releaseDate') or item.get('firstAirDate')
        year = int(release_date.split("-")[0]) if release_date and release_date.split("-")[0].isdigit() else None
        label = f"{title} ({year})" if year else title
        
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