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
    
    ### loop to check online

class milk_warmer(hass.Hass):

    def initialize(self):
        self.utils = self.get_app("utils")
        self.device = self.args["device"]
        self.duration = self.args["duration"]
        self.gh_devices = self.args["gh_devices"] if "gh_devices" in self.args else None

        self.listen_state(self.milk_warmer_cb, self.device, new = "on", duration = 5)
    
    def milk_warmer_cb(self, entity, attribute, old, new, kwargs):
        sec = self.utils.get_sec(self.duration)
        self.log(f"Turning off {self.device} in {sec} seconds")
        self.run_in(self.milk_warmer2_cb, sec)
    
    def milk_warmer2_cb(self, kwargs):
        if self.get_state(self.device) == "off":
            return
        
        self.utils.off(self.device)

        if self.gh_devices:
            gh_devices = self.utils.to_list(self.gh_devices)
            msg = ("Jax's Milk is Ready!")
            self.log(gh_devices)
            for gh in gh_devices:
                # if self.get_state(gh) == "off": 
                self.call_service("tts/google_translate_say", entity_id = gh, message = msg)

