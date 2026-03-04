import xbmcaddon
import xbmcvfs
import xbmc
import xbmcgui
import xbmcaddon
import time
import os
import json

addon = xbmcaddon.Addon()
cache = {}
cache_path = xbmcvfs.translatePath(f"special://profile/addon_data/{addon.getAddonInfo('id')}/cache.json")


def load_cache():
    global cache
    window = xbmcgui.Window(10000)
    cache_string = window.getProperty("seerr_cache")
    if cache_string != "" and cache_string is not None:
     try:
      cache = json.loads(window.getProperty("seerr_cache"))
     except:
        return
     
def load_cache_disk():
    global cache
    if addon.getSettingBool('enable_caching'):
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    cache = json.load(f)
        except Exception as e:
            xbmc.log(f"[KodiSeerr] Cache load error: {e}", xbmc.LOGERROR)
            cache = {}

def save_cache():
    if addon.getSettingBool('enable_caching'):
        window = xbmcgui.Window(10000) # Home
        window.setProperty("seerr_cache",  json.dumps(cache))

def save_cache_disk():
    if addon.getSettingBool('enable_caching'):
        try:
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            with open(cache_path, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            xbmc.log(f"[KodiSeerr] Cache save error: {e}", xbmc.LOGERROR)

def get_cached(key):
    if not addon.getSettingBool('enable_caching'):
        return None
    if key in cache:
        entry = cache[key]
        if time.time() - entry.get('timestamp', 0) < entry.get("duration", 60):
            return entry.get('data')
    return None

def set_cached(key, data,  duration=None):
    if not duration:
        duration = addon.getSettingInt('cache_duration') * 60
    if addon.getSettingBool('enable_caching'):
        cache[key] = {'data': data, 'timestamp': time.time(), "duration": duration}

def clear_cache():
    """Clear all cached data"""
    global cache
    try:
        if os.path.exists(cache_path):
            os.remove(cache_path)
        cache = {}
        xbmcgui.Dialog().notification('KodiSeerr', 'Cache cleared successfully', xbmcgui.NOTIFICATION_INFO, 3000)
    except Exception as e:
        xbmc.log(f"[KodiSeerr] Clear cache error: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('KodiSeerr', 'Failed to clear cache', xbmcgui.NOTIFICATION_ERROR)

def clean_cache():
    current_time = time.time()
    for id, item in cache.items():
        if current_time - item.get("timestamp", 0) > item.get("duration", 60):
            del cache[id]
    save_cache()