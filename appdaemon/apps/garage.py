import appdaemon.plugins.hass.hassapi as hass
import time


class Garage(hass.Hass):

    def initialize(self):
        self.handle = None
        self.garage_door = self.args["garage_door"]

        self.listen_state(self.cb_garage_open, self.garage_door, new = "open", duration = 5, mode = 1)
        self.listen_state(self.cb_garage_open, self.garage_door, new = "open", duration = 15 * 60, mode = 2)

    def cb_garage_open(self, entity, attribute, old, new, kwargs):
        mode = kwargs["mode"]

        if mode == 1:
            self.log("garage opened")
            if self.noone_home():
                t = time.strftime("%d-%b-%Y %H:%M:%S")
                msg = f"{t}: Garage door open"
                self.notify(msg, name = "html5")
        elif mode == 2:
            t = time.strftime("%d-%b-%Y %H:%M:%S")
            msg = f"{t}: Garage door has been open for 15 minutes"
            self.notify(msg, name = "html5")
        

