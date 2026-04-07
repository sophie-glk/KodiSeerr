def trakt_login(addon_data_path):
    from apis.TraktClient import TraktClient
    TraktClient(addon_data_path, reauth=True)



if __name__ == '__main__':
    import sys
    import xbmcvfs
    from utils.get_addon_id import get_addon_id
    addon_id = get_addon_id()
    addon_data_path = xbmcvfs.translatePath(f"special://profile/addon_data/{addon_id}")
    mode = sys.argv[1]
    if mode == "trakt_login":
        trakt_login(addon_data_path)
    elif mode == "clear_cache":
        import cache
        cache.clear_cache()



