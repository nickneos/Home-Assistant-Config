import appdaemon.plugins.hass.hassapi as hass
import time

class Button(hass.Hass):

    def initialize(self):
        self.utils = self.get_app("utils")
        
        for button in self.args["buttons"]:
            self.listen_event(self.cb_button, "xiaomi_aqara.click",
                              entity_id = button)

    def cb_button(self, event_name, data, kwargs):
        click_type = data["click_type"]        
        action = None
        button = kwargs["entity_id"]
        
        for x in self.args["actions"]:
            if click_type == x["click_type"]:
                action = x
        if not action:
            return
        self.log(f"{button}: {action}")       
        
        button_type = action["type"] if "type" in action else "standard"
        tgt_devs = action["target_dev"] if "target_dev" in action else []
        tgt_devs = self.utils.to_list(tgt_devs)

        for dev in tgt_devs:
            if button_type == "standard":
                s = action["service"] 
                if s == "turn_on":
                    self.utils.on(dev)
                elif s == "turn_off":
                    self.utils.off(dev)
                elif s == "toggle":
                    self.utils.toggle(dev)
            
            elif button_type == "dimmer":
                if self.utils.is_off(dev):
                    self.call_service("light/turn_on", entity_id = dev)
                else:
                    dim_step = action["dim_step"] if "dim_step" in action else 3
                    dim_step_pct = round(100 / dim_step)
                    brightness = self.get_state(dev, attribute = "brightness")
                    if brightness:
                        brightness = self.utils.bound_to_100(brightness)
                        brightness = brightness + dim_step_pct
                        if brightness > 100:
                            brightness = dim_step_pct
                        self.call_service("light/turn_on", entity_id = dev, brightness_pct = brightness)
        

class Doorbell(hass.Hass):

    def initialize(self):
        self.utils = self.get_app("utils")
        self.click_type = self.args["click_type"]
        self.gw_mac = self.args["gw_mac"]
        self.ringtone_id = self.args["ringtone_id"]
        self.vol_slider = self.args["vol_slider"]
        self.flash = self.args["flash"] if "flash" in self.args else None
        self.courtesy_light = self.args["courtesy_light"] if "courtesy_light" in self.args else None
        self.gh_devices = self.args["gh_devices"] if "gh_devices" in self.args else None

        for button in self.args["buttons"]:
            self.listen_event(self.cb_doorbell, "xiaomi_aqara.click",
                              entity_id = button)
        
        self.listen_state(self.doorbell_slider_change, self.vol_slider)

    def cb_doorbell(self, event_name, data, kwargs):

        event_click = data["click_type"]
        button = kwargs["entity_id"]
        
        if event_click != self.click_type:
            return
        self.log(f"{button}: {self.click_type}")    

        if self.courtesy_light and self.sun_down():
            self.turn_on(self.courtesy_light["entity_id"])
            self.start_timer()

        if self.anyone_home():
            vol = self.get_state(self.vol_slider)
            vol = float(vol)
            self.call_service("xiaomi_aqara/play_ringtone", 
                               gw_mac = self.gw_mac,
                               ringtone_id = self.ringtone_id,
                               ringtone_vol = vol)
        
        if self.flash:
            lights = self.flash
            for x in lights: ###### this needs to be reviewed ###########
                self.call_service("light/lifx_effect_pulse", 
                                    entity_id = x, 
                                    brightness = "255", color_name = "green", 
                                    period = "0.5", cycles = "10")

        if self.gh_devices and self.anyone_home():
            msg = ("There's someone at the door")
            for gh in self.gh_devices:
                if self.get_state(gh) == "off": 
                    self.call_service("tts/google_say", entity_id = gh,
                                      message = msg)
                    break

        t = time.strftime("%d-%b-%Y %H:%M:%S")
        message = f"{t}: Doorbell pressed"
        self.log(message)
        self.notify(message, name = "html5")

    def start_timer(self):
        timer = self.courtesy_light["timer"] if "timer" in self.courtesy_light else 60
        self.handle = self.run_in(self.end_timer, timer)

    def end_timer(self, kwargs):
        self.turn_off(self.courtesy_light["entity_id"])
    
    def doorbell_slider_change(self, entity, attribute, old, new, kwargs):
        vol = float(new)
        self.call_service("xiaomi_aqara/play_ringtone", 
                            gw_mac = self.gw_mac,
                            ringtone_id = self.ringtone_id, 
                            ringtone_vol = vol)
        