import appdaemon.plugins.hass.hassapi as hass


class Timer(hass.Hass):

    def initialize(self):
        self.handle = None
        self.listen_state(self.timer, "input_select.timer_device", old = "Select...")
    
    def timer(self, entity, attribute, old, new, kwargs):
        n = float(self.get_state("input_number.timer_hours"))

        if new == "Main AC":
            dev = "climate.living_room"
        elif new == "Bedroom AC":
            dev = "climate.bedroom"
        else:
            return
        
        if self.handle != None:
            self.cancel_timer(self.handle)
            self.log(f"Cancelling {self.handle}")

        self.log(f"Turning off {dev} in {n} hour(s)")
        self.handle = self.run_in(self.power_off, n*60*60, device = dev)
        self.log(self.info_timer(self.handle))
        self.set_state("input_select.timer_device", state = old)
    
    def power_off(self, kwargs):
        dev = kwargs["device"]
        self.log(f"Turning off {dev}")
        self.turn_off(dev)

