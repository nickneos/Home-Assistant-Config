import appdaemon.plugins.hass.hassapi as hass


class Router(hass.Hass):

    def initialize(self):
        self.listen_state(self.cb_reboot_router, "binary_sensor.online", new = "off", duration = 30 * 60)

    def cb_reboot_router(self, entity, attribute, old, new, kwargs):
        self.log("No Internet connectivity for 30 minutes...Rebooting router")
        self.call_service("mqtt/publish", 
                          topic = "cmnd/sonoff_s20_02/backlog", 
                          payload = "power 0; delay 100; power 1")