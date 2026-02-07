"""
game_map.py — Tile-based map: loading, rendering, and collision queries.

The map is a 2-D list of terrain codes (see config.py).
A small hand-crafted default map is included; you can replace it or
load one from a file later.
"""

import pygame
from bolo.config import (
    TILE_SIZE, TERRAIN_COLORS, TERRAIN_BLOCKS_MOVEMENT,
    TERRAIN_BLOCKS_BULLETS, GRASS, WATER, WALL, TREE, ROAD,
)

# fmt: off
# Default map layout — each number is a terrain code.
# Legend: 0=grass  1=water  2=wall  3=tree  4=road
DEFAULT_MAP = [
    [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
    [2,0,0,0,0,0,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,0,0,0,0,0,0,0,2],
    [2,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,2],
    [2,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,2],
    [2,0,0,0,0,4,4,4,4,0,2,0,0,0,0,0,0,0,0,2,0,0,0,0,0,0,0,0,0,0,0,2],
    [2,0,0,0,0,4,0,0,4,0,0,0,0,0,3,3,0,0,0,0,0,0,4,4,4,4,0,0,0,0,0,2],
    [2,3,0,0,0,4,0,0,4,0,0,0,0,3,3,3,3,0,0,0,0,0,4,0,0,4,0,0,0,0,3,2],
    [2,3,3,0,0,4,4,4,4,0,0,0,0,0,3,3,0,0,0,0,0,0,4,0,0,4,0,0,0,3,3,2],
    [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,0,0,0,0,0,2],
    [2,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
    [2,0,0,0,2,2,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,2],
    [2,0,0,0,2,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,2,0,0,0,0,0,2],
    [2,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
    [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,0,0,0,0,0,0,0,2],
    [2,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,2,2,0,0,0,0,0,3,0,0,0,0,0,0,2],
    [2,0,0,0,0,3,3,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,3,3,0,0,0,0,0,2],
    [2,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,2],
    [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,4,4,4,0,0,0,0,0,0,0,0,0,0,0,0,2],
    [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,2],
    [2,0,0,0,0,0,0,0,3,0,0,0,0,0,0,4,0,0,4,0,0,0,0,3,0,0,0,0,0,0,0,2],
    [2,0,0,0,0,0,0,3,3,3,0,0,0,0,0,4,4,4,4,0,0,0,3,3,3,0,0,0,0,0,0,2],
    [2,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,2],
    [2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,2],
    [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
]
# fmt: on


class GameMap:
    """Holds the tile grid and handles rendering + collision queries."""

    def __init__(self, grid=None):
        self.grid = grid if grid is not None else [row[:] for row in DEFAULT_MAP]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.width_px = self.cols * TILE_SIZE
        self.height_px = self.rows * TILE_SIZE

        # Pre-render the static map surface once for speed.
        self.surface = pygame.Surface((self.width_px, self.height_px))
        self._render_surface()

    # ── rendering ────────────────────────────────────────────────────
    def _render_surface(self):
        """Draw every tile onto the cached surface."""
        for row in range(self.rows):
            for col in range(self.cols):
                terrain = self.grid[row][col]
                color = TERRAIN_COLORS.get(terrain, TERRAIN_COLORS[GRASS])
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE,
                                   TILE_SIZE, TILE_SIZE)
                pygame.draw.rect(self.surface, color, rect)

                # Draw subtle grid lines for readability.
                pygame.draw.rect(self.surface, (0, 0, 0), rect, 1)

                # Extra decoration for specific terrain types
                if terrain == TREE:
                    self._draw_tree(col * TILE_SIZE, row * TILE_SIZE)
                elif terrain == WATER:
                    self._draw_water(col * TILE_SIZE, row * TILE_SIZE)
                elif terrain == WALL:
                    self._draw_wall(col * TILE_SIZE, row * TILE_SIZE)

    def _draw_tree(self, x, y):
        """Draw a simple tree icon on the tile."""
        cx, cy = x + TILE_SIZE // 2, y + TILE_SIZE // 2
        # Canopy
        pygame.draw.circle(self.surface, (20, 130, 20), (cx, cy - 3), 10)
        # Trunk
        pygame.draw.rect(self.surface, (100, 70, 30),
                         (cx - 2, cy + 5, 4, 8))

    def _draw_water(self, x, y):
        """Draw simple wave lines."""
        for i in range(3):
            yy = y + 8 + i * 9
            pygame.draw.line(self.surface, (80, 160, 255),
                             (x + 4, yy), (x + TILE_SIZE - 4, yy), 1)

    def _draw_wall(self, x, y):
        """Draw brick-like pattern."""
        # Horizontal mortar lines
        for i in range(1, 4):
            yy = y + i * (TILE_SIZE // 4)
            pygame.draw.line(self.surface, (90, 90, 90),
                             (x, yy), (x + TILE_SIZE, yy), 1)
        # Alternating vertical mortar
        for i in range(4):
            yy = y + i * (TILE_SIZE // 4)
            offset = TILE_SIZE // 2 if i % 2 else 0
            for vx in range(offset, TILE_SIZE, TILE_SIZE // 2):
                pygame.draw.line(self.surface, (90, 90, 90),
                                 (x + vx, yy), (x + vx, yy + TILE_SIZE // 4), 1)

    def draw(self, screen, camera_x=0, camera_y=0):
        """Blit the pre-rendered map, offset by camera position."""
        screen.blit(self.surface, (-camera_x, -camera_y))

    # ── collision helpers ────────────────────────────────────────────
    def get_terrain(self, px, py):
        """Return the terrain code at pixel position (px, py)."""
        col = int(px) // TILE_SIZE
        row = int(py) // TILE_SIZE
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return WALL  # out-of-bounds counts as wall

    def blocks_movement(self, px, py):
        """True if the pixel position is inside a movement-blocking tile."""
        return self.get_terrain(px, py) in TERRAIN_BLOCKS_MOVEMENT

    def blocks_bullet(self, px, py):
        """True if the pixel position is inside a bullet-blocking tile."""
        return self.get_terrain(px, py) in TERRAIN_BLOCKS_BULLETS

    def is_tree(self, px, py):
        """True if position is on a tree tile (slows tanks)."""
        return self.get_terrain(px, py) == TREE

    def rect_blocked(self, rect):
        """Check if any corner of a pygame.Rect is on a blocked tile."""
        corners = [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]
        return any(self.blocks_movement(x, y) for x, y in corners)

    def find_open_position(self, start_col=1, start_row=1):
        """Return pixel (x, y) centre of the first open grass tile found."""
        for row in range(start_row, self.rows):
            for col in range(start_col, self.cols):
                if self.grid[row][col] == GRASS:
                    return (col * TILE_SIZE + TILE_SIZE // 2,
                            row * TILE_SIZE + TILE_SIZE // 2)
        return (TILE_SIZE * 2, TILE_SIZE * 2)  # fallback
