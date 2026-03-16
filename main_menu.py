
import xbmcplugin
import xbmcgui
from utils import build_url
def main_menu(addon_handle):
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
        ('trakt', 'Trakt', 'DefaultAddonService.png', True),
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