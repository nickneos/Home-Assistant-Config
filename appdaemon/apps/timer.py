import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime

class Timer(hass.Hass):

    def initialize(self):
        self.utils = self.get_app("utils")
        self.handle = None
        self.device = self.args["device"]
        self.input = self.args["input"]
        self.units = self.args["units"] if "units" in self.args else "minutes"
        self.listen_state(self.cb_timer, self.input)
    
    def cb_timer(self, entity, attribute, old, new, kwargs):           
        dev = self.device

        if self.utils.is_off(dev):
            self.log(f"{dev} currently off...no timer set")
            return

        if self.units == "minutes":
            sec = float(new) * 60 
        elif self.units == "hours":
            sec = float(new) * 60 * 60
        else:
            sec = float(new)
            self.units = "seconds"

        if self.handle != None:
            self.cancel_timer(self.handle)
            self.log(f"Cancelling {self.handle}")

        self.handle = self.run_in(self.power_off, sec)
        t, i, k  = self.info_timer(self.handle)
        time_str = t.strftime("%Y-%m-%d %H:%M:%S")
        self.log(f"Turning off {dev} in {round(float(new))} {self.units} ({time_str})")
        
    def power_off(self, kwargs):
        dev = self.device
        self.utils.off(dev)
