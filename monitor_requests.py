import xbmcplugin
import xbmcgui
import xbmc
from utils import build_url
from utils import set_info_tag
from utils import make_art
def show_requests(mode, current_page, jellyseer_client, radarr_client, sonarr_client, addon_handle):
    """Display user's requests with pagination"""
    xbmcplugin.setContent(addon_handle, 'videos')
    take = 20
    skip = (current_page - 1) * take
    data = jellyseer_client.api_request("/request", params={"take": take, "skip": skip, "sort": "added", "filter": "all"})
    items = data.get('results', []) if data else []
    page_info = data.get('pageInfo', {})
    total_results = page_info.get('results', len(items))
    total_pages = page_info.get('pages', 1)

    page_info_item = xbmcgui.ListItem(label=f'[I]Page {current_page} of {total_pages}[/I]')
    page_info_item.setArt({'icon': 'DefaultAddonNone.png'})
    xbmcplugin.addDirectoryItem(addon_handle, '', page_info_item, False)

    jump_url = build_url({'mode': 'jump_to_page', 'original_mode': mode})
    jump_item = xbmcgui.ListItem(label='[B]Jump to Page...[/B]')
    jump_item.setArt({'icon': 'DefaultAddonNone.png'})
    xbmcplugin.addDirectoryItem(addon_handle, jump_url, jump_item, True)

    if current_page > 1:
        prev_page_url = build_url({'mode': mode, 'page': current_page - 1})
        prev_item = xbmcgui.ListItem(label=f'[B]<< Previous Page ({current_page - 1})[/B]')
        prev_item.setArt({'icon': 'DefaultVideoPlaylists.png'})

    requestData_radarr = get_radarr_queue_data(radarr_client)
    requestData_sonarr_series =  get_sonarr_queue_data_series(sonarr_client)
    for item in items:
        media = item.get('media', {})
        id = media.get('tmdbId')
        size = None
        sizeleft = None
        arr_status = ""
        timeleft = ""
        seer_status = media.get('status')
        if seer_status in [2,3]:
         for item in requestData_radarr + requestData_sonarr_series:
          if item.get("tmdbId") == id:
             try:
                 size = float(item.get("size"))/(1024**3)
                 sizeleft = float(item.get("sizeleft"))/(1024**3)
                 arr_status = item.get("status")
                 timeleft = item.get("timeleft")
             except:
                 continue
        media_type = media.get('mediaType')
        request_id = item.get('id')
        mediaData = jellyseer_client.api_request(f"/{media_type}/{id}", params={})
        if not mediaData:
            continue
        label_text = mediaData.get('title') or mediaData.get('name') or "Untitled"
        plot_text = ""
        if seer_status == 2:
            label_text += " [COLOR yellow](Pending)[/COLOR]"
        elif seer_status == 3:
            label_text += " [COLOR cyan](Processing)[/COLOR]"
            label_text += f" Status: {arr_status}"
            plot_text += f" Status: {arr_status},"
            if arr_status == "downloading" and media_type == "movie":
                            plot_text += f" Time left: {timeleft} h,"
                            if size is not None and sizeleft is not None:
                                sizedone =  size - sizeleft
                                plot_text += f" {sizedone:.1f} GB / {size:.1f} GB"
        elif seer_status == 4:
            label_text += " [COLOR lime](Partially Available)[/COLOR]"
        elif seer_status == 5:
            label_text += " [COLOR lime](Available)[/COLOR]"

        context_menu = []
        if seer_status in [2, 3]:
            context_menu.append(('Cancel Request', f'RunPlugin({build_url({"mode": "cancel_request", "request_id": request_id})})'))
        context_menu.append(('Show Details', f'RunPlugin({build_url({"mode": "show_details", "type": media_type, "id": id})})'))
        if media_type == "movie":
           url = build_url({'mode': 'request', 'type': media_type, 'id': id})
        else:
           url =  build_url({'mode': "showrequestedseasons", "id": id }) 
        list_item = xbmcgui.ListItem(label=label_text)
        list_item.addContextMenuItems(context_menu)
        info = {'title': label_text, 'plot': plot_text}
        set_info_tag(list_item, info)
        art = make_art(mediaData)
        list_item.setArt(art)
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)

    if current_page < total_pages:
        next_page_url = build_url({'mode': mode, 'page': current_page + 1})
        next_item = xbmcgui.ListItem(label=f'[B]Next Page ({current_page + 1}) >>[/B]')
        next_item.setArt({'icon': 'DefaultVideoPlaylists.png'})
        xbmcplugin.addDirectoryItem(addon_handle, next_page_url, next_item, True)
    
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(addon_handle)    

