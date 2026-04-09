import requests
import xbmc
import xbmcaddon
import json
from utils.logging import notify_error, notify_info
import urllib.parse
addon = xbmcaddon.Addon()
monitor = xbmc.Monitor()


def main_loop():
    while not monitor.abortRequested():
      hostname = addon.getSetting('ntfy_url')
      topic = addon.getSetting('ntfy_topic')
      if not topic:
         notify_error("No ntfiy.sh topic was provided")
         if monitor.waitForAbort(60):
            break
         continue
      try:
        resp = requests.get(f"{hostname}/{urllib.parse.urlencode(topic)}/json", stream=True)
        resp.raise_for_status()
        for line in resp.iter_lines():
            notif = json.loads(line)
            if notif.get("event") == "message":
                notify_info(notif.get("message"))
      except Exception as e:
         notify_error("An error occured while connecting to the ntfy instance. Trying again in 1 minute.")
      if monitor.waitForAbort(60):
         break
      
if __name__ == '__main__':
    main_loop()
