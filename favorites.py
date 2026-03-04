from utils import build_url, make_art, make_info, set_info_tag
import xbmcgui
import xbmcplugin
import xbmc
import json
import os

def add_to_favorites(media_type, media_id, favorites_path):
    """Add item to favorites"""
    favorites = load_favorites(favorites_path)
    fav_key = f"{media_type}_{media_id}"
    if fav_key in favorites:
        xbmcgui.Dialog().notification('KodiSeerr', 'Already in favorites', xbmcgui.NOTIFICATION_INFO)
    else:
        favorites.add(fav_key)
        save_favorites(favorites, favorites_path)
        xbmcgui.Dialog().notification('KodiSeerr', 'Added to favorites', xbmcgui.NOTIFICATION_INFO)

def remove_from_favorites(media_type, media_id, favorites_path):
    """Remove item from favorites"""
    favorites = load_favorites(favorites_path)
    fav_key = f"{media_type}_{media_id}"
    if fav_key in favorites:
        favorites.remove(fav_key)
        save_favorites(favorites, favorites_path)
        xbmcgui.Dialog().notification('KodiSeerr', 'Removed from favorites', xbmcgui.NOTIFICATION_INFO)
        xbmc.executebuiltin('Container.Refresh')

def list_favorites(favorites_path, jellyseer_client, addon_handle):
    """List user's favorite items"""
    xbmcplugin.setContent(addon_handle, 'videos')
    favorites = load_favorites(favorites_path)
    
    if not favorites:
        info_item = xbmcgui.ListItem(label='[I]No favorites yet[/I]')
        xbmcplugin.addDirectoryItem(addon_handle, '', info_item, False)
    else:
        for fav in favorites:
            parts = fav.split('_')
            if len(parts) >= 2:
                media_type = parts[0]
                media_id = parts[1]
                
                data = jellyseer_client.api_request(f"/{media_type}/{media_id}")
                if data:
                    title = data.get('title') or data.get('name', 'Unknown')
                    label = title
                    
                    context_menu = []
                    context_menu.append(('Remove from Favorites', f'RunPlugin({build_url({"mode": "remove_favorite", "type": media_type, "id": media_id})})'))
                    context_menu.append(('Show Details', f'RunPlugin({build_url({"mode": "show_details", "type": media_type, "id": media_id})})'))
                    
                    url = build_url({'mode': 'request', 'type': media_type, 'id': media_id})
                    list_item = xbmcgui.ListItem(label=label)
                    list_item.addContextMenuItems(context_menu)
                    info = make_info(data, media_type)
                    art = make_art(data)
                    set_info_tag(list_item, info)
                    list_item.setArt(art)
                    xbmcplugin.addDirectoryItem(addon_handle, url, list_item, False)
    
    xbmcplugin.endOfDirectory(addon_handle)

def load_favorites(favorites_path):
    try:
        if os.path.exists(favorites_path):
            with open(favorites_path, 'r') as f:
                return set(json.load(f))
    except Exception as e:
        xbmc.log(f"[KodiSeerr] Favorites load error: {e}", xbmc.LOGERROR)
    return set()

def save_favorites(favorites, favorites_path):
    try:
        os.makedirs(os.path.dirname(favorites_path), exist_ok=True)
        with open(favorites_path, 'w') as f:
            json.dump(list(favorites), f)
    except Exception as e:
        xbmc.log(f"[KodiSeerr] Favorites save error: {e}", xbmc.LOGERROR)