import xbmcaddon
from jellyseerr_api import JellyseerrClient
from ApiClient import ApiClient


def create_client(client=JellyseerrClient):
    """Get the API client, creating a new one if settings have changed"""
    addon = xbmcaddon.Addon()
    url = addon.getSetting(f"{client.name}_url")
    url_4k = None
    api_token = addon.getSetting(f"{client.name}_api_token")
    api_token_4k = None
    has_4k = False
    try:
     has_4k = addon.getSettingBool(f"{client.name}_has_4k")
    except:
     has_4k = False
    if has_4k:
     url_4k = addon.getSetting(f"{client.name}_url_4k")
     api_token_4k = addon.getSetting(f"{client.name}_api_token_4k")

    return client(url, api_token, url_4k, api_token_4k)


