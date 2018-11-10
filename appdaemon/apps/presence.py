import appdaemon.plugins.hass.hassapi as hass

#
# Presence App
#
# Args:
#   devices_on: devices to turn on when someone arrives home
#   devices_off: devices to turn off when everyones left home
#   pet_light: light to leave on at night when no ones home


class Presence(hass.Hass):

    def initialize(self):
        self.listen_state(self.someones_arrived, "group.all_devices", new = "home")
        self.listen_state(self.everyones_left, "group.all_devices", old = "home")
        self.run_at_sunset(self.sunset_cb, offset = -30 * 60)


    def someones_arrived(self, entity, attribute, old, new, kwargs):
        self.log("*** Someone's Arrived ***")

        if self.now_is_between("sunset - 00:30:00", "sunrise + 00:10:00"):

            for device in self.args["devices_on"]:
                if device == "light.1_kitchen":
                    self.log(f"Turning on {device}")
                    self.turn_on(device, brightness_pct = "100", kelvin = "3500")

                # turn on harmony only for Nick or Ash
                elif device == "switch.template_harmony_fetch":
                    if self.get_tracker_state("device_tracker.nicks_note8") == "home" or self.get_tracker_state("device_tracker.ashs_s8_plus") == "home":
                        self.log(f"Turning on {device}")
                        self.turn_on(device) 

                else:
                    self.log(f"Turning on {device}")
                    self.turn_on(device)
        
        # turn off radio
        self.log("Turning off {}".format(self.args["radio_device"]))
        self.turn_off(self.args["radio_device"]) 
        # turn off hallway 2 after 15 minutes
        self.run_in(self.delayed_action, 1 * 60)


    def everyones_left(self, entity, attribute, old, new, kwargs):
        self.log("*** Everyone's Left ***")
        
        for device in self.args["devices_off"]:
            self.log(f"Turning off {device}")
            self.turn_off(device)

        # turn on news on google home office
        self.log("Streaming {} on {}".format(self.args["radio_url"], self.args["radio_device"]))
        self.call_service("media_player/play_media", entity_id = self.args["radio_device"], media_content_id = self.args["radio_url"], media_content_type = "music")

        # leave pet light on at night
        if self.now_is_between("sunset - 00:30:00", "sunrise"):
            self.log("Turning on {}".format(self.args["pet_light"]))
            self.turn_on(self.args["pet_light"], transition = "15")


    def sunset_cb(self, kwargs):
        if self.get_state("input_boolean.holiday_mode") == "on":
            return
            
        if self.noone_home():
            self.log("Turning on {}".format(self.args["pet_light"]))
            self.turn_on(self.args["pet_light"], brightness_pct = "60", kelvin = "3200", transition = "120")
        else:
            for device in self.args["devices_on"]:
                d1, d2 = self.split_entity(device)
                if d1 in ["light", "switch"] and d2 != "template_harmony_fetch":
                    self.log(f"Turning on {device}")
                    self.turn_on(device)
            

    def delayed_action(self, kwargs):
        self.log("Turning off {}".format(self.args["pet_light"]))
        self.turn_off(self.args["pet_light"])