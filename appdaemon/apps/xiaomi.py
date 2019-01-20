import appdaemon.plugins.hass.hassapi as hass
import time


class Button(hass.Hass):

    def initialize(self):
        for switch in self.args["bedroom_switch"]:
            self.listen_event(self.bedroom_switch, "xiaomi_aqara.click",
                              entity_id = switch)
        
        for switch in self.args["outside_switch"]:
            self.listen_event(self.outside_switch, "xiaomi_aqara.click", 
                              entity_id = switch)
        
        for switch in self.args["doorbell"]:
            self.listen_event(self.doorbell, "xiaomi_aqara.click", 
                              entity_id = switch)

    def bedroom_switch(self, event_name, data, kwargs):
        device, entity = self.split_entity(data["entity_id"])
        button = entity
        click = data["click_type"]
        
        if click == "single":
            dev = "light.Bedroom"
            self.log(f"{button} pressed ({click})...action = {dev}")
            self.call_service("light/toggle", entity_id = dev)
          
        elif click == "long_click_press":
            dev = "switch.master_switch"
            self.log(f"{button} pressed ({click})...action = {dev}")
            self.turn_off(dev)
        
        elif click == "double":
            dev = "switch.template_soniq_tv"
            self.log(f"{button} pressed ({click})...action = {dev}")
            self.call_service("switch/toggle", entity_id = dev)


    def outside_switch(self, event_name, data, kwargs):
        device, entity = self.split_entity(data["entity_id"])
        button = entity
        click = data["click_type"]

        if click == "single":
            dev = "light.flood_light"
            self.log(f"{button} pressed ({click})...action = {dev}")
            self.call_service("light/toggle", entity_id = dev)

        elif click  == "double":
            dev = "light.fairy_lights"
            self.log(f"{button} pressed ({click})...action = {dev}")
            self.call_service("light/toggle", entity_id = dev)


    def doorbell(self, event_name, data, kwargs):
        
        if self.anyone_home():
            self.call_service("xiaomi_aqara/play_ringtone", 
                               gw_mac = self.args["gw_mac"],
                               ringtone_id = "10001", ringtone_vol = "25")

        self.call_service("light/lifx_effect_pulse", 
                           entity_id = "group.all_lights", 
                           brightness = "255", color_name = "green", 
                           period = "0.4", cycles = "10")

        if self.anyone_home():
            devices = ["media_player.google_home_main", 
                       "media_player.google_home_bedroom",
                       "media_player.google_home_office"]
            msg = ("Attention. There's someone at the door. "
                   + "There's someone at the door")
            for gh in devices:
                if self.get_state(gh) == "off": 
                    self.call_service("tts/google_say", entity_id = gh,
                                      message = msg)

        t = time.strftime("%d-%b-%Y %H:%M:%S")
        message = f"{t}: Doorbell pressed"
        self.log(message)
        self.notify(message, name = "html5")

