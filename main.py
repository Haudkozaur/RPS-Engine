import pygame
from arena import Arena
from start_screen import StartScreen
from RPS import Scissors, Stone, Paper
from collisions import CollisionManager
from hud import HUD
from winner_overlay import WinnerOverlay
from buttons import ButtonPanel
from scoreboard import Scoreboard
from assets import AssetCache


IMG_MAP = {
    "scissors": "img/scissors.png",
    "stone":    "img/stone.png",
    "paper":    "img/paper.png",
}

PANEL_WIDTH = 220  # room for buttons + scoreboard on the right


# ---------- sizing ----------

def icon_size_for(n: int) -> tuple[int, int]:
    """
    The value 'n' is the number of elements (per type).
    """
    if n <= 2:
        s = 100
    elif n <= 5:
        s = 72
    elif n <= 10:
        s = 56
    elif n <= 20:
        s = 48
    elif n <= 40:
        s = 32
    else:
        s = 24
    return (s, s)


def make_collision_manager_for(sprites, assets: AssetCache) -> CollisionManager:
    if sprites:
        icon_w = sprites[0].rect.width
    else:
        icon_w = 64
    cell_size = max(32, int(icon_w * 1.2))
    return CollisionManager(
        img_map=IMG_MAP,
        asset_cache=assets,        # fast morphs via cache
        cell_size=cell_size,
        restitution=1.0,
        separation_bias=1.02,
        min_speed=60.0,
    )


# ---------- spawning ----------

def spawn_sprites(n: int, arena: Arena) -> list:
    """Spawn n of each icon at random positions inside the arena."""
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
    WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED, vsync=1)
    pygame.display.set_caption("RPS-Engine")
    clock = pygame.time.Clock()

    _ = clock.tick(120)  # ensure first dt is small

    # Start screen
    n = StartScreen(screen).run()

    # Arena shrunk so the right panel has room
    arena = Arena(WIDTH - PANEL_WIDTH, HEIGHT, margin=40, border=4)

    # Systems/UI
    hud = HUD()
    overlay = WinnerOverlay(IMG_MAP)
    scoreboard = Scoreboard()
    panel = ButtonPanel(screen.get_rect())
    assets = AssetCache()  # cache of pre-scaled surfaces

    # Initial round: build cache for current size, then spawn & collisions
    assets.build(IMG_MAP, icon_size_for(n))
    sprites = spawn_sprites(n, arena)
    collisions = make_collision_manager_for(sprites, assets)

    # Round state
    round_active = True
    running = True

    # --- actions ---

    def restart_simulation():
        nonlocal sprites, collisions, round_active
        # rebuild cache in case size changes with n
        assets.build(IMG_MAP, icon_size_for(n))
        sprites = spawn_sprites(n, arena)
        collisions = make_collision_manager_for(sprites, assets)
        round_active = True

    def restart_to_start(scr, w, h):
        nonlocal sprites, collisions, n, round_active
        n = StartScreen(scr).run()
        scoreboard.reset()
        assets.build(IMG_MAP, icon_size_for(n))
        sprites = spawn_sprites(n, arena)
        collisions = make_collision_manager_for(sprites, assets)
        round_active = True

    def exit_game():
        nonlocal running
        running = False

    # Wire up buttons
    panel.set_action(0, lambda: restart_to_start(screen, WIDTH, HEIGHT))
    panel.set_action(1, lambda: restart_simulation())
    panel.set_action(2, lambda: exit_game())

    # --- main loop ---
    while running:
        dt = clock.tick(120) / 1000.0
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

        # Counts for HUD
        hud.update_counts(sprites)
        counts = hud.counts

        # Detect winner
        alive = [k for k, v in counts.items() if v > 0]
        if round_active and len(alive) == 1:
            scoreboard.add_win(alive[0])
            round_active = False

        # --- draw ---
        screen.fill((255, 255, 255))
        overlay.draw_if_winner(screen, arena.rect, counts)  # winner background
        arena.draw(screen)
        hud.draw(screen, arena.rect)

        for s in sprites:
            s.draw(screen)

        panel.draw(screen)

        sb_x = panel.buttons[0].rect.left
        sb_y = panel.buttons[-1].rect.bottom + 30
        scoreboard.draw(screen, sb_x, sb_y)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
