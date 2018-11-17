import appdaemon.plugins.hass.hassapi as hass
import random

#
# Sunset App
#
# Args:
#   devices_on: devices to turn on when someone arrives home
#   devices_off: devices to turn off when everyones left home
#   pet_light: light to leave on at night when no ones home


class Sunset(hass.Hass):

    def initialize(self):
        self.run_at_sunset(self.sunset_cb, offset = -30 * 60)


    def sunset_cb(self, kwargs):
        self.log("sunset callback triggered")

        if self.get_state("input_boolean.holiday_mode") == "on" and self.noone_home():
            self.log("Holiday Mode is activated...beginning holiday algorithm")
            self.turn_on("light.hallway_2", brightness_pct = "60", kelvin = "3200", transition = "120")
            sec_delay = random.randint(15*60, 180*60)  # between 15 to 180 minutes
            # self.run_in(self.holiday_mode, 1)
            return
        elif self.noone_home():
            self.log("Turning on {}".format(self.args["pet_light"]))
            self.turn_on(self.args["pet_light"], brightness_pct = "60", kelvin = "3200", transition = "120")
        else:
            for device in self.args["devices_on"]:
                self.log(f"Turning on {device}")
                self.turn_on(device)
    
