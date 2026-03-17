image_base = "https://image.tmdb.org/t/p/w500"
def build_url(query):
    from os import sys
    import urllib.parse
    base_url = sys.argv[0]
    return base_url + '?' + urllib.parse.urlencode(query)

def set_info_tag(list_item, info):
    info_tag = list_item.getVideoInfoTag()
    if info.get('title'): info_tag.setTitle(info['title'])
    if info.get('plot'): info_tag.setPlot(info['plot'])
    if info.get('year'):
        try:
            info_tag.setYear(int(info['year']))
        except Exception:
            pass
    if info.get('genre'): info_tag.setGenres(info['genre'])
    if info.get('rating'):
        try:
            info_tag.setRating(float(info['rating']))
        except Exception:
            pass
    if info.get('votes'):
        try:
            info_tag.setVotes(int(info['votes']))
        except Exception:
            pass
    if info.get('premiered'): info_tag.setPremiered(info['premiered'])
    if info.get('duration'):
        try:
            info_tag.setDuration(int(info['duration']))
        except Exception:
            pass
    if info.get('mpaa'): info_tag.setMpaa(info['mpaa'])
    if info.get('cast'): info_tag.setCast(info['cast'])
    if info.get('director'): info_tag.setDirector(info['director'])
    if info.get('studio'): info_tag.setStudio(info['studio'])
    if info.get('mediatype'): info_tag.setMediaType(info['mediatype'])

def make_art(item):
    art = {}
    for k in ["posterPath", "backdropPath", "logoPath", "bannerPath", "landscapePath", "iconPath", "clearartPath"]:
        if item.get(k):
            if k == "posterPath":
                art["poster"] = image_base + item[k]
                art["thumb"] = image_base + item[k]
            elif k == "backdropPath":
                art["fanart"] = image_base + item[k]
            elif k == "logoPath":
                art["clearlogo"] = image_base + item[k]
            elif k == "bannerPath":
                art["banner"] = image_base + item[k]
            elif k == "landscapePath":
                art["landscape"] = image_base + item[k]
            elif k == "iconPath":
                art["icon"] = image_base + item[k]
            elif k == "clearartPath":
                art["clearart"] = image_base + item[k]
    return art

def make_info(item, media_type):
    release_date = item.get('releaseDate') or item.get('firstAirDate')
    year = int(release_date.split("-")[0]) if release_date and release_date.split("-")[0].isdigit() else 0
    def join_names(obj_list):
        return ', '.join(
            g['name'] if isinstance(g, dict) and 'name' in g else str(g)
            for g in obj_list
        )
    genres = join_names(item.get('genres', []))
    studio = join_names(item.get('studios', [])) if item.get('studios') else ''
    country = join_names(item.get('productionCountries', [])) if item.get('productionCountries') else ''
    mpaa = item.get('certification', '')
    runtime = item.get('runtime', 0)
    try:
        runtime = int(runtime)
    except Exception:
        runtime = 0
    try:
        rating = float(item.get('voteAverage', 0))
    except Exception:
        rating = 0.0
    votes = item.get('voteCount', 0)
    try:
        votes = int(votes)
    except Exception:
        votes = 0
    director = ', '.join([c['name'] for c in item.get('crew', []) if c.get('job') == 'Director']) if item.get('crew') else ''
    cast = [person['name'] for person in item.get('cast', []) if isinstance(person, dict) and 'name' in person]
    cast_str = ', '.join(cast[:5])
    plot = item.get('overview', '')
    title = item.get('title') or item.get('name')
    rich_plot = f"{title} ({year})"
    if genres: rich_plot += f"\nGenres: {genres}"
    if studio: rich_plot += f"\nStudio: {studio}"
    if country: rich_plot += f"\nCountry: {country}"
    if mpaa: rich_plot += f"\nCertification: {mpaa}"
    if runtime: rich_plot += f"\nRuntime: {runtime} min"
    if rating: rich_plot += f"\nRating: {rating} ({votes} votes)"
    if director: rich_plot += f"\nDirector: {director}"
    if cast_str: rich_plot += f"\nCast: {cast_str}"
    if plot: rich_plot += f"\n\n{plot}"

    info = {
        'title': title or "",
        'plot': rich_plot or "",
        'year': year,
        'genre': genres or "",
        'rating': rating,
        'votes': votes,
        'premiered': release_date or "",
        'duration': runtime,
        'mpaa': mpaa or "",
        'cast': cast,
        'director': director or "",
        'studio': studio or "",
        'country': country or "",
        'mediatype': media_type
    }
    return info

