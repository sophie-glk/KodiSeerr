from apis.jellyseerr_api import JellyseerrClient
import xbmcaddon
def create_seerr_client():
    name = "seerr"
    addon = xbmcaddon.Addon()
    auth_method_id = addon.getSetting(f'{name}_auth_method')
    auth_method = ""
    auth_data = {}
    if auth_method_id == "API-Key": #API_KEY
        auth_method = "api_token"
        auth_data = {"api_token": addon.getSetting(f"{name}_api_token")}
    elif auth_method_id == "Plex": #Plex
        auth_method = "plex"
        auth_data = {"authToken": addon.getSetting(f"{name}_plex_token")}
    elif auth_method_id == "Jellyfin": #Jellyfin
        auth_method = "jellyfin"
        auth_data = {"username": addon.getSetting(f"{name}_jellyfin_username"), "password": addon.getSetting(f"{name}_jellyfin_password")}
    elif auth_method_id == "Seerr": ##local
        auth_method = "local"
        auth_data = {"email": addon.getSetting(f"{name}_local_email"), "password": addon.getSetting(f"{name}_local_password")}
    url = addon.getSetting(f"{name}_url")
    allow_self_signed = addon.getSetting("allow_self_signed")

    return JellyseerrClient(server_url=url, auth_method=auth_method, auth_data=auth_data, allow_self_signed=allow_self_signed)

