import appdaemon.plugins.hass.hassapi as hass
import datetime


class Google_Home(hass.Hass):

    def initialize(self):
        self.run_daily(self.goolge_home_quiet_mode, datetime.time(23, 5), quiet = True)
        self.run_daily(self.goolge_home_quiet_mode, datetime.time(6, 55), quiet = False)
    
    def goolge_home_quiet_mode(self, kwargs):
        quiet_mode = kwargs["quiet"]
        for gh in self.args["devices"]:
            if quiet_mode:
                vol = "0.2"
            else:
                vol = "0.6" if gh == "media_player.google_home_main" else "0.5"
            self.log(f"Setting volume to {vol} for {gh}")
            self.call_service("media_player/volume_set", entity_id = gh, volume_level = vol)