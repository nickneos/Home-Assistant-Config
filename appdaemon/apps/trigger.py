import appdaemon.plugins.hass.hassapi as hass

#
# App to send email report for devices running low on battery
#
# Args:
#
# threshold = value below which battery levels are reported and email is sent
# always_send = set to 1 to override threshold and force send
#
# None
#
# Release Notes
#
# Version 1.0:
#   Initial Version

class Trigger(hass.Hass):
    #
    # App to send email report for devices running low on battery
    #
    # Args:
    #
    # threshold = value below which battery levels are reported and email is sent
    # always_send = set to 1 to override threshold and force send
    #
    # None
    #
    # Release Notes
    #
    # Version 1.0:
    #   Initial Version
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