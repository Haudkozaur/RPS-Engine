# collisions.py
from __future__ import annotations
import math
import random
from typing import Sequence, Dict, Tuple, List, Set
from collections import defaultdict


class CollisionManager:
    """
    Broad-phase via spatial hashing (uniform grid), narrow-phase circle–circle.
    Resolves overlap (equal mass, elastic swap of normal components),
    applies RPS morph rules, and enforces a minimum speed to avoid stalls.
    """

    def __init__(
        self,
        img_map: Dict[str, str],
        cell_size: int = 128,
        restitution: float = 1.0,
        separation_bias: float = 1.01,
        min_speed: float = 60.0,
    ) -> None:
        """
        img_map: {"scissors": "scissors.png", "stone": "stone.png", "paper": "paper.png"}
        cell_size: spatial grid cell size (≈ icon size works well)
        restitution: 1.0 = perfectly elastic
        separation_bias: >1 pushes a bit extra apart to prevent re-sticking
        min_speed: clamp speed after collisions so sprites never stall
        """
        self.img_map = img_map
        self.cell_size = cell_size
        self.restitution = restitution
        self.separation_bias = separation_bias
        self.min_speed = min_speed

    # ---------- public API ----------

    def resolve_all(self, sprites: Sequence) -> None:
        """
        Bucket sprites into grid cells by center, then resolve collisions only
        within each cell and its 8 neighbors.
        Expects sprites to expose:
          - cx, cy (float center), radius (float), vx, vy
          - set_center(x, y), morph_to(kind, img_path), kind
        """
        # 1) bucketize by cell
        grid = defaultdict(list)  # (cx//cell_size, cy//cell_size) -> [index]
        for i, s in enumerate(sprites):
            cell = (int(s.cx // self.cell_size), int(s.cy // self.cell_size))
            grid[cell].append(i)

        # 2) for each cell and neighbors, resolve pairs
        visited: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = set()
        neighbors = [(-1, -1), (0, -1), (1, -1),
                     (-1,  0), (0,  0), (1,  0),
                     (-1,  1), (0,  1), (1,  1)]

        for cell, idxs in grid.items():
            for dx, dy in neighbors:
                c2 = (cell[0] + dx, cell[1] + dy)
                if c2 not in grid:
                    continue
                key = (min(cell, c2), max(cell, c2))
                if key in visited:
                    continue
                visited.add(key)

                # If same cell, use its list; otherwise merge two lists
                if c2 == cell:
                    self._resolve_list(idxs, sprites)
                else:
                    self._resolve_list(idxs + grid[c2], sprites)

    # ---------- internals ----------

    def _resolve_list(self, idxs: List[int], sprites: Sequence) -> None:
        """Resolve collisions among a small set of indices (same/neighboring cells)."""
        n = len(idxs)
        for a_i in range(n):
            A = sprites[idxs[a_i]]
            ax, ay, ar = A.cx, A.cy, A.radius
            for b_i in range(a_i + 1, n):
                B = sprites[idxs[b_i]]

                # Narrow-phase: circle–circle
                dx = B.cx - ax
                dy = B.cy - ay
                r_sum = ar + B.radius
                dist_sq = dx * dx + dy * dy
                if dist_sq >= r_sum * r_sum:
                    continue  # no collision

                # Compute normal
                if dist_sq > 0.0:
                    dist = math.sqrt(dist_sq)
                    nx = dx / dist
                    ny = dy / dist
                else:
                    # Perfect overlap; pick an arbitrary normal
                    dist = 1.0
                    nx, ny = 1.0, 0.0

                # --- Separate positions along the normal ---
                overlap = (r_sum - dist) * self.separation_bias
                ax -= 0.5 * overlap * nx
                ay -= 0.5 * overlap * ny
                bx = B.cx + 0.5 * overlap * nx
                by = B.cy + 0.5 * overlap * ny

                A.set_center(ax, ay)
                B.set_center(bx, by)

                # --- Resolve velocities: swap normal components (equal mass) ---
                va_n = A.vx * nx + A.vy * ny
                vb_n = B.vx * nx + B.vy * ny

                va_n_after = vb_n * self.restitution
                vb_n_after = va_n * self.restitution

                A.vx += (va_n_after - va_n) * nx
                A.vy += (va_n_after - va_n) * ny
                B.vx += (vb_n_after - vb_n) * nx
                B.vy += (vb_n_after - vb_n) * ny

                # Enforce minimal speed (prevents stalls after head-on swaps)
                self._enforce_min_speed(A)
                self._enforce_min_speed(B)

                # --- Apply RPS morph rules ---
                self._apply_rps_rules(A, B)

    def _apply_rps_rules(self, a, b) -> None:
        """
        RPS transmutation:
          paper vs stone      -> stone -> paper
          stone vs scissors   -> scissors -> stone
          scissors vs paper   -> paper -> scissors
        """
        ka, kb = a.kind, b.kind

        # paper vs stone
        if (ka == "paper" and kb == "stone"):
            b.morph_to("paper", self.img_map["paper"])
        elif (ka == "stone" and kb == "paper"):
            a.morph_to("paper", self.img_map["paper"])

        # stone vs scissors
        elif (ka == "stone" and kb == "scissors"):
            b.morph_to("stone", self.img_map["stone"])
        elif (ka == "scissors" and kb == "stone"):
            a.morph_to("stone", self.img_map["stone"])

        # scissors vs paper
        elif (ka == "scissors" and kb == "paper"):
            b.morph_to("scissors", self.img_map["scissors"])
        elif (ka == "paper" and kb == "scissors"):
            a.morph_to("scissors", self.img_map["scissors"])

    def _enforce_min_speed(self, S) -> None:
        """Ensure sprite's speed is not below min_speed; keep direction if possible."""
        spd = math.hypot(S.vx, S.vy)
        if spd >= self.min_speed:
            return
        if spd < 1e-6:
            ang = random.uniform(0.0, 360.0)
            S.vx = math.cos(math.radians(ang)) * self.min_speed
            S.vy = math.sin(math.radians(ang)) * self.min_speed
        else:
            k = self.min_speed / spd
            S.vx *= k
            S.vy *= k
