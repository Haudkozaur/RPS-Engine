import random
import pygame

class Arena:

    def __init__(self, window_w: int, window_h: int, margin: int = 40, border: int = 4):
        # Make a centered square inside the window, inset by 'margin'
        side = min(window_w, window_h) - 2 * margin
        left = (window_w - side) // 2
        top  = (window_h - side) // 2
        self.rect = pygame.Rect(left, top, side, side)

        self.border_color = (30, 30, 30)
        self.border = border

    def draw(self, screen: pygame.Surface) -> None:
        pygame.draw.rect(screen, self.border_color, self.rect, self.border)

    def random_point(self, padding: int = 0, *, float_coords: bool = True) -> tuple[float, float]:
        """
        Return a random point inside the arena.
        """
        max_pad = max(0, min(padding, min(self.rect.width, self.rect.height) // 2 - 1))
        left   = self.rect.left   + max_pad
        right  = self.rect.right  - max_pad
        top    = self.rect.top    + max_pad
        bottom = self.rect.bottom - max_pad
        if float_coords:
            x = random.uniform(left, right)
            y = random.uniform(top, bottom)
        else:
            x = random.randint(int(left), int(right))
            y = random.randint(int(top), int(bottom))
        return (x, y)