import appdaemon.plugins.hass.hassapi as hass
import time

#
# Presence App
#

class Presence(hass.Hass):

    def initialize(self):

        self.arrival_on = self.args["arrival_on"] if "arrival_on" in self.args else []
        self.arrival_off = self.args["arrival_off"] if "arrival_off" in self.args else []
        self.away_on = self.args["away_on"] if "away_on" in self.args else []
        self.away_off = self.args["away_off"] if "away_off" in self.args else []
        self.radio = self.args["radio"] if "radio" in self.args else None
        self.people_notifications = self.args["people_notifications"] if "people_notifications" in self.args else []
        self.residents = self.args["residents"] if "residents" in self.args else []

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
            d1, d2 = self.split_entity(device)
            # turn on lights at night
            if d1 == "light": 
                # skip to next loop item if daytime
                if not is_night:
                    self.log(f"Not turning on {device} as daytime")
                    continue
                self.log(f"Turning on {device}")
                if device == "light.kitchen":
                    self.turn_on(device, brightness_pct = "100", kelvin = "3500")
                else:
                    self.turn_on(device)
            # turn on harmony only for Nick or Ash
            elif device == "switch.template_harmony_fetch":
                for person in self.residents:
                    if self.get_tracker_state(person) == "home":
                        self.log(f"Turning on {device}")
                        self.turn_on(device)
                        break
            else:
                self.log(f"Turning on {device}")
                self.turn_on(device)

        # devices to turn off
        for device in self.arrival_off:
            d1, d2 = self.split_entity(device)
            if d1 == "light":
                n = 5
                self.log(f"Turning off {device} in {n} minutes")
                self.run_in(self.delayed_off, n * 60, device = device)
            else:
                self.log(f"Turning off {device}")
                self.turn_off(device) 

        # turn off radio
        if self.radio:
            r_dev = self.radio["device"]
            self.log(f"Turning off {r_dev}")
            self.turn_off(r_dev) 
        

    def everyones_left(self, entity, attribute, old, new, kwargs):

        if self.get_state("input_boolean.people_automations") == "off":
            return
        
        self.log("*** Everyone's Left ***")
        is_night = self.now_is_between("sunset - 00:30:00", "sunrise + 00:10:00")
        
        
        # devices to turn off
        for device in self.away_off:
            self.log(f"Turning off {device}")
            self.turn_off(device)

        # devices to turn on
        for device in self.away_on:
            d1, d2 = self.split_entity(device)
            if d1 == "light":
                if not is_night:
                    continue
                self.log(f"Turning on {device}")
                self.turn_on(device)
            else:
                self.log(f"Turning on {device}")
                self.turn_on(device)

        # turn on news on google home office
        if self.radio:
            r_dev = self.radio["device"]
            r_url = self.radio["url"]
            self.log(f"Streaming {r_url} on {r_dev}")
            self.call_service("media_player/play_media", entity_id = r_dev, media_content_id = r_url, media_content_type = "music")


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
