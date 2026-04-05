from apis.TraktClient import TraktClient
from utils.utils import set_info_tag
from utils.url_handling import build_url
import xbmcgui
import xbmcplugin

def trakt_router(args, addon_handle, addon_data_path, page=1):
    trakt_mode = args.get("trakt_mode" ,"")
    if trakt_mode != "":
        handle_trakt(trakt_mode, args, addon_handle, addon_data_path, page)
        return
    trakt_main_menu(addon_handle)

def trakt_main_menu(addon_handle):
    xbmcplugin.setContent(addon_handle, 'files')
    items = [
        ('recommended_shows',   'Recommended Shows',       'DefaultTVShows.png',              True),
        ('recommended_movies',  'Recommended Movies',      'DefaultMovies.png',               True),
        ('trending_shows',      'Trending Shows',          'DefaultTVShows.png',              True),
        ('trending_movies',     'Trending Movies',         'DefaultMovies.png',               True),
        ('popular_shows',       'Popular Shows',           'DefaultTVShows.png',              True),
        ('popular_movies',      'Popular Movies',          'DefaultMovies.png',               True),
        ('watched_shows',       'Most Watched Shows',      'DefaultRecentlyWatchedEpisodes.png', True),
        ('watched_movies',      'Most Watched Movies',     'DefaultRecentlyWatchedMovies.png',  True),
        ('played_shows',        'Most Played Shows',       'DefaultRecentlyWatchedEpisodes.png', True),
        ('played_movies',       'Most Played Movies',      'DefaultRecentlyWatchedMovies.png',  True),
        ('collected_shows',     'Most Collected Shows',    'DefaultTVShows.png',              True),
        ('collected_movies',    'Most Collected Movies',   'DefaultMovies.png',               True),
        ('anticipated_shows',   'Most Anticipated Shows',  'DefaultTVShows.png',              True),
        ('anticipated_movies',  'Most Anticipated Movies', 'DefaultMovies.png',               True),
        ('boxoffice_movies',    'Box Office Movies',       'DefaultMovies.png',               True),
        ('show_user_lists',    'My Lists',       'DefaultMovies.png',               True),
        ('show_trending_lists',    'Trending Lists',       'DefaultMovies.png',               True),
        ('show_popular_lists',    'Popular Lists',       'DefaultMovies.png',               True),
         ('show_watch_list',    'My Watchlist',       'DefaultMovies.png',               True),

    ]
    for item in items:
        if item[0] is None:
            continue
        mode, label, icon, is_folder = item
        list_item = xbmcgui.ListItem(label)
        list_item.setArt({'icon': icon, 'thumb': icon})
        url = build_url({'mode': 'trakt', 'trakt_mode': mode})
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, is_folder)
    xbmcplugin.endOfDirectory(addon_handle)

def handle_trakt(trakt_mode, args, addon_handle, addon_data_path, page=1):
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
    elif trakt_mode == "watched_shows":
        show_watched_shows(trakt_client, addon_handle, page)
    elif trakt_mode == "watched_movies":
        show_watched_movies(trakt_client, addon_handle, page)
    elif trakt_mode == "played_shows":
        show_played_shows(trakt_client, addon_handle, page)
    elif trakt_mode == "played_movies":
        show_played_movies(trakt_client, addon_handle, page)
    elif trakt_mode == "collected_shows":
        show_collected_shows(trakt_client, addon_handle, page)
    elif trakt_mode == "collected_movies":
        show_collected_movies(trakt_client, addon_handle, page)
    elif trakt_mode == "anticipated_shows":
        show_anticipated_shows(trakt_client, addon_handle, page)
    elif trakt_mode == "anticipated_movies":
        show_anticipated_movies(trakt_client, addon_handle, page)
    elif trakt_mode == "boxoffice_movies":
        show_boxoffice_movies(trakt_client, addon_handle)
    elif trakt_mode == "show_user_lists":
        from trakt.lists import show_user_lists
        show_user_lists(trakt_client, addon_handle, page=page)
    elif trakt_mode == "show_popular_lists":
        from trakt.lists import show_popular_lists
        show_popular_lists(trakt_client, addon_handle, page=page)
    elif trakt_mode == "show_trending_lists":
        from trakt.lists import show_trending_lists
        show_trending_lists(trakt_client, addon_handle , page=page)
    elif trakt_mode == "show_list_items":
        from trakt.lists import show_list_items
        show_list_items(args.get("user_slug"), args.get("list_id"), trakt_client, addon_handle, page=page)
    elif trakt_mode == "show_watch_list":
        from trakt.lists import show_watchlist
        show_watchlist(trakt_client, addon_handle, page=page)

