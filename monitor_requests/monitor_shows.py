from monitor_requests.monitor_requests import get_context_menu_by_status, get_url_by_status, is_directory
from utils.utils import get_status_label, make_art, set_info_tag
from utils.url_handling import build_url
import xbmcplugin
import xbmcgui

def show_requested_episodes(jellyseer_client, sonarr_client, settings, addon_handle):
    xbmcplugin.setContent(addon_handle, 'videos')
    requests_data = settings.get_preferences("episode_requests")
    episode_requests = requests_data.get("requests", {})
    for id, data in episode_requests.items():
        for season, episode_list in data.get("seasons").items():
           show_requested_episodes_by_season(id, season, jellyseer_client, sonarr_client, addon_handle, episode_list)
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)  


def show_series_request(id, request_id, mediaData, seer_status, item, sonarr_client, addon_handle):
        requestData_sonarr_series = []
        if sonarr_client is not None:     
            requestData_sonarr_series =  get_sonarr_queue_data_series(sonarr_client)
        arr_status = ""
        timeleft = ""
        if seer_status in [2,3]:
         for item in  requestData_sonarr_series:
          if item.get("tmdbId") == id:
             try:
                 timeleft = item.get("timeleft")
             except:
                 continue
        label_text = mediaData.get('title') or mediaData.get('name') or "Untitled"
        label_text += " " + get_status_label(int(seer_status))
        plot_text = ""
        if seer_status == 3:
            if arr_status == "downloading":
                            plot_text += f" Time left: {timeleft} h,"
        url =  build_url({'mode': "show_requested_seasons", "id": id }) 
        list_item = xbmcgui.ListItem(label=label_text)
        list_item.addContextMenuItems(get_context_menu_by_status(seer_status, id, request_id, "tv"))
        info = {'title': label_text, 'plot': plot_text}
        set_info_tag(list_item, info)
        art = make_art(mediaData)
        list_item.setArt(art)
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)


def show_requested_seasons(id, request_id, jellyseer_client, addon_handle, sonarr_enable = False):
    if sonarr_enable:
        xbmcplugin.setContent(addon_handle, 'seasons')
    else:
        xbmcplugin.setContent(addon_handle, 'files')
    try:
        seer_info = jellyseer_client.api_request(f"/tv/{id}")
    except:
        return
    media_info = seer_info.get("mediaInfo", [])
    seasons = media_info.get("seasons", []) if media_info else []      
    for season in seasons :
        season_number = season.get("seasonNumber", 0)
        seer_status = int(season.get("status", 0)) 
        label_text = f"Season {season_number} " + get_status_label(seer_status)
        list_item = xbmcgui.ListItem(label=label_text)
        url = ""
        
        if sonarr_enable:
            list_item.setInfo('video', {
            'mediatype': 'season',
            'season': season_number
            })
            url = build_url({"mode": "show_requested_episodes_by_season", "type": "tv", "id": id, "season": season_number})
        list_item.addContextMenuItems(get_context_menu_by_status(seer_status, id, request_id, "tv"))
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)      
    xbmcplugin.endOfDirectory(addon_handle,  cacheToDisc=False)


