import xbmc
import xbmcgui
from utils.logging import notify_error, notify_info, log_error
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
        notify_info('Issue reported')
        xbmcgui.Dialog().notification('KodiSeerr', 'Issue reported', xbmcgui.NOTIFICATION_INFO)
    except Exception as e:
        log_error(f"Issue report error: {e}")
        notify_error("Failed to report issue")