"""
base.py — Capturable bases.

A base starts neutral. When a player tank stays within capture range
for long enough, the base is captured and changes colour. Capturing
all bases (or the most) wins the game.
"""

import math
import pygame
from bolo.config import (
    BASE_CAPTURE_RANGE, BASE_CAPTURE_TIME, BASE_SIZE,
    BASE_NEUTRAL_COLOR, BASE_PLAYER_COLOR, BASE_ENEMY_COLOR,
    FPS, WHITE,
)


class Base:
    """A capturable point on the map."""

    NEUTRAL = 0
    PLAYER = 1
    ENEMY = 2

    def __init__(self, x, y, owner=None):
        self.x = float(x)
        self.y = float(y)
        self.owner = owner if owner is not None else self.NEUTRAL

        # Capture progress: 0.0 → BASE_CAPTURE_TIME = fully captured
        self.capture_progress = 0.0

    def update(self, player_tank):
        """
        If the living player is in range, advance capture progress.
        If they leave, the progress resets over time.
        """
        if not player_tank.alive:
            # Slowly decay progress when player is dead
            self.capture_progress = max(0, self.capture_progress - 0.5 / FPS)
            return

        if self.owner == self.PLAYER:
            return  # already captured

        dx = player_tank.x - self.x
        dy = player_tank.y - self.y
        dist = math.hypot(dx, dy)

        if dist <= BASE_CAPTURE_RANGE:
            self.capture_progress += 1.0 / FPS
            if self.capture_progress >= BASE_CAPTURE_TIME:
                self.owner = self.PLAYER
                self.capture_progress = BASE_CAPTURE_TIME
                player_tank.bases_captured += 1
        else:
            # Slowly decay when out of range
            self.capture_progress = max(0, self.capture_progress - 0.5 / FPS)

    def draw(self, screen, camera_x, camera_y):
        sx = int(self.x - camera_x)
        sy = int(self.y - camera_y)

        # Pick colour based on owner
        if self.owner == self.PLAYER:
            color = BASE_PLAYER_COLOR
        elif self.owner == self.ENEMY:
            color = BASE_ENEMY_COLOR
        else:
            color = BASE_NEUTRAL_COLOR

        # Outer diamond shape
        points = [
            (sx, sy - BASE_SIZE),
            (sx + BASE_SIZE, sy),
            (sx, sy + BASE_SIZE),
            (sx - BASE_SIZE, sy),
        ]
        pygame.draw.polygon(screen, color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)

        # Flag/symbol in centre
        pygame.draw.circle(screen, WHITE, (sx, sy), 5)
        if self.owner == self.PLAYER:
            pygame.draw.circle(screen, BASE_PLAYER_COLOR, (sx, sy), 3)
        elif self.owner == self.ENEMY:
            pygame.draw.circle(screen, BASE_ENEMY_COLOR, (sx, sy), 3)

        # Capture progress ring (shown only while capturing)
        if self.owner != self.PLAYER and self.capture_progress > 0:
            frac = self.capture_progress / BASE_CAPTURE_TIME
            arc_angle = frac * 360
            if arc_angle > 0:
                pygame.draw.arc(screen, (255, 255, 100),
                                (sx - BASE_SIZE - 4, sy - BASE_SIZE - 4,
                                 (BASE_SIZE + 4) * 2, (BASE_SIZE + 4) * 2),
                                math.radians(90),
                                math.radians(90 + arc_angle), 3)
