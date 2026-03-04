import xbmcaddon
import xbmcvfs
import xbmc
import xbmcaddon
import time
import os
import json

addon = xbmcaddon.Addon()
cache = {}
cache_path = xbmcvfs.translatePath(f"special://profile/addon_data/{addon.getAddonInfo('id')}/cache.json")


def load_cache():
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
        save_cache()