def show_requested_episodes_by_season(id, season, jellyseer_client, sonarr_client, addon_handle, filter = []):
    episodes = get_sonarr_episodes(id, season, sonarr_client)
    try:
        seer_episode_data = jellyseer_client.api_request(f"/tv/{id}/season/{season}").get("episodes", [])
        show_name = jellyseer_client.api_request(f"/tv/{id}", method="GET").get("name", "")
        sonarr_requests = sonarr_client.api_request(f"/queue", params={}, use_cache=False).get("records")
    except:
        return
    if sonarr_client.has4k():
        episodes += get_sonarr_episodes(id, season, sonarr_client, use_4k=True)
        try:
            sonarr_requests += sonarr_client.api_request(f"/queue", params={}, request_4k=True, use_cache=False).get("records")
        except:
            return
    for ep in episodes:
        episode_id = ep.get("id")
        title = ep.get("title")
        ep_number = ep.get("episodeNumber")
        if filter and ep_number not in filter:
            continue
        hasFile = ep.get("hasFile")
        plot_text = ""
        status = 6
        if hasFile:
            status = 5
            plot_text = "[COLOR lime](Available)[/COLOR]"
        else:
            found = False
            for request in sonarr_requests:
                if int(request.get("episodeId")) == int(episode_id):
                    status = 3
                    found = True
                    status = request.get("status")
                    plot_text += f"[COLOR cyan]({status})[/COLOR]"
                    size = float(request.get("size"))/(1024**3)
                    sizeleft = float(request.get("sizeleft"))/(1024**3)
                    timeleft = request.get("timeleft")
                    plot_text += f"[CR] Time left: {timeleft} h"
                    sizedone =  size - sizeleft
                    plot_text += f"[CR] {sizedone:.1f} GB / {size:.1f} GB"
                    break
            if not found:
                plot_text = "[COLOR red] (Missing) [/COLOR]"
        url = get_url_by_status(status, id, id, "episode", season, ep_number)
        list_item = xbmcgui.ListItem(label = title)
        list_item.addContextMenuItems(get_context_menu_by_status(status, id, "-1", "episode", season, ep_number, episode_id))
        list_item.setInfo("video",  {'title': title, 'tvshowtitle': show_name, "episode": ep_number, "season": season,  'plot': plot_text, 'mediatype': 'episode'})
        ##get Art
        for item in seer_episode_data:
            if ep_number == item.get("episodeNumber"):
                list_item.setArt({'icon': item.get("stillPath")})
                break
        
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_directory(status))
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_EPISODE)
    if not filter:
        xbmcplugin.endOfDirectory(addon_handle,  cacheToDisc=False)    

def get_sonarr_episodes(id, season_num, sonarr_client, use_4k=False):
    try:
        sonarr_series = sonarr_client.api_request(f"/series", request_4k = use_4k, use_cache=False)
    except:
        return
    series_id = ""
    for series in sonarr_series:
        if int(series.get("tmdbId")) == int(id):
           series_id = series.get("id")
           break
    try:
        episodes = sonarr_client.api_request(f"/episode", params={"seriesId": series_id}, request_4k = use_4k, use_cache=False)
    except:
        return
    episode_data = []
    for ep in episodes:
        if int(ep.get("seasonNumber")) != int(season_num):
            continue
        episode_data.append(ep)  
    return episode_data


def get_sonarr_queue_data_series(sonarr_client):
    try:
        requestData_sonarr = sonarr_client.api_request(f"/queue", params={}, request_4k=False, use_cache = False).get("records")
    except:
        return
    requestData_sonarr_4k = []
    if sonarr_client.has4k():
        try:
            requestData_sonarr_4k = sonarr_client.api_request(f"/queue", params={}, request_4k=True, use_cache = False).get("records")
        except:
            return
    foundSeriesIds = []
    requestData_sonarr_series = []
    for item in requestData_sonarr:
        seriesId = item.get("seriesId")
        if seriesId not in foundSeriesIds:
         foundSeriesIds.append(seriesId)
         try:
            tmdbId = sonarr_client.api_request(f"/series/{seriesId}").get("tmdbId")
         except:
             return
         item.update({"tmdbId" : tmdbId})
         requestData_sonarr_series.append(item)
    for item in requestData_sonarr_4k:
        seriesId = item.get("seriesId")
        if seriesId not in foundSeriesIds:
         foundSeriesIds.append(seriesId)
         try:
            tmdbId = sonarr_client.api_request(f"/series/{seriesId}", request_4k=True).get("tmdbId")
         except:
             return
         item.update({"tmdbId" : tmdbId})
         requestData_sonarr_series.append(item)
    return requestData_sonarr_series
