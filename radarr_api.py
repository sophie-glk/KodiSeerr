import urllib.request
import urllib.error
import http.cookiejar
import ssl
import xbmcaddon
import xbmc
import json
from urllib.parse import urlencode, quote

class RadarrClient:
    def __init__(self, base_url, api_token):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.opener = None
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

    def api_request(self, endpoint, method="GET", data=None, params=None):
        """Sends an authenticated API request to the server."""

        url = f"{self.base_url}/api/v1{endpoint}"
        if params:
            safe_params = {k: str(v) for k, v in params.items()}
            url += '?' + urlencode(safe_params, quote_via=quote)

        if data is not None:
            data = json.dumps(data).encode('utf-8')

        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Accept", "application/json")
        req.add_header("X-Api-Key", self.api_token)
        if method == "POST":
            req.add_header("Content-Type", "application/json")

        try:
            with self.opener.open(req) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            # If we get 401, try to login again once
            if e.code == 401 and self.logged_in:
                xbmc.log(f"[kodiseerr] Got 401, retrying login", xbmc.LOGDEBUG)
                self.logged_in = False
                if self.login():
                    # Retry the request
                    try:
                        req = urllib.request.Request(url, data=data, method=method)
                        req.add_header("Accept", "application/json")
                        req.add_header("X-Api-Key", self.api_token)
                        if method == "POST":
                            req.add_header("Content-Type", "application/json")
                        with self.opener.open(req) as resp:
                            return json.loads(resp.read().decode())
                    except Exception as retry_e:
                        xbmc.log(f"[kodiseerr] Retry failed: {retry_e}", xbmc.LOGERROR)
                        return None
            error_body = e.read().decode() if e.fp else ""
            xbmc.log(f"[kodiseerr] API request failed: {e.code} {e.reason} - {error_body}", xbmc.LOGERROR)
            return None
        except urllib.error.URLError as e:
            xbmc.log(f"[kodiseerr] API request failed: {e.reason}", xbmc.LOGERROR)
            return None
