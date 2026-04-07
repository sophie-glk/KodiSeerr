from apis.ApiClient import ApiClient

class RadarrClient(ApiClient):
    name = "radarr"
    def __init__(self, server_url,  api_token, has_4k=False, server_url_4k=None, api_token_4k=None, allow_self_signed = False):
       if server_url_4k is not None:
           server_url_4k = f"{server_url_4k}/api/v3"
       super().__init__(f"{server_url}/api/v3", api_token, has_4k, server_url_4k, api_token_4k, allow_self_signed)

    def _handle_status_code(self, status_code):
     if status_code in [200, 201, 202, 204]:
        return True
     error_messages = {
        400: "Bad Request - request couldn't be parsed",
        401: "Unauthorized - No valid API Key?",
        403: "Forbidden - Insufficient permissions",
        404: "Not Found - movie or resource doesn't exist",
        405: "Method Not Allowed - wrong HTTP method used",
        409: "Conflict - movie already exists in library?",
        422: "Unprocessable Entity - invalid movie data (bad TMDB ID or missing required fields?)",
        500: "Internal Server Error - This is most likely due to a logic bug in this addon"
     }
     message = error_messages.get(status_code, f"Unexpected error (HTTP {status_code})")
     self._error_notification(message)
     return False