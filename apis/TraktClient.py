import hashlib

from cache import get_cached, set_cached
import xbmc
import xbmcgui
import time
import requests
import json


class TraktClient:
    BASE_URL = "https://api.trakt.tv"
    def __init__(self, client_id: str, client_secret: str, addon_data_path: str):
        self.addon_data_path = addon_data_path
        self.ID = "24aabe81-9074-4813-81bb-31dbec750d7d"
        self.client_id = client_id
        self.client_secret = client_secret
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

    def api_request(self, method: str, endpoint: str, use_cache: bool = True):
        if method != "GET":
            use_cache = False
        cache_key = None
        if use_cache:
         cache_key = str(self.BASE_URL + endpoint + method + self.access_token + self.refresh_token)
         cached = get_cached(cache_key)
         if cached is not None:
            return cached
        if not self.access_token:
            xbmcgui.Dialog().notification("KodiSeerr", "Trakt not authorized", xbmcgui.NOTIFICATION_ERROR)
            return None
        authed_headers = {**self.headers, "Authorization": f"Bearer {self.access_token}"}
        response = requests.request(
            method, f"{self.BASE_URL}{endpoint}", headers=authed_headers
        )
        response.raise_for_status()
        data = response.json()
        if use_cache:
            set_cached(cache_key, data)
        return data
