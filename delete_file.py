import xbmcgui
import xbmc
def delete_file(tmdb_id, media_type, jellyseer_client, sonarr_client, settings, is_4k = False, season = -1, episode_nr = -1, episode_id = -1):
    if not xbmcgui.Dialog().yesno('KodiSeerr', 'Delete this item?'):
        return
    
    if media_type == "episode":
        try:
            episode_file_id = sonarr_client.api_request(f"/episode/{episode_id}", is_4k = is_4k).get("episodeFileId")
            sonarr_client.api_request(f"/episodefile/{episode_file_id}", method="DELETE")
        except:
            return
        requests_data = settings.get_preferences("episode_requests")
        episode_requests = requests_data.get("requests", {})   
        to_remove = -1
        for id, data in episode_requests.items():
          found = False
          for seas, episode_list in data.get("seasons").items():
              if str(seas) == str(season) and episode_nr in episode_list:
                  episode_list.remove(episode_nr)
                  if not episode_list:
                      data["seasons"].pop(seas)
                  if not data["seasons"]:
                     episode_requests.pop(id)
                  found = True
                  break   
          if found:
              break
        settings.save_preferences("episode_requests", requests_data)    
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
        from utils.logging import notify_error
        notify_error(f"Failed to find item in Seerr Database {tmdb_id}")
        return
    try:
        jellyseer_client.api_request(f"/media/{media_id}/file", method="DELETE")
    except:
        pass
    xbmc.executebuiltin('Container.Refresh')
