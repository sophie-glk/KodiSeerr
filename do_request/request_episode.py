
from do_request.request_main import ask_4k, ask_quality_profile
import xbmcgui
import xbmc
import xbmcplugin
def request_episode(id, title, season, episode_number, sonarr_client, jellyseerr_client, addon_handle, settings):
      is4k = False
      if settings.enable_ask_4k() and sonarr_client.has4k():
        is4k = ask_4k(settings, f"{title} S{season}E{episode_number}")
      quality_profile = None
      if settings.show_quality_profiles():
        quality_profile = ask_quality_profile(jellyseerr_client, "tv", is4k)

      if settings.confirm_before_request():
        msg = f"Request {title} (S{season}E{episode_number})"
        if is4k:
            msg += " in 4K"
        msg += "?"
        if not xbmcgui.Dialog().yesno('KodiSeerr', msg):
            xbmcplugin.endOfDirectory(addon_handle, succeeded=False, cacheToDisc=False) 
            return

      try:      
        series_data = sonarr_client.api_request(f"/series/lookup?term=tmdb:{id}", request_4k = is4k)[0]
      except:
          return
      #if the show is missing we have to add it.
      series_id = series_data.get("id")
      if series_id == None:
            seerr_sonarr_settings = {}
            try:
                instances = jellyseerr_client.api_request("/settings/sonarr")
            except:
                from utils.logging import log_error
                log_error("Sonarr instance could not be found inside Seerr response")
                return
            for instance in instances:
                if instance.get("is4k") == is4k and instance.get("isDefault"):
                    seerr_sonarr_settings = instance
                    break          
            if not seerr_sonarr_settings:
                from utils.logging import notify_error
                notify_error("Request Failed")
                return
            series_data["RootFolderPath"] = seerr_sonarr_settings.get("activeDirectory")
            series_data["QualityProfileId"] = seerr_sonarr_settings.get("activeProfileId")
            series_data["path"] = f"{series_data['RootFolderPath']}/{title}"
            series_data["seasonFolder"] = seerr_sonarr_settings.get("enableSeasonFolders")
            #series_data["addOptions"] = {"searchForMissingEpisodes": True}
            try:
                series_data = sonarr_client.api_request("/series", method="POST", data=series_data, request_4k = is4k)
            except:
                return
            series_id = series_data.get("id")
            xbmc.sleep(1000) # wait for sonarr to add the show
      try:
          episodes = sonarr_client.api_request(f"/episode", params={"seriesId": series_id}, request_4k = is4k,  use_cache=False)
      except:
          return
      if not episodes:
          from utils.logging import notify_error
          notify_error("Request Failed")
          return
      episode_id = None
      for ep in episodes:
          if int(ep.get("seasonNumber")) == int(season) and int(ep.get("episodeNumber")) == int(episode_number):
            episode_id = ep.get("id")

      if not episode_id:
       from utils.logging import notify_error
       notify_error("Episode not found")
       return
      
      if quality_profile:  
        series_data["qualityProfileId"] = quality_profile
    
      ### send request

      try:
          season_data = series_data.get("seasons")
          for s in season_data:
              if s.get("seasonNumber") == season:
                 ### set monitored setting
                 s["monitored"] = True
                 break
          sonarr_client.api_request(f"/series/{series_id}", method="PUT", data=series_data, request_4k = is4k)   
          xbmc.sleep(1000)  # wait for sonarr to update
          sonarr_client.api_request("/command", method="POST", data = {"name": "EpisodeSearch", "episodeIds": [episode_id] }, request_4k = is4k)
      except:
          return
      from utils.logging import notify_info
      notify_info("Request Sent!")

      requests_data = settings.get_preferences("episode_requests")
      shows = requests_data.get("requests", {})
      show = shows.get(id, {})
      show_seasons = show.get("seasons", {})
      show_season = show_seasons.get(str(season), []) 
      show_season.append(episode_number) 
      show_seasons[str(season)] = show_season
      show["seasons"] = show_seasons
      shows[id] = show 
      requests_data["requests"] = shows
      settings.save_preferences("episode_requests", requests_data)