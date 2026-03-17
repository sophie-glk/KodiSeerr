import xbmcgui
import xbmc
def test_connection(addon):
    """Test connection to Jellyseerr server"""
    try:
        from apis.jellyseerr_api import JellyseerrClient
        
        test_url = addon.getSetting("jellyseerr_url").rstrip("/")
        test_username = addon.getSetting("jellyseerr_username")
        test_password = addon.getSetting("jellyseerr_password")
        test_api_token = addon.getSetting("jellyseerr_api_token")
        test_auth_method = addon.getSetting("auth_method")
        
        if not test_auth_method:
            test_auth_method = "password"
        
        test_client = JellyseerrClient(test_url, test_username, test_password, test_api_token, test_auth_method)
        
        if test_client.login():
            xbmcgui.Dialog().notification('KodiSeerr', 'Connection successful!', xbmcgui.NOTIFICATION_INFO, 3000)
        else:
            xbmcgui.Dialog().notification('KodiSeerr', 'Connection failed. Check settings.', xbmcgui.NOTIFICATION_ERROR, 5000)
    except Exception as e:
        xbmc.log(f"[KodiSeerr] Test connection error: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('KodiSeerr', f'Error: {str(e)}', xbmcgui.NOTIFICATION_ERROR, 5000)
    xbmc.executebuiltin("Action(Back)")