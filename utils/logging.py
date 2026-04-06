import xbmc
prefix  = "[KodiSeerr]"
def log_error(message):
    global prefix
    xbmc.log(f"{prefix} Trakt: {message}", level=xbmc.LOGERROR)