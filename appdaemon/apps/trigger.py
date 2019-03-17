import appdaemon.plugins.hass.hassapi as hass

class Trigger(hass.Hass):

    def initialize(self):
        
        self.trigger = self.args["trigger"]
        self.action = self.args["action"]
        self.listen_state(self.cb_switch_control, self.trigger)
    
    def cb_switch_control(self, entity, attribute, old, new, kwargs):
        if new == "on":
            for dev in self.action:
                self.log(f"Turning on {dev}")
                self.turn_on(dev)
        elif new == "off":
            for dev in self.action:
                self.log(f"Turning off {dev}")
                self.turn_off(dev)