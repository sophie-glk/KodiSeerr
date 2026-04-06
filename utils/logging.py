name = "Seerr4Kodi"
prefix  = f"[{name}]"
def log_error(message):
    import xbmc
    global prefix
    xbmc.log(f"{prefix} Trakt: {message}", level=xbmc.LOGERROR)

def notify_error(message, heading = ""):
      import xbmcgui
      xbmcgui.Dialog().notification(
            heading=f"{prefix} {heading}",
            message=message,
            icon=xbmcgui.NOTIFICATION_ERROR,
            time=4000,
        )

def notify_info(message, heading = ""):
      import xbmcgui
      xbmcgui.Dialog().notification(
            heading=f"{prefix} {heading}",
            message=message,
            icon=xbmcgui.NOTIFICATION_INFO,
            time=4000,
        )