from apis.create_seerr_client import create_seerr_client
import xbmcaddon
addon = xbmcaddon.Addon()
def trakt_login(addon_data_path):
    from apis.TraktClient import TraktClient
    TraktClient(addon_data_path, reauth=True)

def populate_sonarr_settings(jellyseerr_client):
    try:
        instances = jellyseerr_client.api_request("/settings/sonarr")
    except:
        from utils.logging import notify_error
        notify_error("Sonarr instance could not be found inside Seerr response")
        return
    for instance in instances:
        is_default = instance.get("isDefault")
        api_key = instance.get("apiKey", "")
        hostname = instance.get("hostname", "")
        port = instance.get("port", "")
        proto = "https://" if instance.get("useSsl", False) else "http://"
        if is_default and instance.get("is4k"):
            addon.setSettingBool("sonarr_enable", True)
            addon.setSettingString("sonarr_url_4k", f"{proto}{hostname}:{port}")
            addon.setSettingString("sonarr_api_token_4k", api_key)
            addon.setSettingBool("sonarr_has_4k", True)
        elif is_default and not instance.get("is4k"):
            addon.setSettingBool("sonarr_enable", True)
            addon.setSettingString("sonarr_url", f"{proto}{hostname}:{port}")
            addon.setSettingString("sonarr_api_token", api_key)


def populate_radarr_settings(jellyseerr_client):
    try:
        instances = jellyseerr_client.api_request("/settings/radarr")
    except:
        from utils.logging import log_error
        log_error("Radarr instance could not be found inside Seerr response")
        return
    for instance in instances:
        is_default = instance.get("isDefault")
        api_key = instance.get("apiKey", "")
        hostname = instance.get("hostname", "")
        port = instance.get("port", "")
        proto = "https://" if instance.get("useSsl", False) else "http://"
        if is_default and instance.get("is4k"):
            addon.setSeettingBool("radarr_enable", True)
            addon.setSettingString("radarr_url_4k", f"{proto}{hostname}:{port}")
            addon.setSettingString("radarr_api_token_4k", api_key)
            addon.setSettingBool("radarr_has_4k", True)
        elif is_default and not instance.get("is4k"):
            addon.setSettingBool("radarr_enable", True)
            addon.setSettingString("radarr_url", f"{proto}{hostname}:{port}")
            addon.setSettingString("radarr_api_token", api_key)


if __name__ == '__main__':
    import sys
    import xbmcvfs
    from utils.get_addon_id import get_addon_id
    addon_data_path = xbmcvfs.translatePath(f"special://profile/addon_data/{addon.getAddonInfo('id')}")
    mode = sys.argv[1]
    if mode == "trakt_login":
        trakt_login(addon_data_path)
    elif mode == "clear_cache":
        import cache
        cache.clear_cache()
    elif mode == "populate_sonarr_settings":
        jellyseerr_client = create_seerr_client()
        populate_sonarr_settings(jellyseerr_client)
    elif mode == "populate_radarr_settings":
        jellyseerr_client = create_seerr_client()
        populate_radarr_settings(jellyseerr_client)



