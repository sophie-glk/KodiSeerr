import xbmc
import xbmcgui
import xbmcplugin
import json

def play_local_file(tmdb_id, media_type, jellyseer_client, addon_handle, season = 1, episode = 1):
    try:
        data = jellyseer_client.api_request(f"/{media_type}/{tmdb_id}").get("externalIds")
    except:
        return
    imdb_id = data.get("imdbId")
    tvdb_id = data.get("tvdbId")

    if media_type == "movie":
        path = get_local_movie(tmdb_id, imdb_id, tvdb_id)
    else:
        path = get_local_episode(tvdb_id, tmdb_id, imdb_id, season, episode)

    if path is None:
         xbmcgui.Dialog().notification('KodiSeerr', f'Could not find the local file', xbmcgui.NOTIFICATION_ERROR, 4000)
         return
    play_item = xbmcgui.ListItem()
    play_item.setPath(path)
    play_item.setProperty('IsPlayable', 'true')
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def get_local_episode(tvdb_id, tmdb_id, imdb_id, season, episode):
    show_query = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetTVShows",
        "params": {"properties": ["uniqueid"]},
        "id": 1
    }

    response = xbmc.executeJSONRPC(json.dumps(show_query))
    data = json.loads(response)
    shows = data.get("result", {}).get("tvshows", [])
    show = None
    for s in shows:
        uids = s.get("uniqueid", {})
        if str(uids.get("tvdb", "")) == str(tvdb_id) or str(uids.get("tmdb", "")) == str(tmdb_id) or str(uids.get("imdb", "")) == str(imdb_id):
            show = s
            break
    if show is None:
        from utils.logging import log_error
        log_error(f"Show with TvDB ID {tvdb_id} not found in local library")
        return None
    show_id = show.get("tvshowid")
    
    episode_query = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetEpisodes",
        "params": {
            "tvshowid": show_id,
            "season": int(season),
            "properties": ["file"],
            "filter": {"field": "episode", "operator": "is", "value": str(episode)}
        },
        "id": 2
    }
    response = xbmc.executeJSONRPC(json.dumps(episode_query))
    data = json.loads(response)
    episodes = data.get('result', {}).get('episodes', [])
    if episodes:
        return episodes[0].get('file')
    else:
        return None
    

def get_local_movie(tmdb_id, imdb_id, tvdb_id):
    query = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetMovies",
        "params": {
            "properties": ["uniqueid", "title", "file"]
        },
        "id": 3
    }
    
    response = xbmc.executeJSONRPC(json.dumps(query))
    data = json.loads(response)
    movies = data.get("result", {}).get("movies", [])
    movie = None
    for m in movies:
        uids = m.get("uniqueid", {})
        if str(uids.get("tmdb", "")) == str(tmdb_id) or str(uids.get("imdb", "")) == str(imdb_id) or str(uids.get("tvdb", "")) == str(tvdb_id):
            movie = m
            break
    if movie is not None:
        return movie.get("file")
    else:
        return None

        