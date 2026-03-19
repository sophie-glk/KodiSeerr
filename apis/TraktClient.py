from cache import get_cached, set_cached
import xbmc
import xbmcgui
import time
import requests
import json
import time

class TraktClient:
    BASE_URL = "https://api.trakt.tv"
    def __init__(self, client_id: str, client_secret: str, addon_data_path: str):
        self.addon_data_path = addon_data_path
        self.ID = "24aabe81-9074-4813-81bb-31dbec750d7d"
        self.client_id = client_id
        self.client_secret = client_secret

        window = xbmcgui.Window(10000)
        rate_limit_string = window.getProperty(self.ID+"rate_limits")
        self.rate_limit = {"start": 0, "length": -1}
        if rate_limit_string != "" and rate_limit_string is not None:
            try:
                self.rate_limit = json.loads(rate_limit_string)
            except:
                pass
        self.headers = {
            "Content-Type": "application/json",
            "trakt-api-version": "2",
            "trakt-api-key": self.client_id,
        }
        if not self.load_tokens():
            self.login()

    # --- Auth ---

    def request_device_code(self) -> dict:
        response = requests.post(
            f"{self.BASE_URL}/oauth/device/code",
            headers=self.headers,
            json={"client_id": self.client_id},
        )
        response.raise_for_status()
        return response.json()

    def refresh_access_token(self) -> None:
        response = requests.post(
            f"{self.BASE_URL}/oauth/token",
            headers=self.headers,
            json={
                "refresh_token": self.refresh_token,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
            },
        )
        response.raise_for_status()
        data = response.json()
        self.access_token = data["access_token"]
        self.refresh_token = data["refresh_token"]
        self.save_tokens()

    def login(self) -> bool:
        device = self.request_device_code()

        dialog = xbmcgui.DialogProgress()
        dialog.create(
            "Trakt Login",
            f"Visit: {device['verification_url']} \n Enter code: [B]{device['user_code']}[/B]"
        )

        expires_in = device["expires_in"]
        interval = device["interval"]
        start_time = time.time()
        deadline = start_time + expires_in
       
        while time.time() < deadline:
            elapsed = time.time() - start_time
            percent = int((elapsed / expires_in) * 100)
            dialog.update(percent)

            if dialog.iscanceled():
                dialog.close()
                return False

            xbmc.sleep(interval * 1000) 

            response = requests.post(
                f"{self.BASE_URL}/oauth/device/token",
                headers=self.headers,
                json={
                    "code": device["device_code"],
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                dialog.close()
                xbmcgui.Dialog().ok("Trakt Login", "Successfully logged in!")
                self.save_tokens()
                return True
            elif response.status_code == 400:
                pass  # Still waiting
            elif response.status_code == 418:
                dialog.close()
                return True
            elif response.status_code == 429:
                interval += 1

        dialog.close()
        xbmcgui.Dialog().ok("Trakt Login", "Login timed out. Please try again.")



    def save_tokens(self, filename: str = "tokens.json") -> None:
        data = {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
        }
        window = xbmcgui.Window(10000)
        window.setProperty(self.ID,  json.dumps(data, separators=(',', ':')))
        path = f"{self.addon_data_path}/{filename}"
        with open(path, "w") as f:
            json.dump(data, f)

    def load_tokens(self, filename: str = "tokens.json") -> bool:
        window = xbmcgui.Window(10000)
        cached_tokens = window.getProperty(self.ID)
        if cached_tokens != "" and cached_tokens is not None:
            try:
                data = json.loads(cached_tokens)
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                return True
            except:
              pass
        
        path = f"{self.addon_data_path}/{filename}"
        try:
            with open(path) as f:
                data = json.load(f)
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                return True
        except FileNotFoundError:
            return False
    
    def paginated_request(self, method: str, endpoint:str, use_cache:bool = True):
        data, headers = self.__api_request(method, endpoint, use_cache=use_cache)
        total_number_of_pages = int(headers.get("X-Pagination-Limit"))
        return data, total_number_of_pages

    def api_request(self, method: str, endpoint: str, use_cache: bool = True):
        data, headers = self.__api_request(method, endpoint, use_cache=use_cache)
        return data
    
    def __api_request(self, method: str, endpoint: str, use_cache: bool = True):
        #check if we have run into a rate limit:
        if time.time() - self.rate_limit.get("start", 0) <= self.rate_limit.get("length", -1):
            xbmcgui.Dialog().notification(
            heading="Trakt Error",
            message="API Rate Limit Exceeded - please try again later",
            icon=xbmcgui.NOTIFICATION_ERROR,
            time=5000,
            )
            return {},{}
        else:
            self.rate_limit = {"start": 0, "length": -1}

        if method != "GET":
            use_cache = False
        cache_key = None

        if use_cache:
         cache_key = str(self.BASE_URL + endpoint + method + self.access_token + self.refresh_token)
         cached = get_cached(cache_key)
         if cached is not None:
                return cached.get("data"), cached.get("header")
            
        if not self.access_token:
            xbmcgui.Dialog().notification("KodiSeerr", "Trakt not authorized", xbmcgui.NOTIFICATION_ERROR)
            return {}
        authed_headers = {**self.headers, "Authorization": f"Bearer {self.access_token}"}
        try:
            response = requests.request(
            method, f"{self.BASE_URL}{endpoint}", headers=authed_headers
        )
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

        headers = response.headers
        status_code = response.status_code
        
        if not self.__handle_status_code(status_code, headers):
            xbmc.sleep(1000)
            raise requests.HTTPError
        try:
            data = response.json()
        except requests.JSONDecodeError as e:
            self.__error_notification("No valid json received", e)
            raise e

        if use_cache:
            set_cached(cache_key, {"data": data, "header": headers})
        return data, response.headers

    def __handle_status_code(self, status_code: int, headers) -> bool:
        if status_code in (200, 201, 204):
            return True
        
        if status_code == 429:
                self.rate_limit = {"start": time.time(), "length": int(headers.get("Retry-After", 30))}
                window = xbmcgui.Window(10000)
                window.setProperty(self.ID+"rate_limits", json.dumps(self.rate_limit))

        error_messages = {
            400: "Bad Request - request couldn't be parsed",
            401: "Unauthorized - please log in again",
            403: "Forbidden - invalid API key or unapproved app",
            404: "Not Found - no record found",
            405: "Method Not Found",
            409: "Conflict - resource already exists",
            412: "Precondition Failed - invalid content type",
            420: "Account Limit Exceeded - list or item count limit reached",
            422: "Unprocessable Entity - validation error",
            423: "Locked User Account - please contact Trakt support",
            426: "VIP Only - upgrade your Trakt account",
            429: "API Rate Limit Exceeded - please try again later",
            500: "Trakt Server Error - please try again later",
            502: "Trakt Unavailable - server overloaded, try again in 30s",
            503: "Trakt Unavailable - server overloaded, try again in 30s",
            504: "Trakt Unavailable - server overloaded, try again in 30s",
            520: "Trakt Unavailable - Cloudflare error",
            521: "Trakt Unavailable - Cloudflare error",
            522: "Trakt Unavailable - Cloudflare error",
        }

        message = error_messages.get(status_code, f"Unexpected error (HTTP {status_code})")
        self.__error_notification(message)

        return False
    
    def __error_notification(self, message, exception):
            xbmc.log(f"[kodiseer] Trakt: {str(exception)}", level=xbmc.LOGERROR)
            xbmcgui.Dialog().notification(
            heading="Trakt Error",
            message=message,
            icon=xbmcgui.NOTIFICATION_ERROR,
            time=5000,
        )
