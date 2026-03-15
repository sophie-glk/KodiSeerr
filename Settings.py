class Settings:
    def __init__(self, data_path, addon):
        self.data_path = data_path
        self.addon = addon
    
    def remember_last_quality(self):
        return self.addon.getSettingBool('remember_last_quality')
    def confirm_before_request(self):
        return self.addon.getSettingBool('confirm_before_request')
    def show_quality_profiles(self):
        return self.addon.getSettingBool('show_quality_profiles')
    def enable_ask_4k(self):
        return self.addon.getSettingBool('enable_ask_4k')
    def get_preferences(self, name):
        from utils import load_file
        preferences_path = self.get_preferences_path(name)
        return load_file(preferences_path)
    def save_preferences(self, name, data):
        from utils import save_file
        preferences_path = self.get_preferences_path(name)
        save_file(data, preferences_path)

    def get_episode_requests(self):
        from utils import load_file
        preferences_path = self.get_preferences_path()
        prefs = load_file(preferences_path)
    def enable_radarr(self):
        return self.addon.getSettingBool('radarr_enable')
    def enable_sonarr(self):
        return self.addon.getSettingBool('sonarr_enable')
    def show_request_status(self):
        return self.addon.getSettingBool('show_request_status')
    def get_preferences_path(self, filename):
        import xbmcvfs
        return xbmcvfs.translatePath(f"{self.data_path}/{filename}.json")

    
    