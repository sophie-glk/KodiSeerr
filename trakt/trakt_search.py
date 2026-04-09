from trakt.trakt_main import display_response
from utils.utils import add_next_page_button, handle_empty_directory
import xbmcgui
import xbmcplugin
def search(query, trakt_client, addon_handle, page=1, number_of_items=25, external_keyboard = False):
    if not query and not external_keyboard:
       query = xbmcgui.Dialog().input('Search for Movie or TV Show')
    if not query:
        handle_empty_directory(addon_handle)
        return
    pDialog = xbmcgui.DialogProgressBG()
    pDialog.create("Search", "Fetching Results")
    try:
        response, total_pages =  trakt_client.paginated_request("GET", f"/search/movie,show?query={query}&extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        pDialog.close()
        return
    pDialog.update(50)
    for rec in response:
        seerr_media_type = "movie"
        trakt_media_type = rec.get("type")
        if trakt_media_type == "show":
            seerr_media_type = "tv"
        display_response([rec.get(trakt_media_type)], seerr_media_type, addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "search", "query" : query}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)    
    pDialog.close()