# ── Recommended (no pagination per API) ──────────────────────────────────────
def show_recommended_shows(trakt_client, addon_handle):
    try:
        recommendations = trakt_client.api_request("GET", "/recommendations/shows?ignore_collected=false&ignore_watchlisted=false&limit=25&extended=full,images")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return 
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(recommendations, "tv", addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_recommended_movies(trakt_client, addon_handle):
    try:
        recommendations = trakt_client.api_request("GET", "/recommendations/movies?ignore_collected=false&ignore_watchlisted=false&limit=25&extended=full,images")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(recommendations, "movie", addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

# ── Trending ──────────────────────────────────────────────────────────────────
def show_trending_movies(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils.utils import add_next_page_button
    try:
        response, total_pages = trakt_client.paginated_request("GET", f"/movies/trending?extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    trending = [r.get("movie") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(trending, "movie", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "trending_movies"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_trending_shows(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils.utils import add_next_page_button
    try:
        response, total_pages = trakt_client.paginated_request("GET", f"/shows/trending?extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    trending = [r.get("show") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(trending, "tv", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "trending_shows"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

# ── Popular ───────────────────────────────────────────────────────────────────
def show_popular_shows(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils.utils import add_next_page_button
    try:
        popular, total_pages = trakt_client.paginated_request("GET", f"/shows/popular?extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(popular, "tv", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "popular_shows"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_popular_movies(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils.utils import add_next_page_button
    try:
        popular, total_pages = trakt_client.paginated_request("GET", f"/movies/popular?extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(popular, "movie", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "popular_movies"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)


# ── Most Watched ──────────────────────────────────────────────────────────────
def show_watched_shows(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils.utils import add_next_page_button
    try:
        response, total_pages = trakt_client.paginated_request("GET", f"/shows/watched/weekly?extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    shows = [r.get("show") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(shows, "tv", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "watched_shows"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_watched_movies(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils.utils import add_next_page_button
    try:
        response, total_pages = trakt_client.paginated_request("GET", f"/movies/watched/weekly?extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    movies = [r.get("movie") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(movies, "movie", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "watched_movies"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

# ── Most Played ───────────────────────────────────────────────────────────────
def show_played_shows(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils.utils import add_next_page_button
    try:
        response, total_pages = trakt_client.paginated_request("GET", f"/shows/played/weekly?extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    shows = [r.get("show") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(shows, "tv", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "played_shows"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_played_movies(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils.utils import add_next_page_button
    try:
        response, total_pages = trakt_client.paginated_request("GET", f"/movies/played/weekly?extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    movies = [r.get("movie") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(movies, "movie", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "played_movies"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

# ── Most Collected ────────────────────────────────────────────────────────────
def show_collected_shows(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils.utils import add_next_page_button
    try:
        response, total_pages = trakt_client.paginated_request("GET", f"/shows/collected/weekly?extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    shows = [r.get("show") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(shows, "tv", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "collected_shows"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_collected_movies(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils.utils import add_next_page_button
    try:
        response, total_pages = trakt_client.paginated_request("GET", f"/movies/collected/weekly?extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    movies = [r.get("movie") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(movies, "movie", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "collected_movies"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

# ── Most Anticipated ──────────────────────────────────────────────────────────
def show_anticipated_shows(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils.utils import add_next_page_button
    try:
        response, total_pages = trakt_client.paginated_request("GET", f"/shows/anticipated?extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    shows = [r.get("show") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(shows, "tv", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "anticipated_shows"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

def show_anticipated_movies(trakt_client, addon_handle, page=1, number_of_items=25):
    from utils.utils import add_next_page_button
    try:
        response, total_pages = trakt_client.paginated_request("GET", f"/movies/anticipated?extended=full,images&page={page}&limit={number_of_items}")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    movies = [r.get("movie") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(movies, "movie", addon_handle)
    add_next_page_button({"mode": "trakt", "trakt_mode": "anticipated_movies"}, int(page), int(total_pages), addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

# ── Box Office (top 10 only, no pagination) ───────────────────────────────────
def show_boxoffice_movies(trakt_client, addon_handle):
    try:
        response = trakt_client.api_request("GET", "/movies/boxoffice?extended=full,images")
    except Exception:
        xbmcplugin.endOfDirectory(addon_handle)
        return
    movies = [r.get("movie") for r in response]
    xbmcplugin.setContent(addon_handle, 'videos')
    display_response(movies, "movie", addon_handle)
    xbmcplugin.endOfDirectory(addon_handle)

# ── Lists ───────────────────────────────────
# TODO

def display_response(response, media_type, addon_handle, season = -1, episode = -1, use_tmdb_for_art=False):
    if response is None:
        return
    isFolder = True
    if media_type == "movie":
        isFolder = False
    for rec in response:
        tmdb_id = rec.get("ids", {}).get("tmdb", "")
        title = rec.get("title", "")
        year = rec.get("year", "")
        overview = rec.get("overview", "")
        label = f"{title} ({year})" if year else title
        images = rec.get("images", {})
        genres = rec.get("genres", [])
        rating = rec.get("rating", "")
        votes = rec.get("votes", "")
        runtime = int(rec.get("runtime", "") or 0)*60  # Trakt returns in minutes, kodi expects in seconds
        context_menu = []
        context_menu.append(('Show Details', f'RunPlugin({build_url({"mode": "show_details", "type": media_type, "id": tmdb_id})})'))
        context_menu.append(('Add to Favorites', f'RunPlugin({build_url({"mode": "add_favorite", "type": media_type, "id": tmdb_id})})'))
        url = build_url({'mode': 'browse_menu', 'type': media_type, 'id': tmdb_id, 'season': season, 'episode': episode})
        list_item = xbmcgui.ListItem(label=label)
        list_item.addContextMenuItems(context_menu)
        info = {'title': title, 'plot': overview, 'year': year, 'mediatype': media_type, 'genre': genres, 'rating': rating, 'votes': votes, 'duration': runtime}
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