import appdaemon.plugins.hass.hassapi as hass
import time

class sensor_light(hass.Hass):

    def initialize(self):
        self.handle = None
        self.counter = 0
        self.utils = self.get_app("utils")
        self.light = self.args["light"]
        self.sensor = self.args["sensor"]
        self.duration = self.args["duration"]
        self.seconds = self.utils.get_sec(self.duration)
        self.toggle = self.args["toggle"] if "toggle" in self.args else None

        tripped = self.utils.tripped_name(self.sensor)

        self.listen_state(self.cb_motion, self.sensor, new = tripped)

    def cb_motion(self, entity, attribute, old, new, kwargs):

        if self.toggle:
            if self.utils.is_off(self.toggle):
                return

        if self.counter == 0 and self.utils.is_on(self.light):
            self.log(f'{self.light} was on prior to {self.sensor} being tripped')
            return

        self.utils.on(self.light)
        self.start_timer()

    def start_timer(self):
        if self.handle != None:
            self.cancel_timer(self.handle)

        self.counter = self.counter + 1
        self.log(f"{self.light} set to turn off in {self.seconds} seconds")
        self.handle = self.run_in(self.end_timer, self.seconds)

    def end_timer(self, kwargs):

        if self.utils.is_tripped(self.sensor) and self.utils.is_on(self.light):
            self.log(f"{self.sensor} still tripped...starting new delay")
            self.start_timer()
        else:
            self.utils.off(self.light)
            self.counter = 0


class Notifications(hass.Hass):

    def initialize(self):
        self.utils = self.get_app("utils")
        self.notify_when_home = self.args["notify_when_home"] if "notify_when_home" in self.args else False
        self.duration = self.args["duration"] if "duration" in self.args else 0
        self.toggle = self.args["toggle"] if "toggle" in self.args else None

        if self.duration == 0:
            self.seconds = 0
        else:        
            self.seconds = self.utils.get_sec(self.duration)
        
        sensors = self.args["sensors"]

        for sensor in sensors:
            s_name = self.get_state(sensor, attribute="friendly_name")
            s_type = self.get_state(sensor, attribute="device_class")
            tripped = self.utils.tripped_name(sensor)

            if s_type == "garage" and self.seconds == 0:
                sec = 5
            else:
                sec = self.seconds
            
            self.listen_state(self.cb_alarm_trigger, sensor, new = tripped, 
                                duration = sec, sensor_name = s_name, 
                                sensor_type = s_type)  

    def cb_alarm_trigger(self, entity, attribute, old, new, kwargs):
        t = time.strftime("%d-%b-%Y %H:%M:%S")
        sensor_name = kwargs["sensor_name"]
        sensor_type = kwargs["sensor_type"] 

        if self.notify_when_home == False and self.anyone_home():
            return
        
        if self.toggle:
            if self.utils.is_off(self.toggle):
                return   
    
        if sensor_type == "motion":
            msg = f"{t}: {sensor_name} sensor tripped".title()
            msg = msg.replace("Sensor Sensor", "Sensor")
            self.notify(msg, name = "html5")

        elif sensor_type in ("door", "garage"):
            if self.seconds >= 60:
                duration = round(self.seconds / 60)
                msg = f"{t}: {sensor_name} has been open for {duration} minutes"
            else:
                msg = f"{t}: {sensor_name} opened"
            self.notify(msg, name = "html5")

        elif sensor_type == "moisture":
            subject = f"{sensor_name} sensor leak detected".title()
            subject = subject.replace("Sensor Sensor", "Sensor")
            msg = f"{t}: {subject}"
            self.notify(msg, name = "html5")
            self.notify(msg, name = "gmail", title = subject)

