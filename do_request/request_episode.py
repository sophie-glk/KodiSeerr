
import xbmcgui
import xbmc
import xbmcplugin
def request_episode(id, season, episode_number, is4k, sonarr_client, jellyseerr_client, confirm_before_request, addon_handle, settings):
      try:      
        series_data = sonarr_client.api_request(f"/series/lookup?term=tmdb:{id}", request_4k = is4k)[0]
      except:
          return
      #if the show is missing we have to add it.
      series_id = series_data.get("id")
      if series_id == None:
            title = series_data.get("title")
            seerr_sonarr_settings = {}
            try:
                instances = jellyseerr_client.api_request("/settings/sonarr")
            except:
                return
            for instance in instances:
                if instance.get("is4k") == is4k and instance.get("isDefault"):
                    seerr_sonarr_settings = instance
                    break          
            if not seerr_sonarr_settings:
                xbmcgui.Dialog().notification('KodiSeerr', f'Request Failed.', xbmcgui.NOTIFICATION_ERROR, 4000)
                return
            series_data["RootFolderPath"] = seerr_sonarr_settings.get("activeDirectory")
            series_data["QualityProfileId"] = seerr_sonarr_settings.get("activeProfileId")
            series_data["path"] = f"{series_data["RootFolderPath"]}/{title}"
            series_data["seasonFolder"] = seerr_sonarr_settings.get("enableSeasonFolders")
            #series_data["addOptions"] = {"searchForMissingEpisodes": True}
            try:
                response = sonarr_client.api_request("/series", method="POST", data=series_data, request_4k = is4k)
            except:
                return
            series_id = response.get("id")
            xbmc.sleep(1000) # wait for sonarr to add the show
      try:
          episodes = sonarr_client.api_request(f"/episode", params={"seriesId": series_id}, request_4k = is4k)
      except:
          return
      if not episodes:
          xbmcgui.Dialog().notification('KodiSeerr', f'Request Failed', xbmcgui.NOTIFICATION_ERROR, 4000)
          return
      episode_id =[]
      episode_title = ""
      for ep in episodes:
          if int(ep.get("seasonNumber")) == int(season) and int(ep.get("episodeNumber")) == int(episode_number):
            episode_id = [ep.get("id")]
            episode_title = ep.get("title")

      if confirm_before_request:
        title = series_data.get("title")
        msg = f"Request {title}: {episode_title} (S{season}E{episode_number})"
        if is4k:
            msg += " in 4K"
        msg += "?"
        if not xbmcgui.Dialog().yesno('KodiSeerr', msg):
            xbmcplugin.endOfDirectory(addon_handle, succeeded=False) 
            return
      try:
          sonarr_client.api_request("/command", method="POST", data = {"name": "EpisodeSearch", "episodeIds": episode_id }, request_4k = is4k)
      except:
          return
      xbmcgui.Dialog().notification('KodiSeerr', 'Request Sent!', xbmcgui.NOTIFICATION_INFO, 3000)

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