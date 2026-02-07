"""
hud.py — Heads-Up Display: health bar, score, ammo indicator, messages.
"""

import pygame
from bolo.config import (
    SCREEN_WIDTH, HUD_HEIGHT, HUD_BG, HUD_TEXT_COLOR,
    HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT, TANK_MAX_HEALTH,
    RED, GREEN, YELLOW, WHITE, BASE_CAPTURE_TIME,
)


class HUD:
    """Draws the status bar at the bottom of the screen."""

    def __init__(self):
        self.font = pygame.font.SysFont("monospace", 16, bold=True)
        self.big_font = pygame.font.SysFont("monospace", 28, bold=True)
        self._message = ""
        self._message_timer = 0.0

    def show_message(self, text, duration=2.0):
        """Display a temporary centred message (e.g. 'Base captured!')."""
        self._message = text
        self._message_timer = duration

    def update(self, dt):
        if self._message_timer > 0:
            self._message_timer -= dt

    def draw(self, screen, player, bases, reload_frac):
        """
        Parameters
        ----------
        screen      : pygame display surface
        player      : Tank instance
        bases       : list of Base instances
        reload_frac : 0.0–1.0 how much of reload time has elapsed
        """
        screen_h = screen.get_height()
        bar_y = screen_h - HUD_HEIGHT

        # Background bar
        pygame.draw.rect(screen, HUD_BG, (0, bar_y, SCREEN_WIDTH, HUD_HEIGHT))
        pygame.draw.line(screen, (60, 60, 60), (0, bar_y),
                         (SCREEN_WIDTH, bar_y), 1)

        x = 10
        cy = bar_y + HUD_HEIGHT // 2

        # ── Health ──────────────────────────────────────────────────
        label = self.font.render("HP", True, HUD_TEXT_COLOR)
        screen.blit(label, (x, cy - label.get_height() // 2))
        x += label.get_width() + 6

        # Bar background
        pygame.draw.rect(screen, (60, 20, 20),
                         (x, cy - HEALTH_BAR_HEIGHT // 2,
                          HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT))
        # Bar fill
        frac = max(0, player.health / TANK_MAX_HEALTH)
        bar_color = GREEN if frac > 0.5 else YELLOW if frac > 0.25 else RED
        pygame.draw.rect(screen, bar_color,
                         (x, cy - HEALTH_BAR_HEIGHT // 2,
                          int(HEALTH_BAR_WIDTH * frac), HEALTH_BAR_HEIGHT))
        pygame.draw.rect(screen, WHITE,
                         (x, cy - HEALTH_BAR_HEIGHT // 2,
                          HEALTH_BAR_WIDTH, HEALTH_BAR_HEIGHT), 1)
        x += HEALTH_BAR_WIDTH + 16

        # ── Reload indicator ────────────────────────────────────────
        reload_w = 60
        label = self.font.render("RDY" if reload_frac >= 1.0 else "...", True,
                                 GREEN if reload_frac >= 1.0 else RED)
        screen.blit(label, (x, cy - label.get_height() // 2))
        x += label.get_width() + 4
        pygame.draw.rect(screen, (40, 40, 40),
                         (x, cy - 4, reload_w, 8))
        pygame.draw.rect(screen, GREEN if reload_frac >= 1.0 else YELLOW,
                         (x, cy - 4, int(reload_w * min(reload_frac, 1.0)), 8))
        x += reload_w + 20

        # ── Bases captured ──────────────────────────────────────────
        total = len(bases)
        captured = sum(1 for b in bases if b.owner == 1)  # PLAYER = 1
        txt = self.font.render(f"Bases: {captured}/{total}", True, HUD_TEXT_COLOR)
        screen.blit(txt, (x, cy - txt.get_height() // 2))
        x += txt.get_width() + 20

        # ── Kills / Deaths ──────────────────────────────────────────
        kd = self.font.render(f"K: {player.kills}  D: {player.deaths}",
                              True, HUD_TEXT_COLOR)
        screen.blit(kd, (x, cy - kd.get_height() // 2))

        # ── Centre message ──────────────────────────────────────────
        if self._message_timer > 0:
            msg = self.big_font.render(self._message, True, YELLOW)
            mx = (SCREEN_WIDTH - msg.get_width()) // 2
            my = screen_h // 3
            # drop shadow
            shadow = self.big_font.render(self._message, True, (40, 40, 0))
            screen.blit(shadow, (mx + 2, my + 2))
            screen.blit(msg, (mx, my))

        # ── Respawn overlay ─────────────────────────────────────────
        if not player.alive:
            overlay = pygame.Surface((SCREEN_WIDTH, screen_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            txt = self.big_font.render("DESTROYED — respawning...", True, RED)
            screen.blit(txt, ((SCREEN_WIDTH - txt.get_width()) // 2,
                              screen_h // 2 - 20))
