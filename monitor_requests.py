import utils
import xbmcplugin
import xbmcgui
import xbmc
import xbmcvfs
from utils import add_next_page_button, build_url, load_file
from utils import set_info_tag
from utils import make_art
def show_requests(page, jellyseer_client, radarr_client, sonarr_client, addon_handle, settings, pagesize = 25):
    """Display user's requests with pagination"""
    xbmcplugin.setContent(addon_handle, 'videos')
    requests_data = settings.get_preferences("episode_requests")
    if requests_data.get("requests", {}):
        list_item = xbmcgui.ListItem(label="Single Episodes")
        icon = "DefaultSets.png"
        list_item.setArt({'icon': icon, 'thumb': icon})
        url = build_url({"mode": "show_requested_episodes"})
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)      
    
    skip = (page - 1) * pagesize
    data = jellyseer_client.api_request("/request", params={"take": pagesize, "skip": skip, "sort": "added", "filter": "all"}, use_cache = False)
    items = data.get('results', []) if data else []
    requestData_radarr = []
    requestData_sonarr_series = []
    #TODO better pages
    if radarr_client is not None:
     requestData_radarr = get_radarr_queue_data(radarr_client)
    if sonarr_client is not None:     
     requestData_sonarr_series =  get_sonarr_queue_data_series(sonarr_client)
    for item in items:
        media = item.get('media', {})
        id = media.get('tmdbId')
        seer_status = media.get('status')
        media_type = media.get('mediaType')
        mediaData = jellyseer_client.api_request(f"/{media_type}/{id}", params={})
        if(media_type == "movie"):
          show_movie_request(id, mediaData, seer_status, item, requestData_radarr, addon_handle)
        elif(media_type == "tv"):
          show_series_request(id, mediaData, seer_status, item, requestData_sonarr_series, addon_handle)
    

    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
    page_info = data.get('pageInfo', {})
    total_pages = page_info.get('pages', 1)
    add_next_page_button({"mode": "requests"}, page, total_pages, addon_handle)
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)    

def show_requested_episodes(jellyseer_client, sonarr_client, settings, addon_handle):
    xbmcplugin.setContent(addon_handle, 'videos')
    requests_data = settings.get_preferences("episode_requests")
    episode_requests = requests_data.get("requests", {})
    for id, data in episode_requests.items():
        for season, episode_list in data.get("seasons").items():
           show_requested_episodes_by_season(id, season, jellyseer_client, sonarr_client, addon_handle, episode_list)
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)  


def show_series_request(id, mediaData, seer_status, item, requestData_sonarr_series, addon_handle):
        arr_status = ""
        timeleft = ""
        if seer_status in [2,3]:
         for item in  requestData_sonarr_series:
          if item.get("tmdbId") == id:
             try:
                 timeleft = item.get("timeleft")
             except:
                 continue
        request_id = item.get('id')
        label_text = mediaData.get('title') or mediaData.get('name') or "Untitled"
        label_text += " " + utils.get_status_label(int(seer_status))
        plot_text = ""
        if seer_status == 3:
            if arr_status == "downloading":
                            plot_text += f" Time left: {timeleft} h,"
        url =  build_url({'mode': "showrequestedseasons", "id": id }) 
        list_item = xbmcgui.ListItem(label=label_text)
        list_item.addContextMenuItems(get_context_menu_by_status(seer_status, id, "tv"))
        info = {'title': label_text, 'plot': plot_text}
        set_info_tag(list_item, info)
        art = make_art(mediaData)
        list_item.setArt(art)
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)
    
def show_movie_request(id, mediaData, seer_status, item, requestData_radarr, addon_handle):
        size = None
        sizeleft = None
        arr_status = ""
        timeleft = ""
        if seer_status in [2,3]:
         for item in requestData_radarr:
          if item.get("tmdbId") == id:
             try:
                 size = float(item.get("size"))/(1024**3)
                 sizeleft = float(item.get("sizeleft"))/(1024**3)
                 arr_status = item.get("status")
                 timeleft = item.get("timeleft")
             except:
                 continue
        request_id = item.get('id')
        label_text = mediaData.get('title') or mediaData.get('name') or "Untitled"
        label_text += " " + utils.get_status_label(int(seer_status))
        plot_text = ""
        if seer_status == 3:
            if arr_status != "":
             plot_text += f" Status: {arr_status}."
            if arr_status == "downloading":
                            plot_text += f" Time left: {timeleft}h."
                            if size is not None and sizeleft is not None:
                                sizedone =  size - sizeleft
                                plot_text += f" Download progress: {sizedone:.1f} GB / {size:.1f} GB."
        
        list_item = xbmcgui.ListItem(label=label_text)
        list_item.addContextMenuItems(get_context_menu_by_status(seer_status, id, "movie"))
        info = {'title': label_text, 'plot': plot_text}
        set_info_tag(list_item, info)
        art = make_art(mediaData)
        list_item.setArt(art)
        xbmcplugin.addDirectoryItem(addon_handle, get_url_by_status(seer_status, id, "movie"), list_item, is_directory(seer_status))

