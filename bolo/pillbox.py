"""
pillbox.py — AI-controlled defensive turrets.

Pillboxes sit at fixed positions and automatically fire at the player
when the player is within range. They can be destroyed, and in a future
version they could be captured.
"""

import math
import pygame
from bolo.config import (
    PILLBOX_RANGE, PILLBOX_FIRE_RATE, PILLBOX_HEALTH, PILLBOX_DAMAGE,
    PILLBOX_BULLET_SPEED, PILLBOX_HOSTILE_COLOR, PILLBOX_FRIENDLY_COLOR,
    PILLBOX_SIZE, FPS, BULLET_COLOR,
)
from bolo.bullet import Bullet


class Pillbox:
    """A stationary AI turret."""

    # owner constants
    NEUTRAL = 0
    HOSTILE = 1
    FRIENDLY = 2

    def __init__(self, x, y, owner=None):
        """
        Parameters
        ----------
        x, y  : centre position in world pixels
        owner : NEUTRAL / HOSTILE / FRIENDLY (default HOSTILE)
        """
        self.x = float(x)
        self.y = float(y)
        self.owner = owner if owner is not None else self.HOSTILE
        self.health = PILLBOX_HEALTH
        self.alive = True
        self._fire_cooldown = 0.0      # seconds until next shot
        self.turret_angle = 0.0        # current aiming direction (degrees)

    def update(self, player_tank, bullets_list):
        """
        Each frame: check distance to player, aim, and fire.
        Only hostile pillboxes fire at the player.
        """
        if not self.alive:
            return

        # Tick cooldown
        if self._fire_cooldown > 0:
            self._fire_cooldown -= 1.0 / FPS

        if self.owner != self.HOSTILE:
            return  # friendly / neutral pillboxes don't shoot

        if not player_tank.alive:
            return

        dx = player_tank.x - self.x
        dy = player_tank.y - self.y
        dist = math.hypot(dx, dy)

        if dist > PILLBOX_RANGE:
            return

        # Aim at the player
        self.turret_angle = math.degrees(math.atan2(-dy, dx))

        # Fire if cooldown expired
        if self._fire_cooldown <= 0:
            self._fire(bullets_list)
            self._fire_cooldown = PILLBOX_FIRE_RATE

    def _fire(self, bullets_list):
        """Spawn a bullet aimed at the player."""
        bx = self.x + math.cos(math.radians(self.turret_angle)) * (PILLBOX_SIZE + 4)
        by = self.y - math.sin(math.radians(self.turret_angle)) * (PILLBOX_SIZE + 4)
        b = Bullet(bx, by, self.turret_angle, owner=self,
                   speed=PILLBOX_BULLET_SPEED, damage=PILLBOX_DAMAGE,
                   color=(255, 120, 50))
        bullets_list.append(b)

    def take_damage(self, amount):
        if not self.alive:
            return
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.alive = False

    def draw(self, screen, camera_x, camera_y):
        if not self.alive:
            # Draw rubble
            sx = int(self.x - camera_x)
            sy = int(self.y - camera_y)
            pygame.draw.circle(screen, (80, 70, 60), (sx, sy), PILLBOX_SIZE // 2)
            return

        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        color = (PILLBOX_FRIENDLY_COLOR if self.owner == self.FRIENDLY
                 else PILLBOX_HOSTILE_COLOR)

        # Base
        pygame.draw.rect(screen, color,
                         (sx - PILLBOX_SIZE, sy - PILLBOX_SIZE,
                          PILLBOX_SIZE * 2, PILLBOX_SIZE * 2),
                         border_radius=3)
        # Inner circle
        pygame.draw.circle(screen, (60, 60, 60), (sx, sy), PILLBOX_SIZE - 3)
        # Gun barrel
        barrel_len = PILLBOX_SIZE + 4
        ex = sx + math.cos(math.radians(self.turret_angle)) * barrel_len
        ey = sy - math.sin(math.radians(self.turret_angle)) * barrel_len
        pygame.draw.line(screen, (200, 200, 200), (sx, sy), (ex, ey), 3)

        # Health bar above
        bar_w = PILLBOX_SIZE * 2
        bar_h = 3
        frac = self.health / PILLBOX_HEALTH
        pygame.draw.rect(screen, (80, 0, 0),
                         (sx - PILLBOX_SIZE, sy - PILLBOX_SIZE - 6, bar_w, bar_h))
        pygame.draw.rect(screen, (0, 200, 0),
                         (sx - PILLBOX_SIZE, sy - PILLBOX_SIZE - 6,
                          int(bar_w * frac), bar_h))
