import appdaemon.plugins.hass.hassapi as hass
import time


class Garage(hass.Hass):

    def initialize(self):
        self.handle = None
        self.garage_door = self.args["garage_door"]
        self.light = self.args["light"] if "light" in self.args else None
        self.duration = self.args["light_duration"] if "light_duration" in self.args else 0

        self.listen_state(self.cb_garage_open, self.garage_door, new = "open", duration = 5, mode = 1)
        self.listen_state(self.cb_garage_open, self.garage_door, new = "open", duration = 15 * 60, mode = 2)

    def cb_garage_open(self, entity, attribute, old, new, kwargs):
        mode = kwargs["mode"]
        
        if mode == 1:
            self.log("garage opened")
            if self.sun_down():
                self.turn_on(self.light)
                self.start_timer()
            if self.noone_home():
                t = time.strftime("%d-%b-%Y %H:%M:%S")
                message = f"{t}: Garage door open"
        elif mode == 2:
            t = time.strftime("%d-%b-%Y %H:%M:%S")
            message = f"{t}: Garage door has been open for 15 minutes"
        else:
            return

        self.notify(message, name = "html5")

    def start_timer(self):
        if self.handle != None:
            self.cancel_timer(self.handle)
        
        self.log(f"{self.light} set to turn off in {self.duration} seconds")
        self.handle = self.run_in(self.end_timer, self.duration)

    def end_timer(self, kwargs):
        if self.get_state(self.garage_door) == "open":
            self.log("Garage door still open...starting new delay")
            self.start_timer()
        else:
            self.log(f"Turning off {self.light}")
            self.turn_off(self.light)
