led_blue = """
# Keep the LED on continuously


# Initial state - set LEDs immediately
call leds.top(0,0,32)  # Blue
call leds.bottom.left(0,0,32)
call leds.bottom.right(0,0,32)
"""

led_green = """
# Keep the LED on continuously


# Initial state - set LEDs immediately
call leds.top(0,32,0)  # Green
call leds.bottom.left(0,32,0)
call leds.bottom.right(0,32,0)
"""

led_red = """
# Keep the LED on continuously


# Initial state - set LEDs immediately
call leds.top(32,0,0)  # Red
call leds.bottom.left(32,0,0)
call leds.bottom.right(32,0,0)
"""

def change_color(node, color):
    """
    Change the color of the LED
    Parameters:
    - node: the node representing the Thymio
    - color: the color to change to
    """
    if color == "blue":
        return node.compile(led_blue)
    elif color == "green":
        return node.compile(led_blue)
    elif color == "red":
        return node.compile(led_blue)
    else:
        return None