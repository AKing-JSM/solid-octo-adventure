"""
config.py — All tunable game constants live here.
Change any value to tweak gameplay without touching game logic.
"""

# ──────────────────────────────────────────────
# Display
# ──────────────────────────────────────────────
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60
TITLE = "BOLO — Tank Combat"

# ──────────────────────────────────────────────
# Map / tiles
# ──────────────────────────────────────────────
TILE_SIZE = 32  # pixels per tile

# Terrain codes used in the map grid
GRASS = 0
WATER = 1
WALL = 2
TREE = 3
ROAD = 4

# Terrain colours (R, G, B)
TERRAIN_COLORS = {
    GRASS: (34, 139, 34),     # forest green
    WATER: (30, 100, 200),    # blue
    WALL:  (120, 120, 120),   # grey
    TREE:  (0, 100, 0),       # dark green
    ROAD:  (160, 140, 100),   # tan
}

# Which terrain types block tank movement?
TERRAIN_BLOCKS_MOVEMENT = {WALL, WATER}

# Which terrain types block bullets?
TERRAIN_BLOCKS_BULLETS = {WALL}

# Slow-down factor when driving through trees (1.0 = normal)
TREE_SPEED_FACTOR = 0.5

# ──────────────────────────────────────────────
# Tank
# ──────────────────────────────────────────────
TANK_SPEED = 3.0          # pixels per frame at full throttle
TANK_ROTATION_SPEED = 4.0 # degrees per frame
TANK_SIZE = 22            # bounding-box half-width in pixels
TANK_MAX_HEALTH = 100
TANK_ARMOR = 0.5          # damage multiplier (lower = tougher)
TANK_RESPAWN_TIME = 3.0   # seconds before respawn
TANK_COLOR = (50, 180, 50)          # player tank body colour
TANK_TURRET_COLOR = (30, 130, 30)   # player turret colour
TANK_ENEMY_COLOR = (200, 50, 50)    # (reserved for future multiplayer)

# ──────────────────────────────────────────────
# Bullets
# ──────────────────────────────────────────────
BULLET_SPEED = 8.0
BULLET_DAMAGE = 25
BULLET_RADIUS = 3
BULLET_MAX_RANGE = 500    # pixels before bullet disappears
BULLET_RELOAD_TIME = 0.4  # seconds between shots
BULLET_COLOR = (255, 255, 100)

# ──────────────────────────────────────────────
# Pillboxes (AI turrets)
# ──────────────────────────────────────────────
PILLBOX_RANGE = 250       # detection / firing range in pixels
PILLBOX_FIRE_RATE = 1.2   # seconds between shots
PILLBOX_HEALTH = 80
PILLBOX_DAMAGE = 15
PILLBOX_BULLET_SPEED = 6.0
PILLBOX_COLOR = (180, 100, 30)
PILLBOX_HOSTILE_COLOR = (200, 50, 50)
PILLBOX_FRIENDLY_COLOR = (50, 50, 200)
PILLBOX_SIZE = 12

# ──────────────────────────────────────────────
# Bases
# ──────────────────────────────────────────────
BASE_CAPTURE_RANGE = 48   # pixels — how close the tank must be
BASE_CAPTURE_TIME = 3.0   # seconds to fully capture
BASE_SIZE = 20
BASE_NEUTRAL_COLOR = (200, 200, 200)
BASE_PLAYER_COLOR = (80, 80, 255)
BASE_ENEMY_COLOR = (255, 80, 80)

# ──────────────────────────────────────────────
# HUD / UI
# ──────────────────────────────────────────────
HUD_HEIGHT = 40
HUD_BG = (20, 20, 20)
HUD_TEXT_COLOR = (220, 220, 220)
HEALTH_BAR_WIDTH = 200
HEALTH_BAR_HEIGHT = 16

# ──────────────────────────────────────────────
# Colours (misc)
# ──────────────────────────────────────────────
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
