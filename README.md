# BOLO — Tank Combat Game

A Python/Pygame recreation of the classic 90s multiplayer tank combat game.

## How to Play

### Install & Run
```bash
pip install pygame
python run_game.py          # or: python -m bolo
```

### Controls
| Key / Input         | Action                        |
|---------------------|-------------------------------|
| W / Up Arrow        | Move forward (up)             |
| S / Down Arrow      | Move backward (down)          |
| A / Left Arrow      | Move left                     |
| D / Right Arrow     | Move right                    |
| Mouse               | Aim turret                    |
| Left Click (hold)   | Fire                          |
| Escape              | Quit                          |

### Objective
- Destroy hostile **pillboxes** (red AI turrets) scattered across the map.
- **Capture bases** by staying near the neutral diamond markers for 3 seconds.
- Capture all 6 bases to win!

### Game Elements
- **Grass** — normal terrain
- **Water** — impassable
- **Walls** — block movement and bullets
- **Trees** — slow your tank to half speed; provide partial cover
- **Roads** — decorative (future: speed boost)
- **Pillboxes** (red squares) — hostile turrets that fire when you're in range
- **Bases** (diamond markers) — stand nearby to capture; progress ring shows timer

## Project Structure
```
bolo/
├── __init__.py     # package marker
├── __main__.py     # allows `python -m bolo`
├── config.py       # ALL tunable constants (speeds, damage, colours…)
├── game_map.py     # tile grid, terrain rendering, collision queries
├── tank.py         # player tank: movement, aiming, health
├── bullet.py       # projectiles for tanks and pillboxes
├── pillbox.py      # AI turrets
├── base.py         # capturable bases
├── hud.py          # health bar, score, messages
└── game.py         # main loop, camera, collision wiring
```

## Customisation

Everything you'd want to tweak lives in `bolo/config.py`:

- `TANK_SPEED`, `TANK_MAX_HEALTH`, `TANK_ARMOR`
- `BULLET_SPEED`, `BULLET_DAMAGE`, `BULLET_RELOAD_TIME`
- `PILLBOX_RANGE`, `PILLBOX_FIRE_RATE`, `PILLBOX_HEALTH`
- `BASE_CAPTURE_TIME`, `BASE_CAPTURE_RANGE`
- Terrain colours, tile size, screen resolution, and more.

### Editing the Map

Open `bolo/game_map.py` and modify `DEFAULT_MAP`. Each number is a terrain type:

| Code | Terrain |
|------|---------|
| 0    | Grass   |
| 1    | Water   |
| 2    | Wall    |
| 3    | Tree    |
| 4    | Road    |
