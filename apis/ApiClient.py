import requests
from utils.logging import log_error
import xbmcaddon
import xbmc
import xbmcgui
import json
from urllib.parse import urlencode, quote
from cache import *

class ApiClient:
    def __init__(self, endpoint_url, api_token = None, has4k=False, endpoint_url_4k=None, api_token_4k=None, allow_self_signed = False, name = ""):

        self.allow_self_signed = allow_self_signed
        self._disable_error_messages = False
        self.endpoint_url = endpoint_url
        self.api_token = api_token
        self.session = None
        self.name = name
        self.__has4k = has4k
        self.endpoint_url_4k = endpoint_url_4k
        self.api_token_4k = api_token_4k
        self.init_session()
     
    def init_session(self):
        self.session = requests.Session()
        self.session.verify = not self.allow_self_signed

    def has4k(self):
        return self.__has4k
    
    def disable_error_messages(self):
        self._disable_error_messages = True
    
    def enable_error_messages(self):
        self._disable_error_messages = False

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
            cache_key = str(url + method + data_json + self.name)
            cached = get_cached(cache_key)
            if cached is not None:
                return cached
        if token:
            headers = {
            "Accept": "application/json",
            "X-Api-Key": token,
            }
        else:
            headers = {
            "Accept": "application/json"
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
        except requests.ConnectionError as e:
            self._error_notification("A Connection error occurred.", e)
            raise e
        except requests.TooManyRedirects as e:
            self._error_notification("Too many redirects.", e)
            raise e
        except requests.Timeout as e:
            self._error_notification("The request timed out.", e)
            raise e
        if not self._handle_status_code(response.status_code):
            raise requests.HTTPError
        
        if not response.content:
            return {}
        try:
            result = response.json()
        except requests.JSONDecodeError as e:
            self._error_notification("No valid json received", e)
            raise e
        if use_cache:
            set_cached(cache_key, result)
        return result
    
    def _handle_status_code(self, status_code: int) -> bool:
        if status_code in [200, 201, 202, 204]:
            return True
        self._error_notification("An API error occured.", f"Error code: {status_code}")
        return False
    
    def _error_notification(self, message, exception =  requests.HTTPError):
            from utils.logging import log_error, notify_error
            log_error( f"{self.name} : {str(exception)}")
            log_error(f"{self.name} : {message}")
            if self._disable_error_messages:
                return
            notify_error(heading=self.name, message=message)
    
