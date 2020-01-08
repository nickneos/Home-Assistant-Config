import appdaemon.plugins.hass.hassapi as hass
import random
import datetime

class Sunset(hass.Hass):
    """
    Sunset App
    Args:
        devices_on: devices to turn on when someone arrives home
        devices_off: devices to turn off when everyones left home
        pet_light: light to leave on at night when no ones home
    """

    def initialize(self):
        self.utils = self.get_app("utils")
        self.handle1 = None
        self.handle2 = None
        self.athome_on = self.args["athome_on"] if "athome_on" in self.args else []
        self.away_on = self.args["away_on"] if "away_on" in self.args else []

        self.run_at_sunset(self.sunset_cb, offset = -30 * 60)

    def sunset_cb(self, kwargs):
        """Sunset Callback Function"""
        self.log("sunset callback triggered")
       
        if self.utils.is_on("input_boolean.holiday_mode"):
            self.run_in(self.holiday_mode, 1, stage = 0)
        else:
            devices = self.away_on if self.noone_home() else self.athome_on
            for dev in devices:
                self.utils.on(dev)

    def holiday_mode(self, kwargs):
        """
        Callback function for holiday mode:
        Simulates house presence by turning on and off different set
        of lights 
        """
        if kwargs["stage"] == 0:
            self.log(
                "Holiday Mode is activated...beginning holiday algorithm")

            # Turn on Hallway 2 Light
            dev = "light.hallway_2"
            # self.turn_on(dev, brightness_pct = "60", kelvin = "3200", 
            #              transition = "120")
            self.utils.on(dev)

            # Generate stage 1 start time
            s_delay = random.randint(15*60, 120*60)
            run_at_1 = self.datetime() + datetime.timedelta(seconds = s_delay)
            self.log(f"Random datetime generated for stage 1: {run_at_1}")

            # Generate stage 2 start time
            basetime = datetime.datetime.combine(self.date(), 
                                                 datetime.time(21, 5))
            s_delay = random.randint(30*60, 180*60)
            run_at_2 = basetime + datetime.timedelta(seconds = s_delay)
            self.log(f"Random datetime generated for stage 2: {run_at_2}")
            
            # Schedulers for stage 1 and stage 2
            self.handle1 = self.run_at(self.holiday_mode, run_at_1, stage = 1)
            self.handle2 = self.run_at(self.holiday_mode, run_at_2, stage = 2)

        elif kwargs["stage"] == 1:
            # Stage 1: turn on some family area lights
            devs = ["light.kitchen", "light.floor_lamp"]
            for dev in devs:
                self.utils.on(dev)
            self.handle1 = None
        
        elif kwargs["stage"] == 2:
            # Stage 2

            # If stage 2 is triggered before stage 1 then cancel stage 1 timer
            if self.handle1 != None: 
                self.log(
                    f"Canceling self.handle1: {self.info_timer(self.handle1)}")
                self.cancel_timer(self.handle1)

            # Turn off all lights
            dev = "group.all_lights"
            self.utils.off(dev)

            # Generate Stage 3 delay and schedule
            s_delay = random.randint(10, 60)
            self.log(f"Random delay generated for stage 3: {s_delay} seconds")
            self.run_in(self.holiday_mode, s_delay, stage = 3)
        
        elif kwargs["stage"] == 3: 
            # Stage 3
            
            # Turn on bedroom light
            self.utils.on("light.bedroom")

            # Generage Stage 4 delay and schedule
            s_delay = random.randint(5*60, 20*60)
            self.log(f"Random delay generated for stage 4: {s_delay} seconds")
            self.run_in(self.holiday_mode, s_delay, stage = 4)
        
        elif kwargs["stage"] == 4:
            # Stage 4: Turn off all lights
            self.utils.off("group.all_lights")


class Fairylights(hass.Hass):

    def initialize(self):
        self.utils = self.get_app("utils")
        self.lights = self.args["lights"] if "lights" in self.args else []
        delta1 = self.args["sunrise_offset"] if "sunrise_offset" in self.args else 0
        delta2 = self.args["sunset_offset"] if "sunset_offset" in self.args else 0

        self.run_at_sunrise(self.sunrise_cb, offset = delta1 * 60)
        self.run_at_sunset(self.sunset_cb, offset = delta2 * 60)

    def sunrise_cb(self, kwargs):
        for x in self.lights:
            self.utils.off(x)

    def sunset_cb(self, kwargs):
        for x in self.lights:
            self.utils.on(x)