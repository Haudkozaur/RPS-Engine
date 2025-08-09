import pygame

class Button:
    def __init__(self, rect, text, font, color_bg, color_text, action):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.color_bg = color_bg
        self.color_text = color_text
        self.action = action 

    def draw(self, screen):
        pygame.draw.rect(screen, self.color_bg, self.rect, border_radius=6)
        label = self.font.render(self.text, True, self.color_text)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if callable(self.action):
                    self.action()


class ButtonPanel:
    def __init__(self, screen_rect, button_width=180, button_height=50, spacing=20):
        font = pygame.font.Font(None, 28)
        panel_x = screen_rect.right - button_width - 20
        panel_y = 100

        # Buttons
        self.buttons = [
            Button(
                (panel_x, panel_y, button_width, button_height),
                "Return to Start",
                font,
                (70, 130, 180), (255, 255, 255),
                action=None  # assigned in main
            ),
            Button(
                (panel_x, panel_y + (button_height + spacing), button_width, button_height),
                "Restart",
                font,
                (34, 139, 34), (255, 255, 255),
                action=None
            ),
            Button(
                (panel_x, panel_y + 2 * (button_height + spacing), button_width, button_height),
                "Exit",
                font,
                (178, 34, 34), (255, 255, 255),
                action=None
            )
        ]

    def draw(self, screen):
        for b in self.buttons:
            b.draw(screen)

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def set_action(self, index, func):
        """Assigns callback function to button at given index."""
        if 0 <= index < len(self.buttons):
            self.buttons[index].action = func