def get_sonarr_queue_data_series(sonarr_client):
    requestData_sonarr = sonarr_client.api_request(f"/queue", params={}, request_4k=False, use_cache = False).get("records")
    requestData_sonarr_4k = []
    if sonarr_client.has4k():
        requestData_sonarr_4k = sonarr_client.api_request(f"/queue", params={}, request_4k=True, use_cache = False).get("records")
    foundSeriesIds = []
    requestData_sonarr_series = []
    for item in requestData_sonarr:
        seriesId = item.get("seriesId")
        if seriesId not in foundSeriesIds:
         foundSeriesIds.append(seriesId)
         tmdbId = sonarr_client.api_request(f"/series/{seriesId}").get("tmdbId")
         item.update({"tmdbId" : tmdbId})
         requestData_sonarr_series.append(item)
    for item in requestData_sonarr_4k:
        seriesId = item.get("seriesId")
        if seriesId not in foundSeriesIds:
         foundSeriesIds.append(seriesId)
         tmdbId = sonarr_client.api_request(f"/series/{seriesId}", request_4k=True).get("tmdbId")
         item.update({"tmdbId" : tmdbId})
         requestData_sonarr_series.append(item)
    return requestData_sonarr_series

def get_radarr_queue_data(radarr_client):
    requestData_radarr = radarr_client.api_request(f"/queue", params={}, use_cache=False).get("records")
    requestData_radarr_4k = []
    if radarr_client.has4k():
        requestData_radarr_4k = radarr_client.api_request(f"/queue", params={}, request_4k=True, use_cache=False).get("records")
    for item in requestData_radarr:
        movieId = item.get("movieId")
        tmdbId = radarr_client.api_request(f"/movie/{movieId}").get("tmdbId")
        item.update({"tmdbId" : tmdbId})
    for item in requestData_radarr_4k:
        movieId = item.get("movieId")
        tmdbId = radarr_client.api_request(f"/movie/{movieId}", request_4k=True).get("tmdbId")
        item.update({"tmdbId" : tmdbId})
    return requestData_radarr + requestData_radarr_4k

def get_url_by_status(status, id, media_type, season=1, episode_number=1):
        is_directory = False
        tmdb_type = media_type
        if media_type == "episode":
            tmdb_type = "tv"
        if media_type != "movie":
            is_directory = True
        if status in [2, 3]:
            url = build_url({"mode": "cancel_request", "id": id, "handle_empty_directory": is_directory})
        elif status == 5:
            url = build_url({"mode": "play_local_file", "id": id, "type": tmdb_type, "season": season, "episode": episode_number})
        else:
            url = build_url({'mode': 'request', 'type': media_type, 'id': id, "season": season, "episode": episode_number, "skip_dialog": True, "handle_empty_directory": is_directory})
        return url

def get_context_menu_by_status(status, id, media_type, season=1, episode_nr=1, episode_id=-1):
        context_menu = []
        if status in [2, 3] and media_type != "episode":
            url = build_url({"mode": "cancel_request", "id": id})
            context_menu.append(('Cancel Request', f'RunPlugin({url})'))
        if  media_type != "movie":
            url = build_url({"mode": "request", "id": id, "type": "tv", "season": season})
            context_menu.append(('Request more', f'RunPlugin({url})'))
        if status == 5:
            url = build_url({"mode": "delete_file", "id": id, "type": media_type, "season": season, "episode": episode_nr, "episode_id": episode_id})
            context_menu.append(('Delete File', f'RunPlugin({url})'))  
        context_menu.append(('Show Details', f'RunPlugin({build_url({"mode": "show_details", "type": media_type, "id": id})})'))
        context_menu.append(('Refresh', f'RunPlugin({build_url({"mode": "refresh"})})'))
        return context_menu

