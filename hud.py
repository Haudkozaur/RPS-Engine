# hud.py
import pygame
from collections import Counter

class HUD:
    """Real-time counters for R/P/S, drawn above the arena."""
    def __init__(self, font: pygame.font.Font | None = None):
        self.font = font or pygame.font.Font(None, 32)
        self.counts = {"scissors": 0, "stone": 0, "paper": 0}
        self.text_color = (20, 20, 20)
        self.bg_color = (245, 245, 245)   # subtle background for readability
        self.pad = 6

    def update_counts(self, sprites) -> None:
        c = Counter(s.kind for s in sprites)
        self.counts["scissors"] = c.get("scissors", 0)
        self.counts["stone"]    = c.get("stone", 0)
        self.counts["paper"]    = c.get("paper", 0)

    def draw(self, screen: pygame.Surface, arena_rect: pygame.Rect) -> None:
        label = f"Scissors: {self.counts['scissors']}   Stone: {self.counts['stone']}   Paper: {self.counts['paper']}"
        surf = self.font.render(label, True, self.text_color)
        # place centered above arena; if no room, draw inside top edge
        y = arena_rect.top - surf.get_height() - 8
        if y < 4:
            y = arena_rect.top + 4
        x = arena_rect.centerx - surf.get_width() // 2

        # background pill
        bg_rect = pygame.Rect(x - self.pad, y - self.pad, surf.get_width() + 2*self.pad, surf.get_height() + 2*self.pad)
        pygame.draw.rect(screen, self.bg_color, bg_rect, border_radius=8)
        screen.blit(surf, (x, y))
