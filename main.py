# main.py
import pygame
from arena import Arena
from start_screen import StartScreen
from RPS import Scissors, Stone, Paper
from collisions import CollisionManager
from hud import HUD
from winner_overlay import WinnerOverlay
from buttons import ButtonPanel
from scoreboard import Scoreboard
from assets import AssetCache  # pre-scaled surfaces for fast morphing


IMG_MAP = {
    "scissors": "img//scissors.png",
    "stone":    "img//stone.png",
    "paper":    "img//paper.png",
}

PANEL_WIDTH = 220  # room for buttons + scoreboard on the right


# ---------- sizing policy ----------

def icon_size_for(n: int) -> tuple[int, int]:
    """
    Step-wise icon size tuned for performance and clarity.
    The value 'n' is the number of icons per type.
    Smaller sizes kick in earlier than before.
    """
    if n <= 2:
        s = 100
    elif n <= 5:
        s = 64
    elif n <= 10:
        s = 48
    elif n <= 20:
        s = 40
    elif n <= 40:
        s = 32
    else:
        s = 24
    return (s, s)


def make_collision_manager_for(sprites, assets: AssetCache) -> CollisionManager:
    """
    Configure the CollisionManager with a cell size adapted to current icon size.
    Roughly ~1.2x icon width (works well as a broad-phase grid).
    Pass the asset cache so morphs don't load/scale every time.
    """
    if sprites:
        icon_w = sprites[0].rect.width
    else:
        icon_w = 64
    cell_size = max(32, int(icon_w * 1.2))
    return CollisionManager(
        img_map=IMG_MAP,
        asset_cache=assets,
        cell_size=cell_size,
        restitution=1.0,
        separation_bias=1.02,
        min_speed=60.0,
    )


# ---------- spawning ----------

def spawn_sprites(n: int, arena: Arena) -> list:
    """Spawn n of each icon at random positions inside the arena, with adaptive size."""
    size = icon_size_for(n)
    pad = (max(size) // 2) + 6  # keep sprites away from arena walls
    sprites = []
    for _ in range(n):
        sprites.append(Scissors(IMG_MAP["scissors"], arena.rect, size=size,
                                center=arena.random_point(padding=pad, float_coords=True)))
        sprites.append(Stone(   IMG_MAP["stone"],    arena.rect, size=size,
                                center=arena.random_point(padding=pad, float_coords=True)))
        sprites.append(Paper(   IMG_MAP["paper"],    arena.rect, size=size,
                                center=arena.random_point(padding=pad, float_coords=True)))
    return sprites


# ---------- app ----------

def main() -> None:
    pygame.init()
    WIDTH, HEIGHT = 1000, 700  # wide enough for the right-side panel
    # vsync for smoother presentation (requires pygame 2.x + supported driver)
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED, vsync=1)
    pygame.display.set_caption("RPS-Engine")
    clock = pygame.time.Clock()

    _ = clock.tick(240)  # ensure first dt is small

    # Start screen -> how many per type
    n = StartScreen(screen).run()

    # Arena shrunk horizontally so the right panel has room
    arena = Arena(WIDTH - PANEL_WIDTH, HEIGHT, margin=40, border=4)

    # Systems/UI
    hud = HUD()
    overlay = WinnerOverlay(IMG_MAP)
    scoreboard = Scoreboard()
    panel = ButtonPanel(screen.get_rect())
    assets = AssetCache()  # pre-scaled surfaces for current icon size

    # Initial round
    assets.build(IMG_MAP, icon_size_for(n))   # build cache once for current size
    sprites = spawn_sprites(n, arena)
    collisions = make_collision_manager_for(sprites, assets)

    # Round state: to award winner exactly once per round
    round_active = True
    running = True

    # --- actions (wired to buttons / keys) ---

    def restart_simulation():
        """Like Enter: re-spawn with current 'n', keep scoreboard."""
        nonlocal sprites, collisions, round_active
        assets.build(IMG_MAP, icon_size_for(n))   # rebuild cache if size changes with n
        sprites = spawn_sprites(n, arena)
        collisions = make_collision_manager_for(sprites, assets)
        round_active = True

    def restart_to_start(scr, w, h):
        """Return to start: ask for new 'n' and reset scoreboard."""
        nonlocal sprites, collisions, n, round_active
        n = StartScreen(scr).run()
        scoreboard.reset()
        assets.build(IMG_MAP, icon_size_for(n))   # rebuild for the new size
        sprites = spawn_sprites(n, arena)
        collisions = make_collision_manager_for(sprites, assets)
        round_active = True

    def exit_game():
        nonlocal running
        running = False

    # Wire up button actions (Return / Restart / Exit)
    panel.set_action(0, lambda: restart_to_start(screen, WIDTH, HEIGHT))
    panel.set_action(1, lambda: restart_simulation())
    panel.set_action(2, lambda: exit_game())

    # --- main loop ---
    while running:
        dt = clock.tick(120) / 1000.0  # seconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                restart_simulation()
            panel.handle_event(event)

        # Physics
        for s in sprites:
            s.update(dt)
        collisions.resolve_all(sprites)

        # Counts for HUD, overlay, scoreboard-logic
        hud.update_counts(sprites)
        counts = hud.counts  # {"scissors": int, "stone": int, "paper": int}

        # Detect winner ONCE per round (exactly one type remains)
        alive = [k for k, v in counts.items() if v > 0]
        if round_active and len(alive) == 1:
            scoreboard.add_win(alive[0])
            round_active = False

        # --- draw ---
        screen.fill((255, 255, 255))

        # Winner background if only one type remains (under sprites)
        overlay.draw_if_winner(screen, arena.rect, counts)

        # Arena frame + HUD
        arena.draw(screen)
        hud.draw(screen, arena.rect)

        # Sprites on top
        for s in sprites:
            s.draw(screen)

        # Buttons panel on the right
        panel.draw(screen)

        # Scoreboard under the buttons
        sb_x = panel.buttons[0].rect.left
        sb_y = panel.buttons[-1].rect.bottom + 30
        scoreboard.draw(screen, sb_x, sb_y)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
