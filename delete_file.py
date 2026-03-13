import xbmcgui
import xbmc
def delete_file(tmdb_id, media_type, jellyseer_client, sonarr_client, is_4k = False, season = -1, episode = -1):
    if not xbmcgui.Dialog().yesno('KodiSeerr', 'Delete this item?'):
        return
    if media_type == "episode":
        #TODO        
        return
    available_media = jellyseer_client.api_request("/media", params={"filter": "available"}, method="GET", use_cache = False).get("results", [])
    media_id = 0
    for media in available_media:
        if str(media.get("tmdbId")) == str(tmdb_id):
            media_id = media.get("id")  
            break
    if media_id == 0:
        xbmcgui.Dialog().notification("KodiSeerr", f"Failed to find item in Seerr Database {tmdb_id}", xbmcgui.NOTIFICATION_ERROR)
        return
    jellyseer_client.api_request(f"/media/{media_id}/file", method="DELETE")
    xbmc.executebuiltin('Container.Refresh')
