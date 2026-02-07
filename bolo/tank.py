"""
tank.py — Player tank: movement, rotation, aiming, drawing, and health.

The tank uses momentum-style movement: pressing a direction accelerates
the tank, and releasing lets it coast to a stop.  The turret always
points toward the mouse cursor.
"""

import math
import pygame
from bolo.config import (
    TANK_SPEED, TANK_ROTATION_SPEED, TANK_SIZE, TANK_MAX_HEALTH,
    TANK_ARMOR, TANK_RESPAWN_TIME, TANK_COLOR, TANK_TURRET_COLOR,
    TILE_SIZE, TREE_SPEED_FACTOR, FPS,
)


class Tank:
    """Player-controlled tank."""

    def __init__(self, x, y, game_map):
        # Position (centre of the tank, in pixels)
        self.x = float(x)
        self.y = float(y)

        # Velocity components
        self.vx = 0.0
        self.vy = 0.0

        # Body angle (degrees, 0 = right, counter-clockwise positive)
        self.body_angle = -90.0  # start facing up

        # Turret angle — always faces the mouse
        self.turret_angle = -90.0

        # Health
        self.health = TANK_MAX_HEALTH
        self.alive = True

        # Respawn
        self._respawn_timer = 0.0
        self._spawn_x = x
        self._spawn_y = y

        # Reference to the map for collision checks
        self.map = game_map

        # Stats
        self.kills = 0
        self.deaths = 0
        self.bases_captured = 0

    # ── update ───────────────────────────────────────────────────────
    def update(self, keys, mouse_pos, camera_x, camera_y):
        """Called once per frame. Handles input, physics, and collisions."""
        if not self.alive:
            self._respawn_timer -= 1.0 / FPS
            if self._respawn_timer <= 0:
                self.respawn()
            return

        self._handle_movement(keys)
        self._apply_physics()
        self._aim_turret(mouse_pos, camera_x, camera_y)

    # ── movement / input ─────────────────────────────────────────────
    def _handle_movement(self, keys):
        """Read WASD / arrow keys and set velocity."""
        dx, dy = 0.0, 0.0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1

        # Normalise diagonal movement so it isn't faster.
        length = math.hypot(dx, dy)
        if length > 0:
            dx /= length
            dy /= length

            # Rotate body toward the movement direction
            target_angle = math.degrees(math.atan2(-dy, dx))
            self.body_angle = _lerp_angle(self.body_angle, target_angle,
                                          TANK_ROTATION_SPEED)

        # Speed modifier for trees
        speed = TANK_SPEED
        if self.map.is_tree(self.x, self.y):
            speed *= TREE_SPEED_FACTOR

        self.vx = dx * speed
        self.vy = dy * speed

    def _apply_physics(self):
        """Move the tank and slide along walls."""
        # Try X then Y separately so the tank slides along obstacles.
        new_x = self.x + self.vx
        half = TANK_SIZE // 2
        test_rect = pygame.Rect(new_x - half, self.y - half,
                                TANK_SIZE, TANK_SIZE)
        if not self.map.rect_blocked(test_rect):
            self.x = new_x

        new_y = self.y + self.vy
        test_rect = pygame.Rect(self.x - half, new_y - half,
                                TANK_SIZE, TANK_SIZE)
        if not self.map.rect_blocked(test_rect):
            self.y = new_y

    # ── turret aiming ────────────────────────────────────────────────
    def _aim_turret(self, mouse_pos, camera_x, camera_y):
        """Point the turret toward the mouse cursor."""
        mx, my = mouse_pos
        # Convert screen-space mouse to world-space
        world_mx = mx + camera_x
        world_my = my + camera_y
        dx = world_mx - self.x
        dy = world_my - self.y
        if dx != 0 or dy != 0:
            self.turret_angle = math.degrees(math.atan2(-dy, dx))

    # ── drawing ──────────────────────────────────────────────────────
    def draw(self, screen, camera_x, camera_y):
        """Render the tank body + turret."""
        if not self.alive:
            return

        sx = self.x - camera_x
        sy = self.y - camera_y
        half = TANK_SIZE // 2

        # --- body (rotated rectangle) ---
        body_surf = pygame.Surface((TANK_SIZE, TANK_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(body_surf, TANK_COLOR, (0, 0, TANK_SIZE, TANK_SIZE),
                         border_radius=4)
        # Track marks
        pygame.draw.rect(body_surf, (40, 140, 40), (0, 0, TANK_SIZE, 4))
        pygame.draw.rect(body_surf, (40, 140, 40),
                         (0, TANK_SIZE - 4, TANK_SIZE, 4))

        rotated = pygame.transform.rotate(body_surf, self.body_angle)
        rect = rotated.get_rect(center=(sx, sy))
        screen.blit(rotated, rect)

        # --- turret (line + circle) ---
        turret_len = half + 6
        end_x = sx + math.cos(math.radians(self.turret_angle)) * turret_len
        end_y = sy - math.sin(math.radians(self.turret_angle)) * turret_len
        pygame.draw.line(screen, TANK_TURRET_COLOR, (sx, sy),
                         (end_x, end_y), 4)
        pygame.draw.circle(screen, TANK_TURRET_COLOR, (int(sx), int(sy)), 6)

    # ── damage / death / respawn ─────────────────────────────────────
    def take_damage(self, amount):
        """Apply damage (reduced by armor). Returns True if tank dies."""
        if not self.alive:
            return False
        self.health -= int(amount * TANK_ARMOR)
        if self.health <= 0:
            self.health = 0
            self.die()
            return True
        return False

    def die(self):
        self.alive = False
        self.deaths += 1
        self._respawn_timer = TANK_RESPAWN_TIME

    def respawn(self):
        self.x = float(self._spawn_x)
        self.y = float(self._spawn_y)
        self.vx = 0
        self.vy = 0
        self.health = TANK_MAX_HEALTH
        self.alive = True

    # ── helpers ──────────────────────────────────────────────────────
    def get_rect(self):
        half = TANK_SIZE // 2
        return pygame.Rect(self.x - half, self.y - half,
                           TANK_SIZE, TANK_SIZE)

    def get_turret_tip(self):
        """World-space position of the barrel tip (bullet spawn point)."""
        turret_len = TANK_SIZE // 2 + 8
        tx = self.x + math.cos(math.radians(self.turret_angle)) * turret_len
        ty = self.y - math.sin(math.radians(self.turret_angle)) * turret_len
        return tx, ty


# ── utility ──────────────────────────────────────────────────────────
def _lerp_angle(current, target, speed):
    """Smoothly rotate *current* toward *target* by up to *speed* degrees."""
    diff = (target - current + 180) % 360 - 180
    if abs(diff) < speed:
        return target
    return current + math.copysign(speed, diff)
