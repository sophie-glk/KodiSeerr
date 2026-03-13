from utils import build_url, get_media_status, load_file, save_file
import xbmc
import xbmcgui
import xbmcvfs
import xbmcplugin
import os
import json

def do_request(media_type, id, enable_ask_4k, jellyseer_client, addon, addon_handle, sonarr_client = None, season = -1, episode_number = -1, skip_dialog = False):
    """Handle media request with advanced options"""
    seasons_to_request = [season]
    tv_request_types = []
    confirm_string = ""
    if media_type == "tv" and not skip_dialog:
     if season > -1:
        tv_request_types.append(f"Request this season (Season {season})")    
     if sonarr_client is not None and episode_number > -1:
        tv_request_types.append("Request this episode")         
     tv_request_types += [ "Request all seasons", "Choose a season to request"]
     if sonarr_client is not None:
        tv_request_types.append("Choose an episode to request")     
     selected_tv_request_nr = xbmcgui.Dialog().select("Seerr Request", tv_request_types)

     if selected_tv_request_nr == -1:
         xbmcplugin.endOfDirectory(addon_handle, succeeded=False) 
         return
     
     selected_tv_request_type = tv_request_types[selected_tv_request_nr]
     if selected_tv_request_type == "Request this episode":
         media_type = "episode"
     elif selected_tv_request_type == f"Request this season ({season})":
         seasons_to_request = [season]
         confirm_string = f"Season {season}"
     elif selected_tv_request_type == f"Request all seasons":
         seasons_to_request = "all"
         confirm_string = f"(All seasons)"
     elif selected_tv_request_type == f"Choose a season to request":
         seasons = jellyseer_client.api_request(f"/tv/{id}").get("seasons", [])
         season_list = []
         for seas in seasons:
            season_list.append(str(seas.get("seasonNumber", -1)))
         selected_nr = xbmcgui.Dialog().select("Season", season_list)
         if selected_nr == -1:
                 return
         season_nr = int(season_list[selected_nr])
         seasons_to_request = [season_nr]
         confirm_string = f"Season {season_nr}"         
     elif selected_tv_request_type == "Choose an episode to request":
         seasons = jellyseer_client.api_request(f"/tv/{id}").get("seasons", [])
         season_list = []
         for seas in seasons:
             season_list.append(str(seas.get("seasonNumber", -1)))
         selected = xbmcgui.Dialog().select("Season", season_list)
         if selected == -1:
             xbmcplugin.endOfDirectory(addon_handle, succeeded=False) 
             return
         selected_season = int(season_list[selected])
         seasons_to_request = [selected_season]
         episodes = jellyseer_client.api_request(f"/tv/{id}/season/{selected_season}").get("episodes", [])
         episode_list = []
         for ep in episodes:
             ep_nr = ep.get("episodeNumber", "")
             item = xbmcgui.ListItem(label=f"Episode {ep_nr}: {ep.get("name")}")
             item.setProperty('ep_nr', str(ep_nr))
             episode_list.append(item)
         selected = xbmcgui.Dialog().select("Episode", episode_list)
         if selected == -1:
             xbmcplugin.endOfDirectory(addon_handle, succeeded=False) 
             return
         episode_number = int(episode_list[selected].getProperty("ep_nr"))
         media_type = "episode"
                       
    is4k = False
    quality_profile = None
    if enable_ask_4k:
        preferences_path = xbmcvfs.translatePath(f"special://profile/addon_data/{addon.getAddonInfo('id')}/preferences.json")
        prefs = load_file(preferences_path)
        if addon.getSettingBool('remember_last_quality') and 'last_4k_choice' in prefs:
            is4k = prefs['last_4k_choice']
        else:
            is4k = xbmcgui.Dialog().yesno('KodiSeerr', 'Request in 4K quality?')

        if addon.getSettingBool('remember_last_quality'):
            prefs['last_4k_choice'] = is4k
            save_file(prefs, preferences_path)
    confirm_before_request = addon.getSettingBool('confirm_before_request')
    show_quality_profiles = addon.getSettingBool('show_quality_profiles')

    if media_type == "episode":
        request_episode(id, season, episode_number, is4k, sonarr_client, jellyseer_client, confirm_before_request, addon_handle, addon)
        return

    if show_quality_profiles:
        profiles = get_quality_profiles(jellyseer_client)
        if profiles:
            profile_names = [p[1] for p in profiles]
            selected = xbmcgui.Dialog().select('Select Quality Profile', profile_names)
            if selected >= 0:
                quality_profile = profiles[selected][0]

    if confirm_before_request:
        title_data = jellyseer_client.api_request(f"/{media_type}/{id}")
        title = title_data.get('title') or title_data.get('name', 'this content') if title_data else 'this content'
        msg = f"Request {title} {confirm_string}"
        if is4k:
            msg += " in 4K"
        msg += "?"
        if not xbmcgui.Dialog().yesno('KodiSeerr', msg):
            xbmcplugin.endOfDirectory(addon_handle, succeeded=False) 
            return
    
    payload = {
        "mediaType": media_type,
        "mediaId": int(id),
        "is4k": is4k
    }
    
    if media_type == "tv":
        payload["seasons"] = seasons_to_request

    if quality_profile:
        payload["profileId"] = quality_profile
    
    try:
        jellyseer_client.api_request("/request", method="POST", data=payload)
        xbmcgui.Dialog().notification('KodiSeerr', 'Request Sent!', xbmcgui.NOTIFICATION_INFO, 3000)
    except Exception as e:
        xbmcgui.Dialog().notification('KodiSeerr', f'Request Failed: {str(e)}', xbmcgui.NOTIFICATION_ERROR, 4000)

