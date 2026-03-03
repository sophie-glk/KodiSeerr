import xbmcaddon
from jellyseerr_api import JellyseerrClient
from ApiClient import ApiClient


def create_client(client=JellyseerrClient):
    """Get the API client, creating a new one if settings have changed"""
    addon = xbmcaddon.Addon()
    url = addon.getSetting(f"{client.name}_url")
    api_token = addon.getSetting(f"{client.name}_api_token")
    return client(url, api_token)


