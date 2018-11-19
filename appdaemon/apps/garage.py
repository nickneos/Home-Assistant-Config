import appdaemon.plugins.hass.hassapi as hass
import time


class Garage(hass.Hass):

    def initialize(self):
        self.listen_state(self.cb_garage_open, "cover.garage", new = "open", duration = 10, mode = 1)
        self.listen_state(self.cb_garage_open, "cover.garage", new = "open", duration = 15 * 60, mode = 2)
    
    def cb_garage_open(self, entity, attribute, old, new, kwargs):
        mode = kwargs["mode"]
        
        if mode == 1 and self.get_tracker_state("device_tracker.ashs_s8_plus") != "home" and \
                         self.get_tracker_state("device_tracker.nicks_note8") != "home":  
            t = time.strftime("%d-%b-%Y %H:%M:%S")
            message = f"{t}: Garage door open"
        elif mode == 2:
            t = time.strftime("%d-%b-%Y %H:%M:%S")
            message = f"{t}: Garage door has been open for 15 minutes"
        else:
            return

        self.notify(message, name = "html5")