from constants import SEEKER


def get_avoider_ir_program(color):
    r, g, b = color
    return f"""
# Variables must be at start
var send_interval = 200  # time in milliseconds
var signal_detected = 0  # For storing received signal
var reset_delay = 500   # Reset after 500ms

# Enable communication first
call prox.comm.enable(1)

# Initialize timer
timer.period[0] = send_interval

# Set constant transmission
onevent timer0
    prox.comm.tx = 2  # Continuously send 2
    call leds.top({r}, {g}, {b})
    call leds.bottom.left({r}, {g}, {b})
    call leds.bottom.right({r}, {g}, {b})

# Force update rx value in every timer tick
    if prox.comm.rx == 0 then
        signal_detected = 0
    end

onevent prox.comm
    signal_detected = prox.comm.rx
    if signal_detected != 0 then
        timer.period[1] = reset_delay
    end

onevent timer1
    prox.comm.rx = 0  # Force reset rx
    signal_detected = 0
    timer.period[1] = 0
"""


def get_seeker_ir_program(color):
    r, g, b = color
    return f"""
# Variables must be at start
var send_interval = 200  # time in milliseconds
var signal_detected = 0  # For storing received signal
var reset_delay = 500   # Reset after 500ms

# Enable communication first
call prox.comm.enable(1)


# Initialize timer
timer.period[0] = send_interval

# Set constant transmission
onevent timer0
    prox.comm.tx = 1 # Continuously send 1
    call leds.top({r}, {g}, {b})
    call leds.bottom.left({r}, {g}, {b})
    call leds.bottom.right({r}, {g}, {b})

# Force update rx value in every timer tick
    if prox.comm.rx == 0 then
        signal_detected = 0
    end

onevent prox.comm
    signal_detected = prox.comm.rx
    if signal_detected != 0 then
        timer.period[1] = reset_delay
    end

onevent timer1
    prox.comm.rx = 0  # Force reset rx
    signal_detected = 0
    timer.period[1] = 0
"""


class IRsignal:
    def __init__(self, node, robot_type):
        self.robot_type = robot_type
        self.node = node

    async def initialize_thymio(self, color):
        program = (
            get_seeker_ir_program(color)
            if self.robot_type == SEEKER
            else get_avoider_ir_program(color)
        )
        try:
            error = await self.node.compile(program)
            if error is not None:
                print(f"Compilation error: {error['error_msg']}")
            await self.node.run()
        except Exception as e:
            print(f"Error initializing IR signal: {e}")

    async def compile_from_state_and_type(self, state, type):
        pass
        # led_program =

    async def get_ir_signal(self):
        self.node.flush()
        value = self.node.v.prox.comm.rx
        return value