def get_status_label(status):
    """Convert status code to label"""
    status_map = {
        1: "",
        2: "[COLOR yellow](Pending)[/COLOR]",
        3: "[COLOR cyan](Processing)[/COLOR]",
        4: "[COLOR lime](Partially Available)[/COLOR]",
        5: "[COLOR lime](Available)[/COLOR]"
    }
    return status_map.get(status, "")

def get_media_status(media_type, media_id, jellyseer_client):
    """Get the request status for a media item"""
    import xbmc
    try:
        data = jellyseer_client.api_request(f"/{media_type}/{media_id}")
        if data and data.get('mediaInfo'):
            status = data['mediaInfo'].get('status', 0)
            return status
    except Exception as e:
        xbmc.log(f"[KodiSeerr] Status check error: {e}", xbmc.LOGERROR)
    return 0

def list_episodes(tv_id, season_number, jellyseer_client, addon_handle):
    import xbmcplugin
    import xbmcgui
    xbmcplugin.setContent(addon_handle, 'episodes')
    data = jellyseer_client.api_request(f"/tv/{tv_id}/season/{season_number}")
    if not data:
        xbmcgui.Dialog().notification("KodiSeerr", "Failed to fetch episodes", xbmcgui.NOTIFICATION_ERROR)
        xbmcplugin.endOfDirectory(addon_handle)
        return
    episodes = data.get('episodes', [])
    show_title = data.get('show', {}).get('name') or data.get('show', {}).get('title', '')
    for ep in episodes:
        ep_num = ep.get('episodeNumber', 0)
        title = ep.get('name') or ep.get('title', f"Episode {ep_num}")
        label = f"S{season_number:02d}E{ep_num:02d} - {title}"
        list_item = xbmcgui.ListItem(label=label)
        info = make_info(ep, 'episode')
        art = make_art(ep)
        set_info_tag(list_item, info)
        list_item.setArt(art)
        xbmcplugin.addDirectoryItem(addon_handle, '', list_item, False)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_EPISODE)
    xbmcplugin.endOfDirectory(addon_handle)

def list_genres(media_type, jellyseer_client, addon_handle):
    import xbmcplugin
    import xbmcgui
    xbmcplugin.setContent(addon_handle, 'genres')
    data = jellyseer_client.api_request(f"/genres/{media_type}", params={})
    if data:
        for item in data:
            name = item.get('name')
            id = item.get('id')
            display_type = "movies" if media_type == "movie" else media_type
            url = build_url({'mode': 'genre', 'display_type': display_type, 'genre_id': id})
            list_item = xbmcgui.ListItem(label=name)
            list_item.setArt({'icon': 'DefaultGenre.png'})
            xbmcplugin.addDirectoryItem(addon_handle, url, list_item, True)
    else:
        xbmcgui.Dialog().notification("KodiSeerr", "Failed to fetch genres", xbmcgui.NOTIFICATION_ERROR)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.endOfDirectory(addon_handle)

