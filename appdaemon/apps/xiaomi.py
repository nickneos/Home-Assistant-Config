import appdaemon.plugins.hass.hassapi as hass


class Button(hass.Hass):

    def initialize(self):
        for switch in self.args["bedroom_switch"]:
            self.log(f"Setting up event listener for {switch}")
            self.listen_event(self.bedroom_switch, "click", entity_id = switch)
        for switch in self.args["outside_switch"]:
            self.log(f"Setting up event listener for {switch}")
            self.listen_event(self.outside_switch, "click", entity_id = switch)
        for switch in self.args["doorbell"]:
            self.log(f"Setting up event listener for {switch}")
            self.listen_event(self.doorbell, "click", entity_id = switch)


    def bedroom_switch(self, event_name, data, kwargs):
        click_type = data["click_type"]
        click_dev = data["entity_id"]
        
        if click_type == "single":
            dev = "light.Bedroom"
            self.log(f"{click_dev} pressed: click_type = {click_type} trigger = {dev}")
            self.call_service("light/toggle", entity_id = dev)
          
        elif click_type == "long_click_press":
            dev = "switch.master_switch"
            self.log(f"{click_dev} pressed: click_type = {click_type} trigger = {dev}")
            self.turn_off(dev)
        
        elif click_type == "double":
            dev = "switch.template_soniq_tv"
            self.log(f"{click_dev} pressed: click_type = {click_type} trigger = {dev}")
            self.call_service("switch/toggle", entity_id = dev)


    def outside_switch(self, event_name, data, kwargs):
        click_type = data["click_type"]
        click_dev = data["entity_id"]

        if click_type == "single":
            dev = "switch.arlec_1b"
            self.log(f"{click_dev} pressed: click_type = {click_type} trigger = {dev}")
            self.call_service("switch/toggle", entity_id = dev)

        elif click_type  == "double":
            dev = "switch.arlec_1c"
            self.log(f"{click_dev} pressed: click_type = {click_type} trigger = {dev}")
            self.call_service("switch/toggle", entity_id = dev)


    def doorbell(self, event_name, data, kwargs):
        
        if data["click_type"] == "single":
            script = "script/doorbell_1" if self.anyone_home() else "script/doorbell_2"
            self.log(f"Doorbell pressed...executing {script}")
            self.call_service(script)



          
