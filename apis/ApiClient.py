import requests
import xbmcaddon
import xbmc
import xbmcgui
import json
from urllib.parse import urlencode, quote
from cache import *

class ApiClient:
    def __init__(self, endpoint_url, api_token, has4k=False, endpoint_url_4k=None, api_token_4k=None):
        self.endpoint_url = endpoint_url
        self.api_token = api_token
        self.session = None
        self.name = ""
        self.__has4k = has4k
        self.endpoint_url_4k = endpoint_url_4k
        self.api_token_4k = api_token_4k
        self.init_session()

    def init_session(self):
        """Initializes the requests session with SSL verification based on addon settings."""
        addon = xbmcaddon.Addon()
        allow_self_signed = addon.getSettingBool("allow_self_signed")

        self.session = requests.Session()
        self.session.verify = not allow_self_signed

    def has4k(self):
        return self.__has4k

    def api_request(self, endpoint, method="GET", data=None, params=None, request_4k=False, use_cache=True):
        """Sends an authenticated API request to the server."""
        if method != "GET":
            use_cache = False

        token = self.api_token_4k if request_4k else self.api_token
        base_url = self.endpoint_url_4k if request_4k else self.endpoint_url
        url = f"{base_url}{endpoint}"

        data_json = ""
        if params:
            safe_params = {k: str(v) for k, v in params.items()}
            url += '?' + urlencode(safe_params, quote_via=quote)

        if data is not None:
            data_json = json.dumps(data, separators=(',', ':'))

        cache_key = None
        if use_cache:
            cache_key = str(url + endpoint + method + data_json + token)
            cached = get_cached(cache_key)
            if cached is not None:
                return cached

        headers = {
            "Accept": "application/json",
            "X-Api-Key": token,
        }
        if method in ("POST", "PUT"):
            headers["Content-Type"] = "application/json"

        try:
            response = self.session.request(
                method=method,
                url=url,
                data=data_json.encode("utf-8") if data_json else None,
                headers=headers,
            )
            xbmc.log(f"[kodiseer] REQUEST: {method} {url} | body: {data_json} | headers: {headers}", level=xbmc.LOGERROR)
            response.raise_for_status()
        except requests.RequestException as e:
            self.__error_notification("There was an ambiguous exception that occurred while handling this request.", e)
            raise e
        except requests.ConnectionError as e:
            self.__error_notification("A Connection error occurred.", e)
            raise e
        except requests.TooManyRedirects as e:
            self.__error_notification("Too many redirects.", e)
            raise e
        except requests.Timeout as e:
            self.__error_notification("The request timed out.", e)
            raise e
        except requests.HTTPError as e:
            self.__error_notification("An API error occured.", e)
            raise e
        if not response.content:
            return {}
        try:
            result = response.json()
        except requests.JSONDecodeError as e:
            self.__error_notification("No valid json received", e)
            raise e
        if use_cache:
            set_cached(cache_key, result)
        return result
    
    def __handle_status_code(self, status_code: int) -> bool:
        pass
    def __error_notification(self, message, exception):
            xbmc.log(f"[kodiseer] {self.name} : {str(exception)}", level=xbmc.LOGERROR)
            xbmcgui.Dialog().notification(
            heading=f"[kodiseer] {self.name}",
            message=message,
            icon=xbmcgui.NOTIFICATION_ERROR,
            time=5000,
        )
    