def get_sonarr_queue_data_series(sonarr_client):
    requestData_sonarr = sonarr_client.api_request(f"/queue", params={}).get("records")
    foundSeriesIds = []
    requestData_sonarr_series = []
    for item in requestData_sonarr:
        seriesId = item.get("seriesId")
        if seriesId not in foundSeriesIds:
         foundSeriesIds.append(seriesId)
         tmdbId = sonarr_client.api_request(f"/series/{seriesId}").get("tmdbId")
         item.update({"tmdbId" : tmdbId})
         requestData_sonarr_series.append(item)
    return requestData_sonarr_series

def get_radarr_queue_data(radarr_client):
    requestData_radarr = radarr_client.api_request(f"/queue", params={}).get("records")
    for item in requestData_radarr:
        movieId = item.get("movieId")
        tmdbId = radarr_client.api_request(f"/movie/{movieId}").get("tmdbId")
        item.update({"tmdbId" : tmdbId})
    return requestData_radarr


def show_requested_seasons(id, jellyseer_client, addon_handle):
    xbmcplugin.setContent(addon_handle, 'seasons')
    seer_info = jellyseer_client.api_request(f"/tv/{id}")
    media_info = seer_info.get("mediaInfo", [])
    seasons = media_info.get("seasons", []) if media_info else []
    xbmc.log(f"DEBUG KODISEERR: Response: {media_info}", level=xbmc.LOGERROR)         
    for season in seasons :
        season_number = season.get("seasonNumber", 0)
        label_text = f"Season {season_number}"
        seer_status = int(season.get("status", 0)) 
        if seer_status == 2:
            label_text += " [COLOR yellow](Pending)[/COLOR]"
        elif seer_status == 3:
            label_text += " [COLOR cyan](Processing)[/COLOR]"
        elif seer_status == 4:
            label_text += " [COLOR lime](Partially Available)[/COLOR]"
        elif seer_status == 5:
            label_text += " [COLOR lime](Available)[/COLOR]"
        list_item = xbmcgui.ListItem(label=label_text)
        list_item.setInfo('video', {
            'mediatype': 'season',
            'season': season_number
        })
        url = build_url({"mode": "showrequestedepisodes", "type": "tv", "id": id, "season": season_number})
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)      
    xbmcplugin.endOfDirectory(addon_handle)

def get_sonarr_episodes(id, season_num, sonarr_client):
    sonarr_series = sonarr_client.api_request(f"/series")
    series_id = ""
    for series in sonarr_series:
        tmdbId =  series.get("tmdbId") 
        if int(series.get("tmdbId")) == int(id):
           series_id = series.get("id")
           break
    episodes = sonarr_client.api_request(f"/episode", params={"seriesId": series_id})
    episode_data = []
    for ep in episodes:
        if int(ep.get("seasonNumber")) != int(season_num):
            continue
        episode_data.append(ep)  
    return episode_data

def show_requested_episodes(id, season, sonarr_client, addon_handle):
    episodes = get_sonarr_episodes(id, season, sonarr_client)
    sonarr_requests = sonarr_client.api_request(f"/queue", params={}).get("records")
    for ep in episodes:
        title = ep.get("title")
        ep_number = ep.get("episodeNumber")
        hasFile = ep.get("hasFile")
        plot_text = ""
        if hasFile:
            plot_text = "[COLOR lime](Available)[/COLOR]"
        else:
            found = False
            for request in sonarr_requests:
                if int(request.get("episodeId")) == int(ep.get("id")):
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
        list_item = xbmcgui.ListItem()
        list_item.setInfo("video",  {'title': title, "episode": ep_number, "season": season,  'plot': plot_text, 'mediatype': 'episode'})
        url = build_url({'mode': 'request', 'type': "tv", 'id': id})
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, False)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_EPISODE)
    xbmcplugin.endOfDirectory(addon_handle)    

def cancel_request(request_id, jellyseer_client):
    """Cancel a pending request"""
    if xbmcgui.Dialog().yesno('KodiSeerr', 'Cancel this request?'):
        try:
            jellyseer_client.api_request(f"/request/{request_id}", method="DELETE")
            xbmcgui.Dialog().notification('KodiSeerr', 'Request cancelled', xbmcgui.NOTIFICATION_INFO)
            xbmc.executebuiltin('Container.Refresh')
        except Exception as e:
            xbmcgui.Dialog().notification('KodiSeerr', f'Failed to cancel: {str(e)}', xbmcgui.NOTIFICATION_ERROR)