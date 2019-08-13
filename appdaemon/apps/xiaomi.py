import appdaemon.plugins.hass.hassapi as hass
import time

class Button(hass.Hass):

    def initialize(self):
        
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
        tgt_dev = action["target_dev"] if "target_dev" in action else None

        if button_type == "standard":
            device, entity = self.split_entity(tgt_dev)
            service = action["service"] 
            self.call_service(f"{device}/{service}", entity_id = tgt_dev)
        
        elif button_type == "dimmer":
            if self.get_state(tgt_dev) == "off":
                self.call_service("light/turn_on", entity_id = tgt_dev)
            else:
                dim_step = action["dim_step"] if "dim_step" in action else 3
                dim_step_pct = round(100 / dim_step)
                brightness = round((self.get_state(tgt_dev, attribute = "brightness") / 255) * 100)
                brightness = brightness + dim_step_pct
                if brightness > 100:
                    brightness = dim_step_pct
                self.call_service("light/turn_on", entity_id = tgt_dev, brightness_pct = brightness)
        
        elif button_type == "doorbell":
            self.doorbell(action)


    def doorbell(self, data):

        if self.sun_down():
            self.turn_on(data["light"])
            self.start_timer()

        if self.anyone_home():
            self.call_service("xiaomi_aqara/play_ringtone", 
                               gw_mac = data["gw_mac"],
                               ringtone_id = data["ringtone_id"], ringtone_vol = data["volume"])
        
        lights = data["flash"]
        for x in lights:
            self.call_service("light/lifx_effect_pulse", 
                                entity_id = x, 
                                brightness = "255", color_name = "green", 
                                period = "0.5", cycles = "10")

        # if self.anyone_home():
        #     # devices = ["media_player.google_home_main", 
        #     #            "media_player.google_home_bedroom",
        #     #            "media_player.google_home_office"]
        #     # msg = ("There's someone at the door")
        #     # for gh in devices:
        #     #     if self.get_state(gh) == "off": 
        #     #         self.call_service("tts/google_say", entity_id = gh,
        #     #                           message = msg)
        #     #         break

        t = time.strftime("%d-%b-%Y %H:%M:%S")
        message = f"{t}: Doorbell pressed"
        self.log(message)
        self.notify(message, name = "html5")


    def start_timer(self):        
        self.handle = self.run_in(self.end_timer, 180)

    def end_timer(self, kwargs):
        self.turn_off(self.light)