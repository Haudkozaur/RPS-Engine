import pygame
from typing import Dict

class Scoreboard:
    """Keeps and renders total wins per kind across rounds."""
    def __init__(self, font: pygame.font.Font | None = None):
        self.font_title = pygame.font.Font(None, 30)
        self.font_line  = font or pygame.font.Font(None, 26)
        self.counts: Dict[str, int] = {"scissors": 0, "stone": 0, "paper": 0}
        self.color_title = (30, 30, 30)
        self.color_text  = (20, 20, 20)

    def reset(self) -> None:
        self.counts = {"scissors": 0, "stone": 0, "paper": 0}

    def add_win(self, kind: str) -> None:
        if kind in self.counts:
            self.counts[kind] += 1

    def draw(self, screen: pygame.Surface, x: int, y: int) -> None:
        # Title
        title = self.font_title.render("Scoreboard", True, self.color_title)
        screen.blit(title, (x, y))
        y += title.get_height() + 8

        # Lines
        for label in ("Scissors", "Stone", "Paper"):
            key = label.lower()
            line = self.font_line.render(f"{label}: {self.counts[key]}", True, self.color_text)
            screen.blit(line, (x, y))
            y += line.get_height() + 4
