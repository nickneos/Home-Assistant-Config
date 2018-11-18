import appdaemon.plugins.hass.hassapi as hass
import random
import datetime

#
# Sunset App
#
# Args:
#   devices_on: devices to turn on when someone arrives home
#   devices_off: devices to turn off when everyones left home
#   pet_light: light to leave on at night when no ones home


class Sunset(hass.Hass):

    def initialize(self):
        self.handle1 = None
        self.run_at_sunset(self.sunset_cb, offset = -30 * 60)


    def sunset_cb(self, kwargs):
        self.log("sunset callback triggered")

        if self.noone_home() and self.get_state("input_boolean.holiday_mode") != "on":
            self.log("Turning on {}".format(self.args["pet_light"]))
            self.turn_on(self.args["pet_light"], brightness_pct = "60", kelvin = "3200", transition = "120")

        elif self.anyone_home() and self.get_state("input_boolean.holiday_mode") != "on":
            for device in self.args["devices_on"]:
                self.log(f"Turning on {device}")
                self.turn_on(device)

        elif self.get_state("input_boolean.holiday_mode") == "on":
            dev = "light.hallway_2"
            self.log("Holiday Mode is activated...beginning holiday algorithm")
            self.log(f"Turning on {dev}")
            self.turn_on(dev, brightness_pct = "60", kelvin = "3200", transition = "120")

            sec_delay = random.randint(15*60, 180*60)  # between 15 to 180 minutes
            runtime = self.datetime() + datetime.timedelta(seconds = sec_delay)
            self.handle1 = self.run_at(self.holiday_mode, runtime, mode = 1)
        
            sec_delay = random.randint(15*60, 180*60)  # between 15 to 180 minutes
            runtime = datetime.time(21, 5) + datetime.timedelta(seconds = sec_delay)
            self.run_at(self.holiday_mode, runtime, mode = 2)


    def holiday_mode(self, kwargs):
        
        if kwargs["mode"] == 1:
            devs = ["light.1_kitchen", "switch.arlec_2a"]
            for dev in devs:
                self.log(f"Turning on {dev}")
                self.turn_on(dev)
            self.handle1 = None
        
        elif kwargs["mode"] == 2:
            if self.handle1 != None: 
                self.cancel_timer(self.handle1)
            self.turn_off("switch.house_lights")
            self.run_in(self.holiday_mode, random.randint(10, 60), mode = 3)
        
        elif kwargs["mode"] == 3:
            self.turn_on("light.bedroom")
            self.run_in(self.holiday_mode, random.randint(5*60, 20*60), mode = 4)
        
        elif kwargs["mode"] == 4:
            self.turn_off("switch.house_lights")


