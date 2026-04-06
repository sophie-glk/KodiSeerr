from utils.utils import handle_empty_directory
import xbmcgui
import xbmc
def show_statistics(jellyseer_client, addon_handle):
    """Show user statistics"""
    handle_empty_directory(addon_handle)
    try:
        requests_data = jellyseer_client.api_request('/request', params={'take': 1000})
        if not requests_data:
            xbmcgui.Dialog().notification("KodiSeerr", "Failed to fetch statistics", xbmcgui.NOTIFICATION_ERROR)
            return
        
        items = requests_data.get('results', [])
        
        total = len(items)
        movies = sum(1 for i in items if i.get('media', {}).get('mediaType') == 'movie')
        tv = sum(1 for i in items if i.get('media', {}).get('mediaType') == 'tv')
        
        status_counts = {}
        for item in items:
            status = item.get('media', {}).get('status', 0)
            status_counts[status] = status_counts.get(status, 0) + 1
        
        pending = status_counts.get(2, 0)
        processing = status_counts.get(3, 0)
        available = status_counts.get(5, 0)
        
        stats = f"[B]Your Request Statistics[/B]\n\n"
        stats += f"Total Requests: {total}\n"
        stats += f"Movies: {movies}\n"
        stats += f"TV Shows: {tv}\n\n"
        stats += f"[COLOR yellow]Pending:[/COLOR] {pending}\n"
        stats += f"[COLOR cyan]Processing:[/COLOR] {processing}\n"
        stats += f"[COLOR lime]Available:[/COLOR] {available}\n"
        
        xbmcgui.Dialog().textviewer("Statistics", stats)
    except Exception as e:
        from utils.logging import log_error
        log_error(f"Statistics error: {e}")
        xbmcgui.Dialog().notification("KodiSeerr", "Failed to fetch statistics", xbmcgui.NOTIFICATION_ERROR)