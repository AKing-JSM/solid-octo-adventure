"""
game.py — Main game loop.  Ties together the map, tank, bullets,
pillboxes, bases, camera, and HUD.

Run with:  python -m bolo.game
"""

import sys
import math
import pygame

from bolo.config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, TILE_SIZE,
    BULLET_RELOAD_TIME, TANK_SIZE, HUD_HEIGHT,
)
from bolo.game_map import GameMap
from bolo.tank import Tank
from bolo.bullet import Bullet
from bolo.pillbox import Pillbox
from bolo.base import Base
from bolo.hud import HUD


# =====================================================================
# Explosion particles (simple eye-candy)
# =====================================================================
class Particle:
    """A tiny expanding + fading circle for explosion effects."""
    def __init__(self, x, y, vx, vy, color, life):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1

    def draw(self, screen, cx, cy):
        if self.life <= 0:
            return
        frac = self.life / self.max_life
        r = int(4 * frac) + 1
        alpha = int(255 * frac)
        color = (*self.color[:3], alpha)
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (r, r), r)
        screen.blit(surf, (int(self.x - cx - r), int(self.y - cy - r)))


def spawn_explosion(x, y, particles, count=12):
    """Create a burst of particles at (x, y)."""
    import random
    for _ in range(count):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 4)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        color = random.choice([(255, 200, 50), (255, 120, 30), (255, 80, 20)])
        life = random.randint(15, 35)
        particles.append(Particle(x, y, vx, vy, color, life))


# =====================================================================
# Camera
# =====================================================================
class Camera:
    """Simple camera that follows the player, clamped to map edges."""

    def __init__(self, map_w, map_h):
        self.x = 0.0
        self.y = 0.0
        self.map_w = map_w
        self.map_h = map_h

    def follow(self, target_x, target_y):
        # Centre the camera on the target
        self.x = target_x - SCREEN_WIDTH / 2
        self.y = target_y - SCREEN_HEIGHT / 2
        # Clamp so we don't show outside the map
        self.x = max(0, min(self.x, self.map_w - SCREEN_WIDTH))
        self.y = max(0, min(self.y, self.map_h - SCREEN_HEIGHT))


