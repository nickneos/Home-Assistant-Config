import appdaemon.plugins.hass.hassapi as hass
import time

class internet_down(hass.Hass):

    def initialize(self):
        self.utils = self.get_app("utils")
        sensor = self.args["sensor"]
        duration = self.args["duration"]
        self.sec = self.utils.get_sec(duration)

        self.listen_state(self.reboot_router_cb, sensor, new = "off", duration = self.sec)

    def reboot_router_cb(self, entity, attribute, old, new, kwargs):
        self.log(f"Offline for {self.sec} seconds...Rebooting Router")
        self.call_service("shell_command/reboot_router")