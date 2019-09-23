import appdaemon.plugins.hass.hassapi as hass
import time

class sensor_light(hass.Hass):

    def initialize(self):
        self.handle = None
        self.utils = self.get_app("utils")
        self.light = self.args["light"]
        self.sensor = self.args["sensor"]
        self.duration = self.args["duration"]
        self.night_mode = self.args["night_mode"] if "night_mode" in self.args else False
        self.brightness = self.args["brightness"] if "brightness" in self.args else None
        self.kelvin = self.args["kelvin"] if "kelvin" in self.args else None
        self.toggle = self.args["toggle"] if "toggle" in self.args else None
        s_type = self.get_state(self.sensor, attribute="device_class")

        if s_type == "garage":
            self.trigger = "open" 
        else:
            self.trigger = "on"

        self.listen_state(self.cb_motion, self.sensor, new = self.trigger)

    def cb_motion(self, entity, attribute, old, new, kwargs):
        
        if self.night_mode and self.sun_up():
            return
        
        if self.toggle:
            if self.get_state(self.toggle) == "off":
                return
    
        self.log(f"{self.sensor} tripped...Turning on {self.light}")
        if self.brightness and self.kelvin:
            self.turn_on(self.light, brightness_pct = self.brightness, kelvin = self.kelvin)
        elif self.brightness:
            self.turn_on(self.light, brightness_pct = self.brightness)
        elif self.kelvin:
            self.turn_on(self.light, kelvin = self.kelvin)
        else:
            self.turn_on(self.light)
        self.start_timer()

    def start_timer(self):
        if self.handle != None:
            self.cancel_timer(self.handle)
        
        self.log(f"{self.light} set to turn off in {self.duration} seconds")
        self.handle = self.run_in(self.end_timer, self.duration)

    def end_timer(self, kwargs):
        
        if self.get_state(self.sensor) == self.trigger:
            self.log(f"{self.sensor} still tripped...starting new delay")
            self.start_timer()
        else:
            self.log(f"Turning off {self.light}")
            self.turn_off(self.light)


class Notifications(hass.Hass):

    def initialize(self):
        self.utils = self.get_app("utils")
        
        sensors = []
        sensors.extend(self.args["motion_sensors"])
        sensors.extend(self.args["door_sensors"])
        sensors.extend(self.args["water_sensors"])

        for sensor in sensors:
            s_name = self.get_state(sensor, attribute="friendly_name")
            s_type = self.get_state(sensor, attribute="device_class")

            self.listen_state(self.cb_alarm_trigger, sensor, new = "on",
                                sensor_name = s_name, sensor_type = s_type)  
    
    def cb_alarm_trigger(self, entity, attribute, old, new, kwargs):
        t = time.strftime("%d-%b-%Y %H:%M:%S")
        sensor_name = kwargs["sensor_name"]
        sensor_type = kwargs["sensor_type"]
        
        if self.utils.noone_home() and self.get_state("input_boolean.motion_notifications") == "on":
                
            if sensor_type == "motion":
                msg = f"{t}: {sensor_name} sensor tripped".title()
                msg = msg.replace("Sensor Sensor", "Sensor")
            elif sensor_type == "door":
                msg = f"{t}: {sensor_name} opened"

            self.notify(msg, name = "html5")
        
        if sensor_type == "moisture":
            subject = f"{sensor_name} sensor leak detected".title()
            subject = subject.replace("Sensor Sensor", "Sensor")
            msg = f"{t}: {subject}"

            self.notify(msg, name = "html5")
            self.notify(msg, name = "gmail", title = subject)

