import xbmc
import xbmcgui
def report_issue(media_type, media_id, jellyseer_client):
    """Report an issue with media"""
    issue_types = ['Video Issue', 'Audio Issue', 'Subtitles Issue', 'Other']
    selected = xbmcgui.Dialog().select('Select Issue Type', issue_types)
    if selected < 0:
        return
    message = xbmcgui.Dialog().input('Describe the issue (optional)')
    try:
        payload = {
            "issueType": selected + 1,
            "message": message or ""
        }
        try:
            jellyseer_client.api_request(f"/{media_type}/{media_id}/issue", method="POST", data=payload)
        except:
            return
        xbmcgui.Dialog().notification('KodiSeerr', 'Issue reported', xbmcgui.NOTIFICATION_INFO)
    except Exception as e:
        xbmc.log(f"[KodiSeerr] Issue report error: {e}", xbmc.LOGERROR)
        xbmcgui.Dialog().notification('KodiSeerr', 'Failed to report issue', xbmcgui.NOTIFICATION_ERROR)