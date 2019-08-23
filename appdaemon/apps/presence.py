import appdaemon.plugins.hass.hassapi as hass
import time

#
# Presence App
#
# Args:
#   arrival_on: devices to turn on when someone arrives home
#   away_off: devices to turn off when everyones left home
#   pet_light: light to leave on at night when no ones home


class Presence(hass.Hass):

    def initialize(self):

        self.arrival_on = self.args["arrival_on"] if "arrival_on" in self.args else []
        self.away_off = self.args["away_off"] if "away_off" in self.args else []
        self.pet_light = self.args["pet_light"] if "pet_light" in self.args else None
        self.radio = self.args["radio"] if "radio" in self.args else None
        self.people_notifications = self.args["people_notifications"] if "people_notifications" in self.args else []

        # listeners for group.all_devices - home and not_home
        self.listen_state(self.someones_arrived, "group.all_devices", new = "home", duration = 6)
        self.listen_state(self.everyones_left, "group.all_devices", old = "home", duration = 60)
        
        # listeners for specific people - home and not_home
        for tracker in self.people_notifications:
            self.log("Setting up people-notification listener for {}".format(tracker))
            self.listen_state(self.people_notification, tracker)


    def someones_arrived(self, entity, attribute, old, new, kwargs):

        if self.get_state("input_boolean.people_automations") == "off":
            return
        
        self.log("*** Someone's Arrived ***")
        is_night = self.now_is_between("sunset - 00:30:00", "sunrise + 00:10:00")

        # devices to turn on
        for device in self.arrival_on:
            platform, dev = self.split_entity(device)

            if platform == "light" and is_night:
                self.log(f"Turning on {device}")
                if device == "light.kitchen":
                    self.turn_on(device, brightness_pct = "100", kelvin = "3500")
                else:
                    self.turn_on(device)
            
            # turn on harmony only for Nick or Ash
            elif device == "switch.template_harmony_fetch":
                if self.get_tracker_state("device_tracker.nicks_note8") == "home" or self.get_tracker_state("device_tracker.ashs_s10") == "home":
                    self.log(f"Turning on {device}")
                    self.turn_on(device) 
            
            else:
                self.log(f"Turning on {device}")
                self.turn_on(device) 

        # turn off radio
        if self.radio:
            r_dev = self.radio["device"]
            self.log(f"Turning off {r_dev}")
            self.turn_off(r_dev) 

        # turn off pet light after 15 minutes if its on
        if self.pet_light:
            if self.get_state(self.pet_light) == "on":
                n = 15
                self.log(f"Turning off {self.pet_light} in {n} minutes")
                self.run_in(self.delayed_off, n * 60, device = self.pet_light)
        

    def everyones_left(self, entity, attribute, old, new, kwargs):

        if self.get_state("input_boolean.people_automations") == "off":
            return
        
        self.log("*** Everyone's Left ***")
        is_night = self.now_is_between("sunset - 00:30:00", "sunrise + 00:10:00")
        
        
        # devices to turn off
        for device in self.away_off:
            self.log(f"Turning off {device}")
            self.turn_off(device)

        # turn on news on google home office
        if self.radio:
            r_dev = self.radio["device"]
            r_url = self.radio["url"]
            self.log(f"Streaming {r_url} on {r_dev}")
            self.call_service("media_player/play_media", entity_id = r_dev, media_content_id = r_url, media_content_type = "music")

        # leave pet light on at night
        if self.pet_light and is_night:
            self.log(f"Turning on {self.pet_light}")
            self.turn_on(self.pet_light, transition = "15")


    def delayed_off(self, kwargs):
        dev = kwargs["device"]
        self.log(f"Turning off {dev}")
        self.turn_off(dev)


    def people_notification(self, entity, attribute, old, new, kwargs):
        if new == "home":
            message = "{}: {} arrived".format(time.strftime("%d-%b-%Y %H:%M:%S"), self.get_state(entity, attribute="friendly_name"))
        elif old == "home":
            message = "{}: {} left".format(time.strftime("%d-%b-%Y %H:%M:%S"), self.get_state(entity, attribute="friendly_name"))
        else:
            return
        
        self.notify(message, name = "html5")
