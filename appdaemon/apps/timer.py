import appdaemon.plugins.hass.hassapi as hass


class Timer(hass.Hass):

    def initialize(self):
        self.handle = None
        self.device = self.args["device"]
        self.input = self.args["input"]
        self.units = self.args["units"] if "units" in self.args else "minutes"
        self.listen_state(self.cb_timer, self.input)
    
    def cb_timer(self, entity, attribute, old, new, kwargs):           
        dev = self.device

        if self.units == "minutes":
            sec = float(new) * 60 
        elif self.units == "hours":
            sec = float(new) * 60 * 60
        else:
            float(new)
        
        if self.handle != None:
            self.cancel_timer(self.handle)
            self.log(f"Cancelling {self.handle}")

        self.log(f"Turning off {dev} in {sec} seconds")
        self.handle = self.run_in(self.power_off, sec, device = dev)
        self.log(self.info_timer(self.handle))

    def power_off(self, kwargs):
        dev = kwargs["device"]
        platform, entity = self.split_entity(dev)

        self.log(f"Turning off {dev}")
        self.call_service(f"{platform}/turn_off", entity_id = dev)

