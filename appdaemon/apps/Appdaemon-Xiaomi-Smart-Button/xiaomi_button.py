"""
Customise what happens when you press a Xiaomi Wireless Button
https://github.com/so3n/Appdaemon-Xiaomi-Smart-Button
"""

import appdaemon.plugins.hass.hassapi as hass

# default values
DEFAULT_ACTION_TYPE = "toggle"
DEFAULT_CLICK_TYPE = "single"
DEFAULT_DIM_STEP_VALUE = 3

ACTION_TYPE_OPTIONS = [
    "turn_on",
    "turn_off",
    "toggle",
    "dim_step"
]

class Button(hass.Hass):

    def initialize(self):
        self.buttons = self.args.get("buttons", [])
        self.actions = self.args.get("actions", [])
        
        if type(self.buttons) is not list:
            self.buttons = [self.buttons]

        for button in self.buttons:
            self.listen_event(self.cb_button_press, "xiaomi_aqara.click",
                              entity_id = button)

    def cb_button_press(self, event_name, data, kwargs):
        """ Callback function when button is pressed """

        event_click = data["click_type"]
        button = kwargs["entity_id"]
        
        for action in self.actions:
            click_type = action.get("click_type", DEFAULT_CLICK_TYPE)
            if event_click == click_type:
                self.log(f"{button}: {action}")
                self.perform_action(action)
                break

    def perform_action(self, action):
        """ Perform action based on the type of the action """

        action_type = action.get("action_type", DEFAULT_ACTION_TYPE)
        dim_step_value = action.get("dim_step_value", DEFAULT_DIM_STEP_VALUE)
        tgt_devs = action.get("target_device", [])

        if action_type not in ACTION_TYPE_OPTIONS:
            self.log("Action Type not valid option")
            return

        if type(tgt_devs) is not list:
            tgt_devs = [tgt_devs]

        for device in tgt_devs:
            if action_type == "turn_on":
                self.turn_on_action(device)
            elif action_type == "turn_off":
                self.turn_off_action(device)
            elif action_type == "toggle":
                self.toggle_action(device)
            elif action_type == "dim_step":
                self.dim_action(device, dim_step_value)

    def turn_on_action(self, device):
        """ turns on device """

        if device == "lights":
            for entity_id in self.get_state('light'):
                if self.get_state(entity_id) == "off":
                    self.turn_on(entity_id)
            return
            
        if self.get_state(device) == "on":
            self.log(f"{device} already on")
            return

        self.log(f"Turning on {device}")
        self.turn_on(device)

    def turn_off_action(self, device):
        """ turns off device """

        if device == "lights":
            for entity_id in self.get_state('light'):
                if self.get_state(entity_id) == "on":
                    self.turn_off(entity_id)
            return
            
        if self.get_state(device) == "off":
            self.log(f"{device} already off")
            return

        self.log(f"Turning off {device}")
        self.turn_off(device)

    def toggle_action(self, device):
        """ toggles device """

        self.log(f"Toggle {device}")
        self.toggle(device)
    
    def dim_action(self, light, dim_step):
        """ increments brightness of light """
        
        if self.get_state(light) == "off":
            self.call_service("light/turn_on", entity_id = light)
        else:
            dim_step_pct = round(100 / dim_step)
            brightness = self.get_state(light, attribute = "brightness")
            if brightness:
                brightness = self.bound_to_100(brightness)
                brightness = brightness + dim_step_pct
                if brightness > 100:
                    brightness = dim_step_pct
                self.call_service("light/turn_on", entity_id = light, brightness_pct = brightness)


    def bound_to_100(self, number):
        """
        Convert HomeAssistant-usable brightness level to something that is
        human readable
        """
        return round(int(float(number)) / 255 * 100)
