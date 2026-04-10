import json

import requests

from apis.ApiClient import ApiClient
from cache import get_cached, set_cached
from utils.logging import log_error

class JellyseerrClient(ApiClient):
    name = "jellyseerr"
    def __init__(self, server_url, auth_method = "api_token", allow_self_signed = False, auth_data = {}):
       self.name = "seerr"
       self.auth_method = auth_method
       self.auth_data = auth_data
       super().__init__(f"{server_url}/api/v1", api_token = auth_data.get("api_token"),  allow_self_signed=allow_self_signed)
    
    def init_session(self):
        super().init_session()
        if self.auth_method != "api_token":
            self.load_cookies()

    def load_cookies(self):
        cc =  get_cached(self.name + "session_cookie")
        if cc:
            try:
                cookies = requests.utils.cookiejar_from_dict(json.loads(cc))
                self.session.cookies.update(cookies)
            except Exception as e:
                self._error_notification("Could not load cookies for Seerr from cache")
        else:
            self.login()

    def login(self):
        auth_endpoint = f"{self.endpoint_url}/auth/{self.auth_method}"
        try:
            response = self.session.request(
                method="POST",
                url=auth_endpoint,
                json=self.auth_data,
                headers = {
                "Accept": "application/json"
                }
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
        if not self._handle_status_code(response.status_code):
            raise requests.HTTPError
        set_cached(self.name + "session_cookie", json.dumps(requests.utils.dict_from_cookiejar(self.session.cookies)))

    def _handle_status_code(self, status_code):
        if status_code in [200, 201, 202, 204]:
            return True
        
        error_messages = {
            400: "Bad Request - request couldn't be parsed",
            401: "Unauthorized - No valid Api Key?",
            403: "Forbidden - Insufficient permissions",
            404: "Not Found - no record found",
            409: "Conflict - Duplicate Request?",
            500: "Internal Server Error - This is most likely due to a logic bug in this addon"
        }

        message = error_messages.get(status_code, f"Unexpected error (HTTP {status_code})")
        self._error_notification(message)
        return False