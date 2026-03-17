from apis.TraktClient import TraktClient
from utils import build_url, set_info_tag
import xbmcgui
import xbmcplugin

def trakt(trakt_mode, addon_handle, addon_data_path, page = 1):
    if trakt_mode != "":
        handle_trakt(trakt_mode, addon_handle, addon_data_path, page)
        return
    trakt_main_menu(addon_handle)

def trakt_main_menu(addon_handle):
    xbmcplugin.setContent(addon_handle, 'files')
    items = [
        ('recommended_shows', 'Recommended Shows', 'DefaultRecentlyAddedMovies.png', True),
        ('recommended_movies', 'Recommended Movies', 'DefaultRecentlyAddedMovies.png', True),
        ('trending_shows', 'Trending Shows', 'DefaultRecentlyAddedMovies.png', True),
        ('trending_movies', 'Trending Movies', 'DefaultRecentlyAddedMovies.png', True),
        ('popular_shows', 'Popular Shows', 'DefaultRecentlyAddedMovies.png', True),
        ('popular_movies', 'Popular Movies', 'DefaultRecentlyAddedMovies.png', True)
    ]
    
    for item in items:
        if item[0] is None:
            continue
        mode, label, icon, is_folder = item
        list_item = xbmcgui.ListItem(label)
        list_item.setArt({'icon': icon, 'thumb': icon})
        url = build_url({'mode': "trakt", "trakt_mode": mode})
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(addon_handle)

def handle_trakt(trakt_mode, addon_handle, addon_data_path, page = 1):
    client_id = "033d0d37baa639a6e3a8e650184f05f04f391aa5b0482c91de44bd98d2518ed9"
    client_secret = "878ed8892926cee292e028d09b9fc4b00695af77fd47489b55518683a2c133e0"
    trakt_client = TraktClient(client_id, client_secret, addon_data_path)
    if trakt_mode == "recommended_shows":
        show_recommended_shows(trakt_client, addon_handle)
    elif trakt_mode == "recommended_movies":
        show_recommended_movies(trakt_client, addon_handle)
    elif trakt_mode == "trending_movies":
        show_trending_movies(trakt_client, addon_handle, page)
    elif trakt_mode == "trending_shows":
        show_trending_shows(trakt_client, addon_handle, page)
    elif trakt_mode == "popular_shows":
        show_popular_shows(trakt_client, addon_handle, page)
    elif trakt_mode == "popular_movies":
        show_popular_movies(trakt_client, addon_handle, page)

def show_recommended_shows(trakt_client, addon_handle):
    recommendations = trakt_client.api_request("GET", "/recommendations/shows?ignore_collected=false&ignore_watchlisted=false&limit=25&extended=full")
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(recommendations, "tv", addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_trending_movies(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils import add_next_page_button
    response, total_pages = trakt_client.paginated_request("GET", f"/movies/trending?extended=full&page={page}&limit={number_of_items}")
    trending = [r.get("movie") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(trending, "movie", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "trending_movies"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_trending_shows(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils import add_next_page_button
    response, total_pages = trakt_client.paginated_request("GET", f"/shows/trending?extended=full&page={page}&limit={number_of_items}")
    trending = [r.get("show") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(trending, "tv", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "trending_shows"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_popular_shows(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils import add_next_page_button
    popular, total_pages = trakt_client.paginated_request("GET", f"/shows/popular?extended=full&page={page}&limit={number_of_items}")
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(popular, "tv", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "popular_shows"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_popular_movies(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils import add_next_page_button
    popular, total_pages = trakt_client.paginated_request("GET", f"/movies/popular?extended=full&page={page}&limit={number_of_items}")
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(popular, "movie", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "popular_movies"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_recommended_movies(trakt_client, addon_handle):
    xbmcplugin.setContent(addon_handle, 'videos')
    recommendations = trakt_client.api_request("GET", "/recommendations/movies?ignore_collected=false&ignore_watchlisted=false&limit=25&extended=full")
    display_response(recommendations, "movie", addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def display_response(response, media_type, addon_handle):
     if response is None:
         return
     isFolder = True
     if media_type == "movie":
         isFolder = False
     for rec in response:
          tmdb_id = rec.get("ids", {}).get("tmdb")
          title = rec.get("title", "")
          year = rec.get("year", "")
          overview = rec.get("overview", "")
          label = f"{title} ({year})" if year else title
          images = rec.get("images", {})
          genres = rec.get("genres", [])
          rating = rec.get("rating", "")
          votes = rec.get("votes", "")
          runtime = rec.get("runtime", "")
          context_menu = []
          context_menu.append(('Show Details', f'RunPlugin({build_url({"mode": "show_details", "type": media_type, "id": tmdb_id})})'))
          context_menu.append(('Add to Favorites', f'RunPlugin({build_url({"mode": "add_favorite", "type": media_type, "id": tmdb_id})})'))
          url = build_url({'mode': 'browse_menu', 'type': media_type, 'id': tmdb_id})
          list_item = xbmcgui.ListItem(label=label)
          list_item.addContextMenuItems(context_menu)
          info = {'title': title, 'plot': overview, 'year': year, 'mediatype': media_type, 'genre': genres, 'rating': rating, 'votes': votes, 'duration': runtime }
          set_info_tag(list_item, info)
          art = {}
          for k in ["poster", "fanart", "logo", "banner", "landscapePath", "thumb", "clearart"]:
           image = images.get(k)
           if image:
            image_path = "https://" + image[0]
            if k == "poster":
                art["poster"] = image_path
                art["thumb"] = image_path
            elif k == "fanart":
                art["fanart"] = image_path
            elif k == "logo":
                art["clearlogo"] = image_path
            elif k == "banner":
                art["banner"] = image_path
            elif k == "landscapePath":
                art["landscape"] = image_path
            elif k == "thumb":
                art["thumb"] = image_path
            elif k == "clearart":
                art["clearart"] = image_path
          list_item.setArt(art)

          xbmcplugin.addDirectoryItem(addon_handle, url, list_item, isFolder)
