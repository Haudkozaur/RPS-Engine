import pygame
from typing import Dict, Tuple

class WinnerOverlay:
    """
    Draws a stretched background image inside the arena when only one type remains.
    """
    def __init__(self, img_map: Dict[str, str]):
        # e.g. {"scissors": "scissors.png", "stone": "stone.png", "paper": "paper.png"}
        self.img_map = img_map
        self._cache: Dict[Tuple[str, Tuple[int,int]], pygame.Surface] = {}

    def _get_scaled(self, kind: str, size: Tuple[int, int]) -> pygame.Surface:
        key = (kind, size)
        if key in self._cache:
            return self._cache[key]
        surf = pygame.image.load(self.img_map[kind]).convert_alpha()
        scaled = pygame.transform.smoothscale(surf, size)
        self._cache[key] = scaled
        return scaled

    def draw_if_winner(self, screen: pygame.Surface, arena_rect: pygame.Rect, counts: Dict[str, int]) -> bool:
        """
        If exactly one kind has count > 0, draw its image stretched to arena and return True.
        """
        alive = [k for k, v in counts.items() if v > 0]
        if len(alive) != 1:
            return False
        winner = alive[0]
        bg = self._get_scaled(winner, (arena_rect.width, arena_rect.height))
        screen.blit(bg, arena_rect.topleft)
        return True
