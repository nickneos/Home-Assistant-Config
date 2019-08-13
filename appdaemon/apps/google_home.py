import appdaemon.plugins.hass.hassapi as hass
import datetime


class Quiet_Mode(hass.Hass):

    def initialize(self):
        self.device = self.args["device"]
        self.night_mode = self.args["night_mode"]
        self.day_mode = self.args["day_mode"]

        self.run_daily(self.gh_set_vol, 
                        datetime.time(self.night_mode["hour"], self.night_mode["min"]), 
                        vol = self.night_mode["vol"])
        self.run_daily(self.gh_set_vol, 
                        datetime.time(self.day_mode["hour"], self.day_mode["min"]), 
                        vol = self.day_mode["vol"])

    def gh_set_vol(self, kwargs):
        gh = self.device
        vol = kwargs["vol"]
        
        self.log(f"Setting volume to {vol} for {gh}")
        self.call_service("media_player/volume_set", entity_id = gh, volume_level = vol)