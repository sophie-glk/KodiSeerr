from utils import build_url, get_media_status
import xbmc
import xbmcgui
import xbmcvfs
import xbmcplugin
import os
import json
def do_request(media_type, id, season, enable_ask_4k, jellyseer_client, addon):
    """Handle media request with advanced options"""
    # Check if already requested/available
    status = get_media_status(media_type, id, jellyseer_client)
    if status in [2, 3, 4] or status >= 5:
        if not xbmcgui.Dialog().yesno('KodiSeerr', 'This content is already requested. Request again?'):
            return
    seasons_to_request = []
    tv_request_types = ["Request this season", "Request all seasons"]
    if media_type == "tv":    
     selected_tv_request_type = xbmcgui.Dialog().select("Seerr Request", tv_request_types)
     if selected_tv_request_type < 0:
         return
     elif selected_tv_request_type == 0:
         if season:
             seasons_to_request = [int(season)]
     else:
         seasons_to_request = "all"
    
    is4k = False
    quality_profile = None
    if enable_ask_4k:
        preferences_path = xbmcvfs.translatePath(f"special://profile/addon_data/{addon.getAddonInfo('id')}/preferences.json")
        prefs = load_preferences(preferences_path)
        if addon.getSettingBool('remember_last_quality') and 'last_4k_choice' in prefs:
            is4k = prefs['last_4k_choice']
        else:
            is4k = xbmcgui.Dialog().yesno('KodiSeerr', 'Request in 4K quality?')

        if addon.getSettingBool('remember_last_quality'):
            prefs['last_4k_choice'] = is4k
            save_preferences(prefs, preferences_path)
    
    if addon.getSettingBool('show_quality_profiles'):
        profiles = get_quality_profiles(jellyseer_client)
        if profiles:
            profile_names = [p[1] for p in profiles]
            selected = xbmcgui.Dialog().select('Select Quality Profile', profile_names)
            if selected >= 0:
                quality_profile = profiles[selected][0]

    if addon.getSettingBool('confirm_before_request'):
        title_data = jellyseer_client.api_request(f"/{media_type}/{id}")
        title = title_data.get('title') or title_data.get('name', 'this content') if title_data else 'this content'
        msg = f"Request {title}"
        if is4k:
            msg += " in 4K"
        msg += "?"
        if not xbmcgui.Dialog().yesno('KodiSeerr', msg):
            return
    
    payload = {
        "mediaType": media_type,
        "mediaId": int(id),
        "is4k": is4k
    }
    
    if media_type == "tv":
        payload["seasons"] = seasons_to_request

    if quality_profile:
        payload["profileId"] = quality_profile
    
    try:
        jellyseer_client.api_request("/request", method="POST", data=payload)
        xbmcgui.Dialog().notification('KodiSeerr', 'Request Sent!', xbmcgui.NOTIFICATION_INFO, 3000)
    except Exception as e:
        xbmcgui.Dialog().notification('KodiSeerr', f'Request Failed: {str(e)}', xbmcgui.NOTIFICATION_ERROR, 4000)

def do_request_as_player(media_type, season_arg, id, addon_handle):
    #immediately tell kodi that we are done with playback, this prevents time outs
    item = xbmcgui.ListItem()
    item.setProperty('IsPlayable', 'true')
    item.setMimeType('audio/mpeg')
    xbmcplugin.setResolvedUrl(addon_handle, False, item)
    season = "all"
    if season_arg != None:
        season = season_arg
    url = build_url({'mode': 'request', 'type': media_type, 'id': id, "season": season})
    xbmc.executebuiltin(f'RunPlugin({url})')

def get_quality_profiles(jellyseer_client):
    """Get available quality profiles from server"""
    try:
        # This depends on Jellyseerr API - might need adjustment
        data = jellyseer_client.api_request('/settings/radarr')
        if data and isinstance(data, list) and len(data) > 0:
            profiles = data[0].get('profiles', [])
            return [(p['id'], p['name']) for p in profiles]
    except Exception as e:
        xbmc.log(f"[KodiSeerr] Quality profiles error: {e}", xbmc.LOGERROR)
    return []

def load_preferences(preferences_path):
    try:
        if os.path.exists(preferences_path):
            with open(preferences_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        xbmc.log(f"[KodiSeerr] Preferences load error: {e}", xbmc.LOGERROR)
    return {}

def save_preferences(prefs, preferences_path):
    try:
        os.makedirs(os.path.dirname(preferences_path), exist_ok=True)
        with open(preferences_path, 'w') as f:
            json.dump(prefs, f)
    except Exception as e:
        xbmc.log(f"[KodiSeerr] Preferences save error: {e}", xbmc.LOGERROR)