def request_episode(id, season, episode_number, is4k, sonarr_client, jellyseerr_client, confirm_before_request, addon_handle, addon):
      
      series_data = sonarr_client.api_request(f"/series/lookup?term=tmdb:{id}", request_4k = is4k)[0]
      if not series_data:
          xbmcgui.Dialog().notification('KodiSeerr', f'Request Failed', xbmcgui.NOTIFICATION_ERROR, 4000)
          return
      #if the show is missing we have to add it.
      series_id = series_data.get("id")
      if series_id == None:
            title = series_data.get("title")
            seerr_sonarr_settings = {}
            for instance in jellyseerr_client.api_request("/settings/sonarr"):
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
            response = sonarr_client.api_request("/series", method="POST", data=series_data, request_4k = is4k)
            series_id = response.get("id")
            xbmc.sleep(1000) # wait for sonarr to add the show
      episodes = sonarr_client.api_request(f"/episode", params={"seriesId": series_id}, request_4k = is4k)
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
        msg = f"Request {title}: {episode_title}"
        if is4k:
            msg += " in 4K"
        msg += "?"
        if not xbmcgui.Dialog().yesno('KodiSeerr', msg):
            xbmcplugin.endOfDirectory(addon_handle, succeeded=False) 
            return
      sonarr_client.api_request("/command", method="POST", data = {"name": "EpisodeSearch", "episodeIds": episode_id }, request_4k = is4k)
      xbmcgui.Dialog().notification('KodiSeerr', 'Request Sent!', xbmcgui.NOTIFICATION_INFO, 3000)

      requests_path = xbmcvfs.translatePath(f"special://profile/addon_data/{addon.getAddonInfo('id')}/episode_requests.json")
      requests_data =  load_file(requests_path)
      shows = requests_data.get("requests", {})
      show = shows.get(id, {})
      show_seasons = show.get("seasons", {})
     
      show_season = show_seasons.get(str(season), []) 
      show_season.append(episode_number) 
      show_seasons[str(season)] = show_season
      show["seasons"] = show_seasons
      shows[id] = show 
      requests_data["requests"] = shows
      save_file(requests_data, requests_path)

def get_quality_profiles(jellyseer_client):
    """Get available quality profiles from server"""
    try:
        # This depends on Jellyseerr API - might need adjustment
        data = jellyseer_client.api_request('/settings/radarr')
        if data and isinstance(data, list) and len(data) > 0:
            profiles = data[0].get('profiles', [])
            return [(p['id'], p['name']) for p in profiles]
    except Exception as e:
        xbmc.log(f"[KodiSeerr] Quality profiles error: {e}", xbmc.LOGERROR)
    return []
