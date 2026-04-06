import xbmcgui
def show_details(media_type, media_id, jellyseer_client):
    """Show detailed information about a media item"""
    try:
        data = jellyseer_client.api_request(f"/{media_type}/{media_id}")
    except:
        return
    if not data:
        from utils.logging import notify_error
        notify_error("Failed to fetch details")
        return
    
    title = data.get('title') or data.get('name', 'Unknown')
    overview = data.get('overview', 'No description available')
    release_date = data.get('releaseDate') or data.get('firstAirDate', 'Unknown')
    rating = data.get('voteAverage', 0)
    genres = ', '.join([g['name'] for g in data.get('genres', [])])
    
    details = f"[B]{title}[/B]\n\n"
    details += f"Release Date: {release_date}\n"
    details += f"Rating: {rating}/10\n"
    if genres:
        details += f"Genres: {genres}\n"
    details += f"\n{overview}\n\n"
    
    if data.get('cast'):
        cast_names = [c['name'] for c in data['cast'][:10]]
        details += f"\n[B]Cast:[/B]\n{', '.join(cast_names)}\n"
    
    if data.get('recommendations'):
        details += f"\n[B]Recommended:[/B]\n"
        for rec in data['recommendations'][:5]:
            rec_title = rec.get('title') or rec.get('name')
            details += f"• {rec_title}\n"
    
    xbmcgui.Dialog().textviewer(title, details)