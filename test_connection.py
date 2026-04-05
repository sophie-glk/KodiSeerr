from utils.utils import handle_empty_directory
import xbmcgui

def test_connection(jellyseerr_client, sonarr_client, radarr_client, settings, addon_handle):
    handle_empty_directory(addon_handle)
    results = ""
    succ = "[COLOR lime] Success [/COLOR]"
    fail = "[COLOR red] Fail [/COLOR]"

    jellyseerr_client.disable_error_messages()
    sonarr_client.disable_error_messages()
    radarr_client.disable_error_messages()

    # seerr
    status = fail
    try:
        response = jellyseerr_client.api_request("/settings/public")
        if response:
            status = succ
    except Exception:
        pass
    results += (status + "Seerr \n")

    # Sonarr (SD)
    if settings.enable_sonarr():

     status = fail
     try:
        response = sonarr_client.api_request("/system/status")
        if response:
            status = succ
     except Exception:
        pass
     results += (status + "Sonarr \n")

    # Sonarr (4K)
     if sonarr_client.has4k():
        status = fail
        try:
            response = sonarr_client.api_request("/system/status", request_4k=True)
            if response:
                status = succ
        except Exception:
            pass
        results += (status + "Sonarr 4K \n")

    # Radarr (SD)
    if settings.enable_radarr():
     status = fail
     try:
        response = radarr_client.api_request("/system/status")
        if response:
            status = succ
     except Exception:
        pass
     results += (status + "Radarr \n")

     # Radarr (4K)
     if radarr_client.has4k():
        status = fail
        try:
            response = radarr_client.api_request("/system/status", request_4k=True)
            if response:
                status = succ
        except Exception:
            pass
        results += (status + "Radarr 4K \n")

    xbmcgui.Dialog().textviewer("Connection Test Results", results)
