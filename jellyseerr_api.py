import urllib.request
import urllib.error
import http.cookiejar
import ssl
from ApiClient import ApiClient
import xbmcaddon
import xbmc
import json
from urllib.parse import urlencode, quote

class JellyseerrClient(ApiClient):
    name = "jellyseerr"
    def __init__(self, server_url,  api_token):
       super().__init__(f"{server_url}/api/v1", api_token)