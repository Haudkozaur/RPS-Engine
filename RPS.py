import random
import pygame
from typing import Tuple, Optional


class RPS:

    def __init__(
        self,
        img_path: str,
        arena_rect: pygame.Rect,
        size: Tuple[int, int] = (150, 150),
        center: Optional[Tuple[float, float]] = None,
        speed_range: Tuple[float, float] = (120.0, 220.0),
    ) -> None:
        # Arena bounds 
        self.arena: pygame.Rect = arena_rect.copy()

        # Load & scale
        self.image: pygame.Surface = pygame.image.load(img_path).convert_alpha()
        self.size: Tuple[int, int] = size
        if self.size:
            self.image = pygame.transform.smoothscale(self.image, self.size)

        # Cached rect + center (float for physics, int for blitting)
        self.rect: pygame.Rect = self.image.get_rect(center=center or self.arena.center)
        self.cx: float = float(self.rect.centerx)
        self.cy: float = float(self.rect.centery)

        # Cached collision radius 
        self.radius: float = 0.30 * max(self.rect.width, self.rect.height)

        # Random initial velocity 
        angle = random.uniform(0.0, 360.0)
        vec = pygame.math.Vector2(1, 0).rotate(angle)
        speed = random.uniform(*speed_range)
        self.vx: float = float(vec.x * speed)
        self.vy: float = float(vec.y * speed)

        # Logical kind; subclasses set this appropriately after super().__init__
        self.kind: str = "unknown"

    # ---------- public API ----------

    def set_center(self, x: float, y: float) -> None:
        
        self.cx, self.cy = x, y
        self.rect.centerx = int(x)
        self.rect.centery = int(y)

    def set_size(self, width: int, height: int) -> None:
        self.size = (width, height)
        # Keep current center while rescaling
        c = (self.rect.centerx, self.rect.centery)
        self.image = pygame.transform.smoothscale(self.image, self.size)
        self.rect = self.image.get_rect(center=c)
        self.cx, self.cy = float(self.rect.centerx), float(self.rect.centery)
        self.radius = 0.30 * max(self.rect.width, self.rect.height)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.image, self.rect)

    def update(self, dt: float) -> None:
        """
        Integrate motion and bounce off arena borders.
        """
        # Integrate
        nx = self.cx + self.vx * dt
        ny = self.cy + self.vy * dt
        self.set_center(nx, ny)

        # Horizontal bounce
        if self.rect.left <= self.arena.left:
            self.rect.left = self.arena.left
            self.cx = float(self.rect.centerx)
            self.vx *= -1.0
        elif self.rect.right >= self.arena.right:
            self.rect.right = self.arena.right
            self.cx = float(self.rect.centerx)
            self.vx *= -1.0

        # Vertical bounce
        if self.rect.top <= self.arena.top:
            self.rect.top = self.arena.top
            self.cy = float(self.rect.centery)
            self.vy *= -1.0
        elif self.rect.bottom >= self.arena.bottom:
            self.rect.bottom = self.arena.bottom
            self.cy = float(self.rect.centery)
            self.vy *= -1.0

    def get_collision_circle(self) -> Tuple[float, float, float]:
        return self.cx, self.cy, self.radius

    def morph_to(self, kind: str, img_path: str) -> None:
        """
        Change this sprite into another kind, preserving position/velocity.
        """
        self.kind = kind
        # Keep center while swapping image
        c = (self.rect.centerx, self.rect.centery)
        self.image = pygame.image.load(img_path).convert_alpha()
        if self.size:
            self.image = pygame.transform.smoothscale(self.image, self.size)
        self.rect = self.image.get_rect(center=c)
        self.cx, self.cy = float(self.rect.centerx), float(self.rect.centery)
        self.radius = 0.45 * max(self.rect.width, self.rect.height)


    def morph_to_cached(self, kind: str, cached_surface: pygame.Surface) -> None:
        """Fast morph: swap to pre-scaled Surface without touching rect/radius."""
        self.kind = kind
        self.image = cached_surface

# subclasses that tag the kind
class Scissors(RPS):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.kind = "scissors"


class Stone(RPS):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.kind = "stone"


class Paper(RPS):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.kind = "paper"
