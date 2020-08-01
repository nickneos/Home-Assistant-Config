"""
Automations based on people presence
"""

import appdaemon.plugins.hass.hassapi as hass
import time

# default values
DEFAULT_DEBOUNCE = 5

class Presence(hass.Hass):

    def initialize(self):
        self.utils = self.get_app("utils")
        self.arrival_on = self.args.get("arrival_on", [])
        self.arrival_off = self.args.get("arrival_off", [])
        self.away_on = self.args.get("away_on", [])
        self.away_off = self.args.get("away_off", [])
        self.radio = self.args.get("radio")
        self.people_notifications = self.args.get("people_notifications", [])
        self.residents = self.args.get("residents", [])

        self.flg_noone_home = self.noone_home(person=True)
        self.flg_anyone_home = self.anyone_home(person=True)
        self.log(f"No One Home: {self.flg_noone_home} | Anyone Home: {self.flg_anyone_home}")

        debounce = self.args.get("debounce", [])
        duration_h = debounce.get("home", DEFAULT_DEBOUNCE)
        duration_nh = debounce.get("not_home", DEFAULT_DEBOUNCE)

        # listeners for device trackers - home and not_home
        self.listen_state(self.cb_home, "person", old='not_home', new="home", duration=duration_h)
        self.listen_state(self.cb_not_home, "person", old="home", new="not_home", duration=duration_nh)
        
        # listeners for specific people - home and not_home
        for i in self.people_notifications:
            self.log("Setting up people-notification listener for {}".format(i))
            self.listen_state(self.people_notification, i)

    def cb_home(self, entity, attribute, old, new, kwargs):

        self.log(f"{entity} home")

        if self.get_state("input_boolean.people_automations") == "off":
            return

        if self.flg_anyone_home:
            self.log("Not running cb_home as someone was already home")
            return
            
        is_night = self.now_is_between("sunset - 00:30:00", "sunrise + 00:10:00")
        self.flg_noone_home = self.noone_home(person=True)
        self.flg_anyone_home = self.anyone_home(person=True)
        self.log(f"No One Home: {self.flg_noone_home} | Anyone Home: {self.flg_anyone_home}")

        # devices to turn off
        for device in self.arrival_off:
            if device == "lights":
                self.utils.turn_off_all_lights()
            elif device.startswith("light."):
                n = 5
                self.log(f"Turning off {device} in {n} minutes")
                self.run_in(self.utils.cb_delayed_off, n * 60, device = device)
            else:
                self.utils.off(device) 

        # turn off radio
        if self.radio:
            r_dev = self.radio["device"]
            self.utils.off(r_dev)

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
            elif d1 == "remote":
                for i in self.residents:
                    if self.get_tracker_state(i) == "home":
                        self.utils.on(device)
                        break
            else:
                self.utils.on(device)
                

    def cb_not_home(self, entity, attribute, old, new, kwargs):
        
        self.log(f"{entity} not_home")

        if self.get_state("input_boolean.people_automations") == "off":
            return
        
        if self.anyone_home(person=True):
            self.log("Not running cb_not_home as there is someone home")
            return

        is_night = self.now_is_between("sunset - 00:30:00", "sunrise + 00:10:00")
        self.flg_noone_home = self.noone_home(person=True)
        self.flg_anyone_home = self.anyone_home(person=True)
        self.log(f"No One Home: {self.flg_noone_home} | Anyone Home: {self.flg_anyone_home}")      
        
        # devices to turn off
        for device in self.away_off:
            if device == "lights":
                self.utils.turn_off_all_lights()
            else:
                self.utils.off(device)

        # turn on news on google home office
        if self.radio:
            r_dev = self.radio["device"]
            r_url = self.radio["url"]
            self.log(f"Streaming {r_url} on {r_dev}")
            self.call_service("media_player/play_media", entity_id = r_dev, media_content_id = r_url, media_content_type = "music")

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


    def people_notification(self, entity, attribute, old, new, kwargs):
        if new == "home":
            message = "{}: {} arrived".format(time.strftime("%d-%b-%Y %H:%M:%S"), self.get_state(entity, attribute="friendly_name"))
        elif old == "home":
            message = "{}: {} left".format(time.strftime("%d-%b-%Y %H:%M:%S"), self.get_state(entity, attribute="friendly_name"))
        else:
            return
        
        self.notify(message, name = "html5")
