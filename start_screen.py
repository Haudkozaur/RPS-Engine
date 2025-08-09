import pygame

class StartScreen:
    """
    Simple number input screen.
    User types how many icons per type (R/P/S) and presses Enter to continue.
    """
    def __init__(self, screen: pygame.Surface,
                 font_large: pygame.font.Font | None = None,
                 font_small: pygame.font.Font | None = None):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_large = font_large or pygame.font.Font(None, 48)
        self.font_small = font_small or pygame.font.Font(None, 28)

        w, h = self.screen.get_size()
        self.input_rect = pygame.Rect(w // 2 - 150, h // 2 - 30, 300, 60)
        self.text = ""

    def run(self) -> int:
        """
        Show the screen until the user presses Enter.
        Returns a positive integer (defaults to 1 if empty/invalid).
        ESC or closing the window quits the app.
        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); raise SystemExit
                    if event.key == pygame.K_RETURN:
                        return self._validated_value()
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        # Accept only digits and limit length to avoid silliness
                        if event.unicode.isdigit() and len(self.text) < 3:
                            self.text += event.unicode

            self._draw()
            pygame.display.flip()
            self.clock.tick(60)

    # ---------- helpers ----------
    def _validated_value(self) -> int:
        try:
            val = int(self.text)
            return val if val > 0 else 1
        except ValueError:
            return 1

    def _draw(self) -> None:
        self.screen.fill((245, 245, 245))
        w, h = self.screen.get_size()

        title = self.font_large.render("How many icons per type?", True, (20, 20, 20))
        self.screen.blit(title, title.get_rect(center=(w // 2, h // 2 - 90)))

        # Input box
        pygame.draw.rect(self.screen, (230, 230, 230), self.input_rect, border_radius=8)
        pygame.draw.rect(self.screen, (40, 40, 40), self.input_rect, 2, border_radius=8)

        placeholder = "1"
        shown = self.text if self.text else placeholder
        txtsurf = self.font_large.render(shown, True, (10, 10, 10))
        self.screen.blit(txtsurf, txtsurf.get_rect(center=self.input_rect.center))

        hint = self.font_small.render("Type digits and press Enter (empty -> 1). ESC to quit.", True, (80, 80, 80))
        self.screen.blit(hint, hint.get_rect(center=(w // 2, h // 2 + 60)))
