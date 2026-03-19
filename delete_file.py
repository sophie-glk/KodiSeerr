import xbmcgui
import xbmc
def delete_file(tmdb_id, media_type, jellyseer_client, sonarr_client, settings, is_4k = False, season = -1, episode_nr = -1, episode_id = -1):
    if not xbmcgui.Dialog().yesno('KodiSeerr', 'Delete this item?'):
        return
    
    if media_type == "episode":
        try:
            episode_file_id = sonarr_client.api_request(f"/episode/{episode_id}").get("episodeFileId")
            sonarr_client.api_request(f"/episodefile/{episode_file_id}", method="DELETE")
        except:
            return
        requests_data = settings.get_preferences("episode_requests")
        episode_requests = requests_data.get("requests", {})   
        to_remove = -1
        for id, data in episode_requests.items():
          for seas, episode_list in data.get("seasons").items():
              if str(seas) == str(season) and str(episode_nr) in str(episode_list):
                  to_remove = id
                  break   
        if to_remove != -1:
            episode_requests.pop(to_remove)
        settings.save_preferences("episode_requests", requests_data)    
        #xbmc.log(f"[kodiseerr] {response}", xbmc.LOGERROR)
        xbmc.executebuiltin('Container.Refresh')        
        return
    try:
        available_media = jellyseer_client.api_request("/media", params={"filter": "available"}, method="GET", use_cache = False).get("results", [])
    except:
        return
    media_id = 0
    for media in available_media:
        if str(media.get("tmdbId")) == str(tmdb_id):
            media_id = media.get("id")  
            break
    if media_id == 0:
        xbmcgui.Dialog().notification("KodiSeerr", f"Failed to find item in Seerr Database {tmdb_id}", xbmcgui.NOTIFICATION_ERROR)
        return
    try:
        jellyseer_client.api_request(f"/media/{media_id}/file", method="DELETE")
    except:
        pass
    xbmc.executebuiltin('Container.Refresh')
