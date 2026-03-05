from ApiClient import ApiClient

class SonarrClient(ApiClient):
    name = "sonarr"
    def __init__(self, server_url,  api_token, server_url_4k=None, api_token_4k=None):
       if server_url_4k is not None:
           server_url_4k = f"{server_url_4k}/api/v3"
       super().__init__(f"{server_url}/api/v3", api_token, server_url_4k, api_token_4k)