def is_directory(status):
    if status == 5:
        return False
    return True


def show_requested_seasons(id, jellyseer_client, addon_handle, sonarr_enable = False):
    if sonarr_enable:
        xbmcplugin.setContent(addon_handle, 'seasons')
    else:
        xbmcplugin.setContent(addon_handle, 'files')
    seer_info = jellyseer_client.api_request(f"/tv/{id}")
    media_info = seer_info.get("mediaInfo", [])
    seasons = media_info.get("seasons", []) if media_info else []      
    for season in seasons :
        season_number = season.get("seasonNumber", 0)
        seer_status = int(season.get("status", 0)) 
        label_text = f"Season {season_number} " + utils.get_status_label(seer_status)
        list_item = xbmcgui.ListItem(label=label_text)
        url = ""
        
        if sonarr_enable:
            list_item.setInfo('video', {
            'mediatype': 'season',
            'season': season_number
            })
            url = build_url({"mode": "show_requested_episodes_by_season", "type": "tv", "id": id, "season": season_number})
        list_item.addContextMenuItems(get_context_menu_by_status(seer_status, id, "tv"))
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)      
    xbmcplugin.endOfDirectory(addon_handle)

def get_sonarr_episodes(id, season_num, sonarr_client, use_4k=False):
    sonarr_series = sonarr_client.api_request(f"/series", request_4k = use_4k, use_cache=False)
    series_id = ""
    for series in sonarr_series:
        if int(series.get("tmdbId")) == int(id):
           series_id = series.get("id")
           break
    episodes = sonarr_client.api_request(f"/episode", params={"seriesId": series_id}, request_4k = use_4k, use_cache=False)
    episode_data = []
    for ep in episodes:
        if int(ep.get("seasonNumber")) != int(season_num):
            continue
        episode_data.append(ep)  
    return episode_data

def show_requested_episodes_by_season(id, season, jellyseer_client, sonarr_client, addon_handle, filter = []):
    episodes = get_sonarr_episodes(id, season, sonarr_client)
    seer_episode_data = jellyseer_client.api_request(f"/tv/{id}/season/{season}").get("episodes", [])
    show_name = jellyseer_client.api_request(f"/tv/{id}", method="GET").get("name", "")
    sonarr_requests = sonarr_client.api_request(f"/queue", params={}, use_cache=False).get("records")
    if sonarr_client.has4k():
        episodes += get_sonarr_episodes(id, season, sonarr_client, use_4k=True)
        sonarr_requests += sonarr_client.api_request(f"/queue", params={}, request_4k=True, use_cache=False).get("records")
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
        url = get_url_by_status(status, id, "episode", season, ep_number)
        list_item = xbmcgui.ListItem(label = title)
        list_item.addContextMenuItems(get_context_menu_by_status(status, id, "episode", season, ep_number, episode_id))
        list_item.setInfo("video",  {'title': title, 'tvshowtitle': show_name, "episode": ep_number, "season": season,  'plot': plot_text, 'mediatype': 'episode'})
        ##get Art
        for item in seer_episode_data:
            if ep_number == item.get("episodeNumber"):
                list_item.setArt({'icon': item.get("stillPath")})
                break
        
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_directory(status))
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_EPISODE)
    xbmcplugin.endOfDirectory(addon_handle)    

#TODO Fix this feature, its broken
def cancel_request(tmdb_id, jellyseer_client, media_type):
    """Cancel a pending request"""
    if not xbmcgui.Dialog().yesno('KodiSeerr', 'Cancel this request?'):
        return
    requests = jellyseer_client.api_request("/request", use_cache=False).get("results", [])
    request_id = -1
    for request in requests:
        media = request.get("media", {})
        if str(tmdb_id) == str(media.get("tmdbId")):
            request_id = request.get("id")
            break
    if request_id != -1:    
        jellyseer_client.api_request(f"/request/{request_id}", method="DELETE")
        xbmcgui.Dialog().notification('KodiSeerr', 'Request cancelled', xbmcgui.NOTIFICATION_INFO)
        xbmc.executebuiltin('Container.Refresh')
    else:
        xbmcgui.Dialog().notification('KodiSeerr', f'Could not find a matching request', xbmcgui.NOTIFICATION_ERROR)