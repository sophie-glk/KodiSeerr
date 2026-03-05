from ApiClient import ApiClient

class JellyseerrClient(ApiClient):
    name = "jellyseerr"
    def __init__(self, server_url,  api_token, server_url_4k=None, api_token_4k=None):
       super().__init__(f"{server_url}/api/v1", api_token)