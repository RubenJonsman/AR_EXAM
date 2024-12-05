class IRsignal:
    def __init__(self, node):
        self.role = "Seeker"
        self.node = node
        self.tx_signal = 0
        self.rx_signal = 0

    def set_ir_signal(self, signal):
        self.tx_signal = signal



avoider_program = """
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

seeker_program = """
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