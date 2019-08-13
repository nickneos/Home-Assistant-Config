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
        # listeners for group.all_devices - home and not_home
        self.listen_state(self.someones_arrived, "group.all_devices", new = "home", duration = 6)
        self.listen_state(self.everyones_left, "group.all_devices", old = "home", duration = 60)
        
        # listeners for specific people - home and not_home
        for tracker in self.args["people_notifications"]:
            self.log("Setting up people-notification listener for {}".format(tracker))
            self.listen_state(self.people_notification, tracker)

        # trackers = self.get_trackers()
        # for tracker in trackers:
        #     self.log("{}: {}".format(self.get_state(tracker, attribute="friendly_name"), self.get_state(tracker)))
 

    def someones_arrived(self, entity, attribute, old, new, kwargs):
        self.log("*** Someone's Arrived ***")
        
        # devices to turn on
        for device in self.args["arrival_on"]:
            if device == "light.kitchen" and self.now_is_between("sunset - 00:30:00", "sunrise + 00:10:00"):
                self.log(f"Turning on {device}")
                self.turn_on(device, brightness_pct = "100", kelvin = "3500")

            elif device != "switch.template_harmony_fetch" and self.now_is_between("sunset - 00:30:00", "sunrise + 00:10:00"):
                self.log(f"Turning on {device}")
                self.turn_on(device)
            
            # turn on harmony only for Nick or Ash
            elif device == "switch.template_harmony_fetch":
                if self.get_tracker_state("device_tracker.nicks_note8") == "home" or self.get_tracker_state("device_tracker.ashs_s10") == "home":
                    self.log(f"Turning on {device}")
                    self.turn_on(device) 

        # turn off radio
        self.log("Turning off {}".format(self.args["radio_device"]))
        self.turn_off(self.args["radio_device"]) 
        # self.cancel_listen_state(self.radio_handle)

        # turn off pet light after 15 minutes if its on
        pet_light = self.args["pet_light"]
        if self.get_state(pet_light) == "on":
            n = 15
            self.log(f"Turning off {pet_light} in {n} minutes")
            self.run_in(self.delayed_action, n * 60)
        

    def everyones_left(self, entity, attribute, old, new, kwargs):
        self.log("*** Everyone's Left ***")
        
        # devices to turn off
        for device in self.args["away_off"]:
            self.log(f"Turning off {device}")
            self.turn_off(device)

        # turn on news on google home office
        self.log("Streaming {} on {}".format(self.args["radio_url"], self.args["radio_device"]))
        self.call_service("media_player/play_media", entity_id = self.args["radio_device"], media_content_id = self.args["radio_url"], media_content_type = "music")
        # radio_handle = self.listen_state(self.gh_keep_alive, self.args["radio_device"], old = "playing", duration = 300)

        # leave pet light on at night
        if self.now_is_between("sunset - 00:30:00", "sunrise"):
            self.log("Turning on {}".format(self.args["pet_light"]))
            self.turn_on(self.args["pet_light"], transition = "15")


    def delayed_action(self, kwargs):
        self.log("Turning off {}".format(self.args["pet_light"]))
        self.turn_off(self.args["pet_light"])


    def people_notification(self, entity, attribute, old, new, kwargs):
        if new == "home":
            message = "{}: {} arrived".format(time.strftime("%d-%b-%Y %H:%M:%S"), self.get_state(entity, attribute="friendly_name"))
        elif old == "home":
            message = "{}: {} left".format(time.strftime("%d-%b-%Y %H:%M:%S"), self.get_state(entity, attribute="friendly_name"))
        else:
            return
        
        self.notify(message, name = "html5")

    # def gh_keep_alive(self, entity, attribute, old, new, kwargs):
    #     self.log("Stream ended...")
    #     self.log("Resuming stream {} on {}".format(self.args["radio_url"], self.args["radio_device"]))
    #     self.call_service("media_player/play_media", entity_id = self.args["radio_device"], media_content_id = self.args["radio_url"], media_content_type = "music")
