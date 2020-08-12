# import appdaemon.appapi as appapi
import appdaemon.plugins.hass.hassapi as hass
import json
from datetime import datetime, timedelta

#
# App to localize frequently used functions
#
# Args: (set these in appdaemon.cfg)
# n/a
#
# EXAMPLE appdaemon.cfg entry below...
#         ... and of how to make utils initialize before other apps 
#         get the chance to
# 
# # Apps
# 
# [utils]
# module = utils
# class = utils
#
# [hello_world]
# module = hello_world
# class = HelloWorld
# dependencies = utils
#
# class HelloWorld(appapi.AppDaemon):
#     def initialize(self):
#         self.utils = self.get_app('utils')
#         self.log('Tomorrow is {}'.format(self.utils.tomorrow())
#

class utils(hass.Hass):
    def initialize(self):
        pass

    def ten_minutes_from_now(self):
        """
        Return datetime.datetime object +10 minutes from current internal 
        AppDaemon clock
        """
        return self.datetime() + timedelta(minutes=10)

    def tomorrow(self):
        """
        Return datetime.date object +1 day from current internal AppDaemon 
        clock
        """
        return self.date() + timedelta(days=1)

    def all_on_lights(self):
        """
        Return list of entity_ids for all lights that are currently on
        """
        all_lights = self.get_state('light')
        all_on_lights = []
        
        for light in all_lights:
            state = self.get_state(light)
            if state == 'on':
                all_on_lights.append(light)

        return all_on_lights

    def get_max_brightness(self):
        """
        Return the maximum brightness value of all lights that are currently on
        """
        all_lights = self.get_state('light')
        max_brightness = []

        for light in all_lights:
            brightness = self.get_state(light, attribute='brightness')
            if brightness is not None:
                max_brightness.append(brightness)

        return max(max_brightness)

    def bound_to_255(self, number):
        """
        Convert percentage-bound rightness to something that is usable for
        HomeAssistant
        """
        return round(int(float(number)) * 255 / 100)

    def bound_to_100(self, number):
        """
        Convert HomeAssistant-usable brightness level to something that is
        human readable
        """
        return round(int(float(number)) / 255 * 100)

    def soon(self, seconds=None, minutes=None, hours=None):
        """
        Return datetime.datetime object for some time in the future from 
        current internal AppDaemon clock. 

        Keyword arguments:
        hours -- hours in the fturue (default None)
        minutes -- minutes in the future (default None)
        seconds -- seconds in the future (default 5)
        """
        if not seconds:
            seconds = 5
        if not minutes:
            minutes = 0
        if not hours:
            hours = 0

        return self.datetime() + timedelta(seconds=seconds, 
                                           minutes=minutes, 
                                           hours=hours)

    def run_every_weekday(self, callback, start, **kwargs):
        """
        Execute a callback at the same time every day of traditional work week. 
        If today is a work day and the time has already passed, the function 
        will not be invoked until the following work day at the specified time.

        Keyword arguments:
        callback -- Function to be invoked when the requested state change 
                    occurs. It must conform to the standard Scheduler Callback 
                    format documented at https://goo.gl/EBtPDx.
        
        start -- A Python time object that specifies when the callback will 
                 occur. If the time specified is in the past, the callback will 
                 occur the next day at the specified time.

        **kwargs -- Arbitary keyword parameters to be provided to the callback
                    function when it is invoked.
        """
        WEEKDAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        handle = []
        upcoming_weekdays = []

        today = self.date()
        todays_event = datetime.combine(today, start)

        if todays_event > self.datetime():
            if today.strftime('%A') in WEEKDAYS:
                upcoming_weekdays.append(today)

        for day_number in range(1, 8):
            day = today + timedelta(days=day_number)
            if day.strftime('%A') in WEEKDAYS:
                if len(upcoming_weekdays) < 5:
                    upcoming_weekdays.append(day)

        for day in upcoming_weekdays:
            event = datetime.combine(day, start)
            handle.append(self.run_every(callback, event, 604800, **kwargs))

        return handle

    def run_every_weekend_day(self, callback, start, **kwargs):
        """
        Execute a callback at the same time every day outside of the 
        traditional work week. If today is a weekend day and the time has 
        already passed, the function  will not be invoked until the following 
        weekend day at the specified time.

        Keyword arguments:
        callback -- Function to be invoked when the requested state change 
                    occurs. It must conform to the standard Scheduler Callback 
                    format documented at https://goo.gl/EBtPDx.
        
        start -- A Python time object that specifies when the callback will 
                 occur. If the time specified is in the past, the callback will 
                 occur the next day at the specified time.

        **kwargs -- Arbitary keyword parameters to be provided to the callback
                    function when it is invoked.
        """
        WEEKEND_DAYS = ['Saturday', 'Sunday']
        handle = []
        upcoming_weekend_days = []

        today = self.date()
        todays_event = datetime.combine(today, start)

        if todays_event > self.datetime():
            if today.strftime('%A') in WEEKEND_DAYS:
               upcoming_weekend_days.append(today)

        for day_number in range(1, 8):
            day = today + timedelta(days=day_number)
            if day.strftime('%A') in WEEKEND_DAYS:
                if len(upcoming_weekend_days) < 2:
                    upcoming_weekend_days.append(day)

        for day in upcoming_weekend_days:
            event = datetime.combine(day, start)
            handle.append(self.run_every(callback, event, 604800, **kwargs))

        return handle

    def cancel_multiday_timer(self, handle):
        """
        Cancel a previously created weekday or weekend timer
        """
        for thing in handle:
            try:
                for timer in thing:
                    self.cancel_timer(timer)
            except TypeError:
                self.cancel_timer(thing)
    
    def on(self, device):
        """
        """
        if self.get_state(device) == "on":
            self.log(f"{device} already on")
            return

        self.log(f"Turning on {device}")
        self.turn_on(device)

    def off(self, device):
        """
        """
        if self.get_state(device) == "off":
            self.log(f"{device} already off")
            return

        self.log(f"Turning off {device}")
        self.turn_off(device)

    def my_toggle(self, device):
        """
        """
        self.log(f"Toggle {device}")
        self.toggle(device)


    def anyone_home(self):
        """
        """
        people = self.get_state("person")
        for p in people:
            if self.get_state(p) == "home":
                return True
        return False

    def noone_home(self):
        """
        """
        people = self.get_state("person")
        for p in people:
            if self.get_state(p) == "home":
                return False
        return True
    
    def is_on(self, device):
        """
        """
        if self.get_state(device) == "on":
            return True
        else:
            return False

    def is_off(self, device):
        """
        """
        if self.get_state(device) == "off":
            return True
        else:
            return False

    def tripped_name(self, device):
        s_type = self.get_state(device, attribute="device_class")

        if s_type == "garage":
            return "open" 
        else:
            return "on"

    def is_tripped(self, device):
        """
        """
        s_type = self.get_state(device, attribute="device_class")
        
        if s_type == "garage":
            trip = "open" 
        else:
            trip = "on"

        if self.get_state(device) == trip:
            return True
        else:
            return False

    def get_sec(self, hhmmss):
        """
        Get Seconds from time.
        """
        h, m, s = hhmmss.split(':')
        return int(h) * 3600 + int(m) * 60 + int(s)
    
    def to_list(self, x):
        """
        convert variable to list if not list
        """
        return x if type(x) is list else [x]
    
    def flash_bulb(self, dev, sec):
        """
        """
        self.turn_on(dev, flash = "long")
        self.run_in(self.cb_delayed_off, sec, device = dev)

    def cb_delayed_off(self, kwargs):
        """
        """
        dev = kwargs["device"]
        self.turn_off(dev)

    def turn_off_all_lights(self):
        """ turns off all lights """

        self.call_service("light/turn_off", entity_id = "all")
