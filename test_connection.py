from utils.utils import handle_empty_directory
import xbmcgui

def test_connection(jellyseerr_client, sonarr_client, radarr_client, settings, addon_handle):
    handle_empty_directory(addon_handle)
    results = ""
    succ = "[COLOR lime] Success [/COLOR]"
    fail = "[COLOR red] Fail [/COLOR]"


    # seerr
    status = fail
    try:
        jellyseerr_client.disable_error_messages()
        response = jellyseerr_client.api_request("/settings/public")
        if response:
            status = succ
    except Exception:
        pass
    results +=  "Seerr"
    results += status + "\n"

    # Sonarr (SD)
    if settings.enable_sonarr():

     status = fail
     try:
        sonarr_client.disable_error_messages()
        response = sonarr_client.api_request("/system/status")
        if response:
            status = succ
     except Exception:
        pass
     results +=  "Sonarr"
     results += status + "\n"

    # Sonarr (4K)
     if sonarr_client.has4k():
        status = fail
        try:
            sonarr_client.disable_error_messages()
            response = sonarr_client.api_request("/system/status", request_4k=True)
            if response:
                status = succ
        except Exception:
            pass
        results +=  "Sonarr (4k)"
        results += status + "\n"

    # Radarr (SD)
    if settings.enable_radarr():
     status = fail
     try:
        radarr_client.disable_error_messages()
        response = radarr_client.api_request("/system/status")
        if response:
            status = succ
     except Exception:
        pass
     results +=  "Radarr"
     results += status + "\n"

     # Radarr (4K)
     if radarr_client.has4k():
        status = fail
        try:
            radarr_client.disable_error_messages()
            response = radarr_client.api_request("/system/status", request_4k=True)
            if response:
                status = succ
        except Exception:
            pass
        results +=  "Radarr (4k)"
        results += status + "\n"

    xbmcgui.Dialog().textviewer("Connection Test Results", results)