# =====================================================================
# Main game class
# =====================================================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        # Hide system cursor; we'll draw a crosshair instead
        pygame.mouse.set_visible(False)

        # Map
        self.game_map = GameMap()

        # Player tank (spawn on an open tile)
        spawn = self.game_map.find_open_position(3, 3)
        self.player = Tank(spawn[0], spawn[1], self.game_map)

        # Camera
        self.camera = Camera(self.game_map.width_px, self.game_map.height_px)

        # Bullets (shared list for player + pillbox bullets)
        self.bullets: list[Bullet] = []
        self._reload_timer = 0.0  # seconds until player can fire again

        # Particles
        self.particles: list[Particle] = []

        # Pillboxes — hand-placed on the map
        self.pillboxes = self._create_pillboxes()

        # Bases
        self.bases = self._create_bases()

        # HUD
        self.hud = HUD()

        # Track previous base-capture count for messages
        self._prev_captured = 0

    # ── entity placement ─────────────────────────────────────────────
    def _create_pillboxes(self):
        """Place pillboxes at strategic locations (tile coordinates)."""
        # (col, row) pairs — placed on grass tiles in the default map
        locations = [
            (8, 5),    # near top-left road
            (23, 7),   # near top-right road
            (15, 13),  # centre
            (7, 19),   # bottom-left trees
            (24, 19),  # bottom-right trees
        ]
        boxes = []
        for col, row in locations:
            px = col * TILE_SIZE + TILE_SIZE // 2
            py = row * TILE_SIZE + TILE_SIZE // 2
            boxes.append(Pillbox(px, py, owner=Pillbox.HOSTILE))
        return boxes

    def _create_bases(self):
        """Place capturable bases on the map."""
        locations = [
            (6, 6),    # top-left enclosure
            (24, 6),   # top-right enclosure
            (15, 10),  # centre (near water)
            (16, 18),  # bottom-centre road
            (9, 20),   # bottom-left
            (23, 20),  # bottom-right
        ]
        bases = []
        for col, row in locations:
            px = col * TILE_SIZE + TILE_SIZE // 2
            py = row * TILE_SIZE + TILE_SIZE // 2
            bases.append(Base(px, py))
        return bases

    # ── main loop ────────────────────────────────────────────────────
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0  # delta-time in seconds

            # ── events ───────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # left click
                        self._player_fire()

            # Continuous fire while mouse held
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                self._player_fire()

            keys = pygame.key.get_pressed()
            mouse_pos = pygame.mouse.get_pos()

            # ── update ───────────────────────────────────────────────
            self.player.update(keys, mouse_pos, self.camera.x, self.camera.y)
            self.camera.follow(self.player.x, self.player.y)

            # Reload timer
            if self._reload_timer > 0:
                self._reload_timer -= dt

            # Bullets
            for b in self.bullets:
                b.update(self.game_map)
            self.bullets = [b for b in self.bullets if b.alive]

            # Pillboxes
            for pb in self.pillboxes:
                pb.update(self.player, self.bullets)

            # Bases
            for base in self.bases:
                base.update(self.player)

            # Check if a new base was just captured
            captured_now = sum(1 for b in self.bases if b.owner == Base.PLAYER)
            if captured_now > self._prev_captured:
                self.hud.show_message("Base captured!", 2.0)
                if captured_now == len(self.bases):
                    self.hud.show_message("ALL BASES CAPTURED — YOU WIN!", 5.0)
            self._prev_captured = captured_now

            # Particles
            for p in self.particles:
                p.update()
            self.particles = [p for p in self.particles if p.life > 0]

            # Collision: player bullets → pillboxes
            self._check_bullet_pillbox_collisions()

            # Collision: pillbox bullets → player
            self._check_bullet_player_collisions()

            # HUD
            self.hud.update(dt)

            # ── draw ─────────────────────────────────────────────────
            self.screen.fill((0, 0, 0))
            cx, cy = self.camera.x, self.camera.y
            self.game_map.draw(self.screen, cx, cy)

            for base in self.bases:
                base.draw(self.screen, cx, cy)

            for pb in self.pillboxes:
                pb.draw(self.screen, cx, cy)

            for b in self.bullets:
                b.draw(self.screen, cx, cy)

            self.player.draw(self.screen, cx, cy)

            for p in self.particles:
                p.draw(self.screen, cx, cy)

            # Reload fraction for HUD
            reload_frac = 1.0 - max(0, self._reload_timer) / BULLET_RELOAD_TIME
            self.hud.draw(self.screen, self.player, self.bases, reload_frac)

            # Crosshair
            self._draw_crosshair(mouse_pos)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    # ── player firing ────────────────────────────────────────────────
    def _player_fire(self):
        if not self.player.alive:
            return
        if self._reload_timer > 0:
            return
        tip = self.player.get_turret_tip()
        b = Bullet(tip[0], tip[1], self.player.turret_angle, owner=self.player)
        self.bullets.append(b)
        self._reload_timer = BULLET_RELOAD_TIME

    # ── collision detection ──────────────────────────────────────────
    def _check_bullet_pillbox_collisions(self):
        """Player bullets hitting pillboxes."""
        for b in self.bullets:
            if not b.alive or b.owner is not self.player:
                continue
            for pb in self.pillboxes:
                if not pb.alive:
                    continue
                dist = math.hypot(b.x - pb.x, b.y - pb.y)
                if dist < TILE_SIZE // 2:
                    pb.take_damage(b.damage)
                    b.alive = False
                    spawn_explosion(pb.x, pb.y, self.particles, count=6)
                    if not pb.alive:
                        spawn_explosion(pb.x, pb.y, self.particles, count=20)
                        self.player.kills += 1
                        self.hud.show_message("Pillbox destroyed!", 1.5)
                    break

    def _check_bullet_player_collisions(self):
        """Pillbox bullets hitting the player."""
        if not self.player.alive:
            return
        half = TANK_SIZE // 2
        for b in self.bullets:
            if not b.alive or b.owner is self.player:
                continue
            dist = math.hypot(b.x - self.player.x, b.y - self.player.y)
            if dist < half + 2:
                died = self.player.take_damage(b.damage)
                b.alive = False
                spawn_explosion(self.player.x, self.player.y,
                                self.particles, count=4)
                if died:
                    spawn_explosion(self.player.x, self.player.y,
                                    self.particles, count=25)

    # ── crosshair ────────────────────────────────────────────────────
    def _draw_crosshair(self, pos):
        mx, my = pos
        size = 10
        gap = 4
        color = (255, 255, 255, 180)
        # Horizontal lines
        pygame.draw.line(self.screen, color, (mx - size, my), (mx - gap, my), 2)
        pygame.draw.line(self.screen, color, (mx + gap, my), (mx + size, my), 2)
        # Vertical lines
        pygame.draw.line(self.screen, color, (mx, my - size), (mx, my - gap), 2)
        pygame.draw.line(self.screen, color, (mx, my + gap), (mx, my + size), 2)
        # Centre dot
        pygame.draw.circle(self.screen, (255, 50, 50), (mx, my), 2)


# ── entry point ──────────────────────────────────────────────────────
def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
