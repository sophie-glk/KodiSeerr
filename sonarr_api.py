from ApiClient import ApiClient

class SonarrClient(ApiClient):
    name = "sonarr"
    def __init__(self, server_url,  api_token):
       super().__init__(f"{server_url}/api/v3", api_token)