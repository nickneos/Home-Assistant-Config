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
        self.handle2 = None
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
            self.run_in(self.holiday_mode, 1, stage = 0)



    def holiday_mode(self, kwargs):
        
        if kwargs["stage"] == 0:
            self.log("Holiday Mode is activated...beginning holiday algorithm")

            # Turn on Hallway 2 Light
            dev = "light.hallway_2"
            self.log(f"Turning on {dev}")
            self.turn_on(dev, brightness_pct = "60", kelvin = "3200", transition = "120")

            # Generate stage 1 start time
            s_delay = random.randint(15*60, 120*60)
            run_at_1 = self.datetime() + datetime.timedelta(seconds = s_delay)
            self.log(f"Random datetime generated for stage 1: {run_at_1}")

            # Generate stage 2 start time
            basetime = datetime.datetime.combine(self.date(), datetime.time(21, 5))
            s_delay = random.randint(30*60, 180*60)
            run_at_2 = basetime + datetime.timedelta(seconds = s_delay)
            self.log(f"Random datetime generated for stage 2: {run_at_2}")
            
            # Schedulers for stage 1 and stage 2
            self.handle1 = self.run_at(self.holiday_mode, run_at_1, stage = 1)
            self.handle2 = self.run_at(self.holiday_mode, run_at_2, stage = 2)

        elif kwargs["stage"] == 1:
            # Stage 1: turn on some family area lights
            devs = ["light.1_kitchen", "switch.arlec_2a"]
            for dev in devs:
                self.log(f"Turning on {dev}")
                self.turn_on(dev)
            self.handle1 = None
        
        elif kwargs["stage"] == 2:
            # Stage 2

            # If stage 2 is triggered before stage 1 then cancel stage 1 timer
            if self.handle1 != None: 
                self.log(f"Canceling self.handle1: {self.info_timer(self.handle1)}")
                self.cancel_timer(self.handle1)

            # Turn off all lights
            dev = "switch.house_lights"
            self.log(f"Turning off {dev}")
            self.turn_off(dev)

            # Generate Stage 3 delay and schedule
            s_delay = random.randint(10, 60)
            self.log(f"Random delay generated for stage 3: {s_delay} seconds")
            self.run_in(self.holiday_mode, s_delay, stage = 3)
        
        elif kwargs["stage"] == 3: 
            # Stage 3
            
            # Turn on bedroom light
            self.turn_on("light.bedroom")

            # Generage Stage 4 delay and schedule
            s_delay = random.randint(5*60, 20*60)
            self.log(f"Random delay generated for stage 4: {s_delay} seconds")
            self.run_in(self.holiday_mode, s_delay, stage = 4)
        
        elif kwargs["stage"] == 4:
            # Stage 4: Turn off all lights
            self.turn_off("switch.house_lights")


