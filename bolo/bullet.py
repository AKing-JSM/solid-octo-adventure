"""
bullet.py — Projectiles fired by tanks and pillboxes.

Bullets travel in a straight line and are destroyed when they hit
a wall, leave the map, or exceed their maximum range.
"""

import math
import pygame
from bolo.config import (
    BULLET_SPEED, BULLET_DAMAGE, BULLET_RADIUS,
    BULLET_MAX_RANGE, BULLET_COLOR,
)


class Bullet:
    """A single projectile."""

    def __init__(self, x, y, angle_deg, owner, speed=None, damage=None,
                 color=None):
        """
        Parameters
        ----------
        x, y       : spawn position (world pixels)
        angle_deg  : direction in degrees (0 = right, CCW positive)
        owner      : reference to the object that fired (tank / pillbox)
        speed      : override default bullet speed
        damage     : override default damage
        color      : override default colour
        """
        self.x = float(x)
        self.y = float(y)
        rad = math.radians(angle_deg)
        spd = speed if speed is not None else BULLET_SPEED
        self.vx = math.cos(rad) * spd
        self.vy = -math.sin(rad) * spd   # screen Y is flipped
        self.damage = damage if damage is not None else BULLET_DAMAGE
        self.color = color if color is not None else BULLET_COLOR
        self.owner = owner
        self.alive = True

        self._start_x = x
        self._start_y = y

    def update(self, game_map):
        """Move the bullet; mark dead if it hits a wall or travels too far."""
        self.x += self.vx
        self.y += self.vy

        # Range check
        dist = math.hypot(self.x - self._start_x, self.y - self._start_y)
        if dist > BULLET_MAX_RANGE:
            self.alive = False
            return

        # Wall collision
        if game_map.blocks_bullet(self.x, self.y):
            self.alive = False

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            return
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)
        pygame.draw.circle(screen, self.color, (sx, sy), BULLET_RADIUS)
        # Small glow/trail
        pygame.draw.circle(screen, (255, 255, 200), (sx, sy), BULLET_RADIUS + 1, 1)

    def get_rect(self):
        r = BULLET_RADIUS
        return pygame.Rect(self.x - r, self.y - r, r * 2, r * 2)
