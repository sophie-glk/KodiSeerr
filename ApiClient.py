import urllib.request
import urllib.error
import ssl
import xbmcaddon
import xbmc
import json
from urllib.parse import urlencode, quote
import hashlib
from cache import *

class ApiClient:
    def __init__(self, endpoint_url, api_token, has4k=False, endpoint_url_4k = None, api_token_4k=None):
        self.endpoint_url = endpoint_url
        self.api_token = api_token
        self.opener = None
        self.name = ""
        self.__has4k = has4k
        self.endpoint_url_4k = endpoint_url_4k
        self.api_token_4k = api_token_4k
        self.init_opener()

    def init_opener(self):
        """Initializes the opener with SSL context based on addon settings."""
        addon = xbmcaddon.Addon()
        allow_self_signed = addon.getSettingBool("allow_self_signed")

        if allow_self_signed:
            ssl_context = ssl._create_unverified_context()
        else:
            ssl_context = ssl.create_default_context()

        https_handler = urllib.request.HTTPSHandler(context=ssl_context)
        self.opener = urllib.request.build_opener(https_handler)
    
    def has4k(self):
        return self.__has4k

    def api_request(self, endpoint, method="GET", data=None, params=None, request_4k = False):
        """Sends an authenticated API request to the server."""
        if not request_4k:
            token = self.api_token
            url = f"{self.endpoint_url}{endpoint}"
        else:
            token = self.api_token_4k
            url = f"{self.endpoint_url}{endpoint}"
        data_json = ""
        if params:
            safe_params = {k: str(v) for k, v in params.items()}
            url += '?' + urlencode(safe_params, quote_via=quote)
        if data is not None:
            data_json = json.dumps(data, separators=(',', ':'))
            data = data_json.encode('utf-8')
        cache_key = hashlib.sha256(str(url + endpoint + method + data_json + token).encode("utf-8")).hexdigest()
        cached = get_cached(cache_key)
        if cached is not None:
            return cached
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Accept", "application/json")
        req.add_header("X-Api-Key", token)
        if method == "POST":
            req.add_header("Content-Type", "application/json")   
        try:
            with self.opener.open(req) as resp:
                response = json.loads(resp.read().decode())
                set_cached(cache_key, response)
                return response
        except urllib.error.HTTPError as e:
            error_body = e.read().decode() if e.fp else ""
            xbmc.log(f"[kodiseerr] {self.name} API request failed: {e.code} {e.reason} - {error_body}", xbmc.LOGERROR)
            return None
        except urllib.error.URLError as e:
            xbmc.log(f"[kodiseerr] {self.name} API request failed: {e.reason}", xbmc.LOGERROR)
            return None
