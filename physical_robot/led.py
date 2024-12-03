class LEDHandler:
    def __init__(self, node):
        self.node = node
        self.color_dict = {"BLUE": "(0,0,32)",
                           "GREEN": "(0,32,0)",
                           "RED": "(32,0,0)",
                           "ORANGE": "(32,16,0)",
                           "PURPLE": "(32,0,32)"}
        
        
    def get_led_string(self, color):
        led_string =  f"""
        # Keep the LED on continuously
        # Initial state - set LEDs immediately
        call leds.top{self.color_dict[color]}
        call leds.bottom.left{self.color_dict[color]}
        call leds.bottom.right{self.color_dict[color]}
        """
        return led_string


    async def change_led_color(self, color):
        print(f"Setting {color.capitalize()}")
        error = await self.change_color(self.node, color)
        if error is not None:
            print(f"Compilation error: {error['error_msg']}")
            return False
        return True
    

    async def change_color(self, color):
        """
        Change the color of the LED
        Parameters:
        - node: the node representing the Thymio
        - color: the color to change to
        """            
        return await self.node.compile(self.get_led_string(color.lower()))

