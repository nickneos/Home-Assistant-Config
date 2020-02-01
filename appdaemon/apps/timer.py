import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime

# default values
DEFAULT_UNITS = "minutes"

class Timer(hass.Hass):

    def initialize(self):
        self.utils = self.get_app("utils")
        self.device = self.args["device"]
        self.input_id = self.args["input_id"]
        self.timer_id = self.args.get("timer_id")
        self.units = self.args.get("units", DEFAULT_UNITS) 

        self.listen_state(self.cb_timer_start, self.input_id)
        self.listen_event(self.cb_timer_finish, "timer.finished",
                        entity_id = self.timer_id)
    
    def cb_timer_start(self, entity, attribute, old, new, kwargs):           
        dev = self.device

        if self.utils.is_off(dev):
            self.log(f"{dev} currently off...no timer set")
            self.set_value(self.input_id, 0)
            return

        if self.units == "minutes":
            sec = float(new) * 60 
        elif self.units == "hours":
            sec = float(new) * 60 * 60
        else:
            sec = float(new)
            self.units = "seconds"

        if float(new) > 0:
            if self.get_state(self.timer_id) == "active":
                self.call_service("timer/cancel", entity_id = self.timer_id)
            
            self.call_service("timer/start", entity_id = self.timer_id, duration = sec)
            self.log(f"Turning off {dev} in {round(float(new))} {self.units}")
        else:
            self.call_service("timer/cancel", entity_id = self.timer_id)
            self.log(f"Cancelling timer for {dev}")
    
    def cb_timer_finish(self, event_name, data, kwargs):
        self.utils.off(self.device)
        self.set_value(self.input_id, 0)

        
