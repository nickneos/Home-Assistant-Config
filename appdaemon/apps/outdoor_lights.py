import appdaemon.plugins.hass.hassapi as hass

DEV1 = "switch.flood_light"
DEV2 = "switch.arlec_1b"

class OutdoorLights(hass.Hass):

    def initialize(self):
        self.listen_state(self.cb_switch_control, DEV1)
    
    def cb_switch_control(self, entity, attribute, old, new, kwargs):
        if new == "on":
            self.turn_on(DEV2)
        elif new == "off":
            self.turn_off(DEV2)