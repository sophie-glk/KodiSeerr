from monitor_requests.monitor_requests import get_context_menu_by_status, get_url_by_status, is_directory
from utils import get_status_label, make_art, set_info_tag
import xbmcgui
import xbmcplugin

def show_movie_request(id, mediaData, seer_status, item, radarr_client, addon_handle):
        requestData_radarr = []
        if radarr_client is not None:
            requestData_radarr = get_radarr_queue_data(radarr_client)
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
        label_text += " " + get_status_label(int(seer_status))
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