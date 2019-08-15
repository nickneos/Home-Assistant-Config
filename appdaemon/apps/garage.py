import appdaemon.plugins.hass.hassapi as hass
import time


class Garage(hass.Hass):

    def initialize(self):
        self.handle = None
        self.garage_door = self.args["garage_door"]
        self.garage_name = self.get_state(self.garage_door, attribute="friendly_name")
        self.notify_when_away = self.args["notify_when_away"] if "notify_when_away" in self.args else False

        if self.notify_when_away:
            self.listen_state(self.cb_garage_open, self.garage_door, new = "open", duration = 5, mode = 1)
        
        if "duration_notify" in self.args:
            self.duration = self.args["duration_notify"] * 60
            self.listen_state(self.cb_garage_open, self.garage_door, new = "open", duration = self.duration, mode = 2)

    def cb_garage_open(self, entity, attribute, old, new, kwargs):
        mode = kwargs["mode"]

        if mode == 1:
            self.log(f"{self.garage_name} opened")
            if self.noone_home():
                t = time.strftime("%d-%b-%Y %H:%M:%S")
                msg = f"{t}: {self.garage_name} open"
                self.notify(msg, name = "html5")
        elif mode == 2:
            t = time.strftime("%d-%b-%Y %H:%M:%S")
            duration = round(self.duration / 60)
            msg = f"{t}: {self.garage_name} has been open for {duration} minutes"
            self.notify(msg, name = "html5")
        

