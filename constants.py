V_MAX = 10
MAX_WHEEL_SPEED = 5000
USE_VISUALIZATION = True
DRAW_LIDAR = True
DRAW_PARTICLES = True
DRAW_ROBOT = True

WIDTH = 1200
HEIGHT = 800
PADDING = 50

BEAM_LENGTH = 300
BEAM_COUNT = 3

AXLE_LENGTH = 10
WHEEL_RADIUS = 2.2
IMG_PATH = 'thymio_small.png'
GRID_SIZE = 20
NUM_PARTICLES = 200
NOISE_FACTOR = 0.01

AVOIDER = 0
SEEKER = 1

CAMERA_RANGE = 300

# STATE CONSTANTS
DEFAULT_STATE = 0
SAFE_STATE = 1
CAUGHT_STATE = 2

# COLORS FOR ROBOT STATES
AVOIDER_COLOR = (30, 144, 255) # BLUE
CAUHGT_AVOIDER_COLOR = (138, 43, 226) # PURPLE
SAFE_AVOIDER_COLOR = (50, 205, 50) # GREEN

SEEKER_COLOR = (220, 20, 60) # RED
SAFE_SEEKER_COLOR = (255, 140, 0) # ORANGE

# STATE COLOR MAP
STATE_COLOR_MAP = {
    (AVOIDER, DEFAULT_STATE): AVOIDER_COLOR,
    (AVOIDER, SAFE_STATE): SAFE_AVOIDER_COLOR,
    (AVOIDER, CAUGHT_STATE): CAUHGT_AVOIDER_COLOR,

    (SEEKER, DEFAULT_STATE): SEEKER_COLOR,
    (SEEKER, SAFE_STATE): SAFE_SEEKER_COLOR
}

GREY_DANGER_ZONE=0
SILVER_SAFE_ZONE=1
BLACK_WALL_ZONE=2
