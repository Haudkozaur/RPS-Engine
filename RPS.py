# RPS.py
import random
import pygame
from typing import Tuple, Optional


class RPS:
    """
    Base class for Rock/Paper/Scissors icons with:
    - cached rect/center/radius (no get_rect() churn every frame)
    - arena-bounded motion & wall bounces
    - morph_to(kind, img_path) to swap graphics on-the-fly (RPS rules)
    """

    def __init__(
        self,
        img_path: str,
        arena_rect: pygame.Rect,
        size: Tuple[int, int] = (150, 150),
        center: Optional[Tuple[float, float]] = None,
        speed_range: Tuple[float, float] = (120.0, 220.0),
    ) -> None:
        # Arena bounds to bounce against (copy to be safe)
        self.arena: pygame.Rect = arena_rect.copy()

        # Load & scale once
        self.image: pygame.Surface = pygame.image.load(img_path).convert_alpha()
        self.size: Tuple[int, int] = size
        if self.size:
            self.image = pygame.transform.smoothscale(self.image, self.size)

        # Cached rect + center (float for physics, int for blitting)
        self.rect: pygame.Rect = self.image.get_rect(center=center or self.arena.center)
        self.cx: float = float(self.rect.centerx)
        self.cy: float = float(self.rect.centery)

        # Cached collision radius (slightly inset circle)
        self.radius: float = 0.45 * max(self.rect.width, self.rect.height)

        # Random initial velocity (px/s)
        angle = random.uniform(0.0, 360.0)
        vec = pygame.math.Vector2(1, 0).rotate(angle)
        speed = random.uniform(*speed_range)
        self.vx: float = float(vec.x * speed)
        self.vy: float = float(vec.y * speed)

        # Logical kind; subclasses set this appropriately after super().__init__
        self.kind: str = "unknown"

    # ---------- public API ----------

    def set_center(self, x: float, y: float) -> None:
        """Update cached float center and sync the rect."""
        self.cx, self.cy = x, y
        self.rect.centerx = int(x)
        self.rect.centery = int(y)

    def set_size(self, width: int, height: int) -> None:
        """Rescale sprite and update rect/radius (keeps current center)."""
        self.size = (width, height)
        # Keep current center while rescaling
        c = (self.rect.centerx, self.rect.centery)
        self.image = pygame.transform.smoothscale(self.image, self.size)
        self.rect = self.image.get_rect(center=c)
        self.cx, self.cy = float(self.rect.centerx), float(self.rect.centery)
        self.radius = 0.45 * max(self.rect.width, self.rect.height)

    def draw(self, screen: pygame.Surface) -> None:
        """Blit using cached rect (no extra get_rect)."""
        screen.blit(self.image, self.rect)

    def update(self, dt: float) -> None:
        """
        Integrate motion and bounce off arena borders.
        Uses cached center and rect for minimal overhead.
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
        """Return (cx, cy, r) for collision checks (already cached)."""
        return self.cx, self.cy, self.radius

    def morph_to(self, kind: str, img_path: str) -> None:
        """
        Change this sprite into another kind, preserving position/velocity.
        Recomputes rect and radius while keeping current center.
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
            """
            Fast morph: swap to pre-scaled Surface without touching rect/radius.
            Assumes cached_surface has the same size as current self.image.
            """
            self.kind = kind
            self.image = cached_surface
            # rect center/size and radius remain the same → zero kosztu


# Thin subclasses that only tag the kind
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
