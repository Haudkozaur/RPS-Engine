import pygame
from typing import Dict, Tuple

class AssetCache:
    def __init__(self) -> None:
        self._surfs: Dict[Tuple[str, Tuple[int,int]], pygame.Surface] = {}
        self.size: Tuple[int,int] | None = None

    def build(self, img_map: Dict[str, str], size: Tuple[int,int]) -> None:
        self._surfs.clear()
        self.size = size
        for kind, path in img_map.items():
            surf = pygame.image.load(path).convert_alpha()
            surf = pygame.transform.smoothscale(surf, size)
            self._surfs[(kind, size)] = surf

    def get(self, kind: str) -> pygame.Surface:
        assert self.size is not None, "AssetCache not built yet"
        return self._surfs[(kind, self.size)]