def list_items(data, mode,  addon_handle, display_type=None, genre_id=None, show_status=True, hide_pagination=True):
    import xbmc
    import xbmcplugin
    import xbmcgui
    items = data.get('results', [])
    current_page = data.get('page', 1)
    total_pages = data.get('totalPages', 1)
    
    is_widget = xbmc.getCondVisibility('Window.IsVisible(home)')
    if items:
        first_media_type = items[0].get('mediaType', 'video')
        if first_media_type == 'movie':
            xbmcplugin.setContent(addon_handle, 'movies')
        elif first_media_type == 'tv':
            xbmcplugin.setContent(addon_handle, 'tvshows')
        else:
            xbmcplugin.setContent(addon_handle, 'videos')
    else:
        xbmcplugin.setContent(addon_handle, 'videos')

    if not (is_widget and hide_pagination):
        page_info = xbmcgui.ListItem(label=f'[I]Page {current_page} of {total_pages}[/I]')
        page_info.setArt({'icon': 'DefaultAddonNone.png'})
        xbmcplugin.addDirectoryItem(addon_handle, '', page_info, False)

        params = {'mode': 'jump_to_page', 'original_mode': mode}
        if mode == "genre":
            params['genre_id'] = genre_id
            params['display_type'] = display_type
        jump_url = build_url(params)
        jump_item = xbmcgui.ListItem(label='[B]Jump to Page...[/B]')
        jump_item.setArt({'icon': 'DefaultAddonNone.png'})
        xbmcplugin.addDirectoryItem(addon_handle, jump_url, jump_item, True)

        if current_page > 1:
            params = {
                'mode': mode,
                'page': current_page - 1
            }
            if mode == "genre":
                params['genre_id'] = genre_id
                params['display_type'] = display_type
            prev_page_url = build_url(params)
            prev_item = xbmcgui.ListItem(label=f'[B]<< Previous Page ({current_page - 1})[/B]')
            prev_item.setArt({'icon': 'DefaultVideoPlaylists.png'})
            xbmcplugin.addDirectoryItem(addon_handle, prev_page_url, prev_item, True)

    for item in items:
        media_type = item.get('mediaType')
        title = item.get('title') or item.get('name')
        release_date = item.get('releaseDate') or item.get('firstAirDate')
        year = int(release_date.split("-")[0]) if release_date and release_date.split("-")[0].isdigit() else None
        label = f"{title} ({year})" if year else title
        
        if show_status:
            status = get_media_status(media_type, item.get('id'))
            status_label = get_status_label(status)
            if status_label:
                label += f" {status_label}"
        
        id = item.get('id')
        
        context_menu = []
        context_menu.append(('Show Details', f'RunPlugin({build_url({"mode": "show_details", "type": media_type, "id": id})})'))
        context_menu.append(('Add to Favorites', f'RunPlugin({build_url({"mode": "add_favorite", "type": media_type, "id": id})})'))
        
        url = build_url({'mode': 'request', 'type': media_type, 'id': id})
        list_item = xbmcgui.ListItem(label=label)
        list_item.addContextMenuItems(context_menu)
        info = make_info(item, media_type)
        art = make_art(item)
        set_info_tag(list_item, info)
        list_item.setArt(art)
        xbmcplugin.addDirectoryItem(addon_handle, url, list_item, False)
        if not (is_widget and hide_pagination):
         if current_page < total_pages:
            params = {
                'mode': mode,
                'page': current_page + 1
            }
            if mode == "genre":
                params['genre_id'] = genre_id
                params['display_type'] = display_type
            next_page_url = build_url(params)
            next_item = xbmcgui.ListItem(label=f'[B]Next Page ({current_page + 1}) >>[/B]')
            next_item.setArt({'icon': 'DefaultVideoPlaylists.png'})
            xbmcplugin.addDirectoryItem(addon_handle, next_page_url, next_item, True)
    
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_UNSORTED)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_VIDEO_YEAR)
    xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_VIDEO_RATING)
    xbmcplugin.endOfDirectory(addon_handle)

def jump_to_page(args):
    """Allow user to jump to a specific page"""
    import xbmcgui
    import xbmc
    keyboard = xbmcgui.Dialog().input('Enter Page Number', type=xbmcgui.INPUT_NUMERIC)
    if keyboard:
        try:
            page = int(keyboard)
            if page < 1:
                xbmcgui.Dialog().notification('KodiSeerr', 'Page number must be at least 1', xbmcgui.NOTIFICATION_ERROR)
                return
            
            original_mode = args.get('original_mode')
            params = {'mode': original_mode, 'page': page}
            
            if args.get('genre_id'):
                params['genre_id'] = args.get('genre_id')
            if args.get('display_type'):
                params['display_type'] = args.get('display_type')
            
            xbmc.executebuiltin(f'Container.Update({build_url(params)})')
        except ValueError:
            xbmcgui.Dialog().notification('KodiSeerr', 'Invalid page number', xbmcgui.NOTIFICATION_ERROR)

def add_next_page_button(url_dict, page: int, total_pages: int, addon_handle):
  import xbmcgui
  import xbmcplugin
  if page >= total_pages:
      return
  url_dict['page'] = page + 1
  button = xbmcgui.ListItem(label="Next Page")
  #art = make_art("")
  #button.setArt(art)
  xbmcplugin.addDirectoryItem(addon_handle, build_url(url_dict), button, True)

def load_file(file_path):
    import os
    import json
    import xbmc
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
    except Exception as e:
        xbmc.log(f"[KodiSeerr] Preferences load error: {e}", xbmc.LOGERROR)
    return {}

def save_file(data, file_path):
    import os
    import json
    import xbmc
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        xbmc.log(f"[KodiSeerr] File save error: {e}", xbmc.LOGERROR)

def handle_empty_directory(addon_handle):
        import xbmc
        import xbmcplugin
        xbmcplugin.setContent(addon_handle, 'videos')
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)   
        xbmc.sleep(50)
        xbmc.executebuiltin('Action(Back)')

     
