import pygame
import sys
from GUI.othello_gui import OthelloGUI
from GUI.button_gui import Button
 
# ── Window — must match othello_gui.py exactly ──────────────────────
WIN_W, WIN_H = 1100, 720
 
# ── Colour palette (same as game) ───────────────────────────────────
BG_COLOR      = (18,  18,  30)
PANEL_COLOR   = (28,  28,  46)
BOARD_GREEN   = (30, 110,  50)
ACCENT        = (88, 166, 255)
ACCENT_HOVER  = (120, 190, 255)
TEXT_LIGHT    = (220, 220, 220)
TEXT_DIM      = (130, 130, 150)
TEXT_MUTED    = (80,  80, 100)
BORDER_COLOR  = (50,  50,  80)
BTN_BG        = (38,  38,  62)
BTN_HOVER     = (50,  60, 100)
BTN_BORDER    = (70,  90, 160)
GREEN_BTN     = (30,  90,  50)
GREEN_HOVER   = (40, 120,  65)
RED_BTN       = (90,  30,  30)
RED_HOVER     = (120, 40,  40)
WHITE_DISC    = (240, 240, 240)
BLACK_DISC    = (30,   30,  30)
 
 
class MenuButton:
    """Themed button that matches the game's dark UI."""
 
    def __init__(self, cx, cy, w, h, text, color=BTN_BG, hover_color=BTN_HOVER,
                 text_color=TEXT_LIGHT, border_color=BTN_BORDER, font_size=26):
        self.rect        = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
        self.text        = text
        self.color       = color
        self.hover_color = hover_color
        self.text_color  = text_color
        self.border_color= border_color
        self.font        = pygame.font.SysFont("segoeui", font_size)
        self.hovered     = False
 
    def draw(self, surface):
        mx, my = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mx, my)
        bg = self.hover_color if self.hovered else self.color
 
        pygame.draw.rect(surface, bg, self.rect, border_radius=10)
        pygame.draw.rect(surface, self.border_color, self.rect, width=1, border_radius=10)
 
        # Render (handle multi-line with \n)
        lines = self.text.split("\n")
        total_h = len(lines) * (self.font.get_height() + 2)
        start_y = self.rect.centery - total_h // 2
        for i, line in enumerate(lines):
            surf = self.font.render(line, True, ACCENT if self.hovered else self.text_color)
            surface.blit(surf, (self.rect.centerx - surf.get_width() // 2,
                                start_y + i * (self.font.get_height() + 2)))
 
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
 
 
def _draw_board_preview(surface, cx, cy, size=160):
    """Draw a mini Othello board as decoration."""
    cells = size // 8
    bx = cx - size // 2
    by = cy - size // 2
    for r in range(8):
        for c in range(8):
            shade = (32, 115, 52) if (r + c) % 2 == 0 else BOARD_GREEN
            pygame.draw.rect(surface, shade, (bx + c * cells, by + r * cells, cells, cells))
            pygame.draw.rect(surface, (20, 80, 35),
                             (bx + c * cells, by + r * cells, cells, cells), 1)
    # Starting discs
    mid = 8 // 2
    for r, c, col in [(mid-1, mid-1, WHITE_DISC), (mid-1, mid, BLACK_DISC),
                      (mid,   mid-1, BLACK_DISC), (mid,   mid, WHITE_DISC)]:
        pygame.draw.circle(surface, col,
                           (bx + c * cells + cells // 2, by + r * cells + cells // 2),
                           cells // 2 - 2)
    # Border
    pygame.draw.rect(surface, ACCENT, (bx, by, size, size), width=2, border_radius=4)
 
 
def _draw_background(surface):
    """Dark gradient-style background with subtle grid pattern."""
    surface.fill(BG_COLOR)
    # Subtle dot grid
    for x in range(0, WIN_W, 40):
        for y in range(0, WIN_H, 40):
            pygame.draw.circle(surface, (30, 30, 50), (x, y), 1)
    # Left accent strip
    pygame.draw.rect(surface, PANEL_COLOR, (0, 0, 4, WIN_H))
    pygame.draw.rect(surface, ACCENT, (0, 0, 4, WIN_H))
 
 
def _draw_title(surface):
    """Draw the OTHELLO title with disc decorations."""
    font_title = pygame.font.SysFont("segoeui", 72, bold=True)
    font_sub   = pygame.font.SysFont("segoeui", 20)
 
    title = font_title.render("OTHELLO", True, ACCENT)
    surface.blit(title, (WIN_W // 2 - title.get_width() // 2, 60))
 
    sub = font_sub.render("Minimax AI  ·  Strategy Board Game", True, TEXT_DIM)
    surface.blit(sub, (WIN_W // 2 - sub.get_width() // 2, 148))
 
    # Decorative discs beside title
    pygame.draw.circle(surface, BLACK_DISC, (WIN_W // 2 - title.get_width() // 2 - 36, 100), 18)
    pygame.draw.circle(surface, (120, 120, 120), (WIN_W // 2 - title.get_width() // 2 - 36, 100), 18, 2)
    pygame.draw.circle(surface, WHITE_DISC, (WIN_W // 2 + title.get_width() // 2 + 36, 100), 18)
    pygame.draw.circle(surface, (120, 120, 120), (WIN_W // 2 + title.get_width() // 2 + 36, 100), 18, 2)
 
    # Divider line
    pygame.draw.line(surface, BORDER_COLOR,
                     (WIN_W // 2 - 200, 178), (WIN_W // 2 + 200, 178), 1)
 
 
class Menu:
    def __init__(self):
        self.win = self._init_pygame()
        self.clock = pygame.time.Clock()
 
    def _init_pygame(self):
        pygame.init()
        win = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Othello  ·  Minimax AI")
        return win
 
    # ── helpers ─────────────────────────────────────────────────────
 
    def _base_frame(self):
        _draw_background(self.win)
        _draw_title(self.win)
        _draw_board_preview(self.win, WIN_W - 180, WIN_H // 2, size=200)
 
    def _event_loop(self, buttons, on_click):
        """Generic event loop. on_click(button) → action string or None."""
        while True:
            self._draw_frame(buttons)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "back"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in buttons:
                        if btn.is_clicked(event.pos):
                            result = on_click(btn)
                            if result == "redraw":
                                break
                            return result
            self.clock.tick(60)
 
    def _draw_frame(self, buttons):
        self._base_frame()
        for btn in buttons:
            btn.draw(self.win)
        pygame.display.update()
 
    # ── MAIN MENU ────────────────────────────────────────────────────
 
    def draw_menu(self):
        cx = WIN_W // 2 - 80   # shift left so board preview has space
 
        buttons = [
            MenuButton(cx, 260, 280, 52, "Start Game",
                       color=GREEN_BTN, hover_color=GREEN_HOVER,
                       border_color=(60, 160, 80)),
            MenuButton(cx, 330, 280, 52, "Game Rules"),
            MenuButton(cx, 400, 280, 52, "Exit",
                       color=RED_BTN, hover_color=RED_HOVER,
                       border_color=(160, 60, 60)),
        ]
 
        # Version tag
        font_sm = pygame.font.SysFont("segoeui", 14)
        ver = font_sm.render("v2.0  ·  AI Coach Edition", True, TEXT_MUTED)
 
        def on_click(btn):
            if btn.text == "Start Game":
                self.draw_submenu()
            elif btn.text == "Game Rules":
                self.draw_rules()
            elif btn.text == "Exit":
                pygame.quit()
                sys.exit()
 
        while True:
            self._base_frame()
            for btn in buttons:
                btn.draw(self.win)
            self.win.blit(ver, (WIN_W // 2 - 80 - ver.get_width() // 2, WIN_H - 30))
            pygame.display.update()
 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in buttons:
                        if btn.is_clicked(event.pos):
                            on_click(btn)
            self.clock.tick(60)
 
    # ── SUBMENU ──────────────────────────────────────────────────────
 
    def draw_submenu(self):
        cx = WIN_W // 2 - 80
 
        font_hdr = pygame.font.SysFont("segoeui", 22)
        hdr = font_hdr.render("Choose Game Mode", True, TEXT_DIM)
 
        buttons = [
            MenuButton(cx, 260, 300, 56, "Multi-player\n(Play with Friend)"),
            MenuButton(cx, 336, 300, 56, "Single-player\n(Play with AI)",
                       color=GREEN_BTN, hover_color=GREEN_HOVER,
                       border_color=(60, 160, 80)),
            MenuButton(cx, 420, 280, 44, "← Back", font_size=22,
                       color=(30, 30, 50), border_color=BORDER_COLOR,
                       text_color=TEXT_DIM),
        ]
 
        while True:
            self._base_frame()
            self.win.blit(hdr, (cx - hdr.get_width() // 2, 210))
            for btn in buttons:
                btn.draw(self.win)
            pygame.display.update()
 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.draw_menu(); return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in buttons:
                        if btn.is_clicked(event.pos):
                            if "Multi-player" in btn.text:
                                game = OthelloGUI(player_mode="human")
                                game.run_game(return_to_menu_callback=self.draw_menu)
                            elif "Single-player" in btn.text:
                                self.draw_difficulty_menu(); return
                            elif "Back" in btn.text:
                                self.draw_menu(); return
            self.clock.tick(60)
 
    # ── DIFFICULTY ───────────────────────────────────────────────────
 
    def draw_difficulty_menu(self):
        cx = WIN_W // 2 - 80
 
        font_hdr = pygame.font.SysFont("segoeui", 22)
        hdr      = font_hdr.render("Select Difficulty", True, TEXT_DIM)
        font_sm  = pygame.font.SysFont("segoeui", 14)
 
        descs = {
            "Easy":   "Depth 2  ·  Good for beginners",
            "Medium": "Depth 3  ·  Balanced challenge",
            "Hard":   "Depth 5  ·  Plays near-optimally",
        }
 
        diff_colors = {
            "Easy":   ((30, 90, 50),  (40, 120, 65),  (60, 160, 80)),
            "Medium": ((30, 60, 100), (40, 80, 140),  (70, 120, 200)),
            "Hard":   ((90, 30, 30),  (120, 40, 40),  (160, 60, 60)),
        }
 
        buttons = []
        for i, (label, (bg, hov, brd)) in enumerate(diff_colors.items()):
            buttons.append(MenuButton(cx, 250 + i * 80, 300, 56, label,
                                      color=bg, hover_color=hov, border_color=brd))
        buttons.append(MenuButton(cx, 490, 280, 44, "← Back", font_size=22,
                                  color=(30, 30, 50), border_color=BORDER_COLOR,
                                  text_color=TEXT_DIM))
 
        while True:
            self._base_frame()
            self.win.blit(hdr, (cx - hdr.get_width() // 2, 200))
 
            for btn in buttons:
                btn.draw(self.win)
                if btn.text in descs:
                    desc = font_sm.render(descs[btn.text], True, TEXT_MUTED)
                    self.win.blit(desc, (cx - desc.get_width() // 2,
                                        btn.rect.bottom + 4))
 
            pygame.display.update()
 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.draw_submenu(); return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for btn in buttons:
                        if btn.is_clicked(event.pos):
                            if btn.text == "Easy":
                                game = OthelloGUI(player_mode="ai", difficulty="easy")
                                game.run_game(return_to_menu_callback=self.draw_menu)
                            elif btn.text == "Medium":
                                game = OthelloGUI(player_mode="ai", difficulty="medium")
                                game.run_game(return_to_menu_callback=self.draw_menu)
                            elif btn.text == "Hard":
                                game = OthelloGUI(player_mode="ai", difficulty="hard")
                                game.run_game(return_to_menu_callback=self.draw_menu)
                            elif "Back" in btn.text:
                                self.draw_submenu(); return
            self.clock.tick(60)
 
    # ── GAME RULES ───────────────────────────────────────────────────
 
    def draw_rules(self):
        font_hdr  = pygame.font.SysFont("segoeui", 28, bold=True)
        font_rule = pygame.font.SysFont("segoeui", 18)
        font_sm   = pygame.font.SysFont("segoeui", 14)
 
        rules = [
            ("1.", "Played on an 8×8 board with 64 discs."),
            ("2.", "Black always moves first."),
            ("3.", "Place a disc to trap opponent discs in a line."),
            ("4.", "Trapped discs flip to your colour."),
            ("5.", "You must play a valid move if one exists."),
            ("6.", "If no valid move, your turn is skipped."),
            ("7.", "Game ends when neither player can move."),
            ("8.", "Player with the most discs wins!"),
        ]
 
        tips = [
            "Tip: Corners are the most valuable squares — they can never be flipped!",
            "Tip: Edges are safer than the centre early in the game.",
            "Tip: Limit your opponent's valid moves (mobility strategy).",
        ]
 
        back_btn = MenuButton(WIN_W // 2, WIN_H - 60, 200, 44, "← Back",
                              font_size=22, color=(30, 30, 50),
                              border_color=BORDER_COLOR, text_color=TEXT_DIM)
 
        while True:
            _draw_background(self.win)
 
            # Header
            hdr = font_hdr.render("Game Rules", True, ACCENT)
            self.win.blit(hdr, (WIN_W // 2 - hdr.get_width() // 2, 50))
            pygame.draw.line(self.win, BORDER_COLOR,
                             (WIN_W // 2 - 200, 90), (WIN_W // 2 + 200, 90), 1)
 
            # Rules — two columns
            col_w = WIN_W // 2 - 60
            for i, (num, text) in enumerate(rules):
                col = i % 2
                row = i // 2
                x = 80 + col * col_w
                y = 120 + row * 54
 
                # Rule number badge
                pygame.draw.rect(self.win, PANEL_COLOR,
                                 pygame.Rect(x, y, 28, 28), border_radius=6)
                pygame.draw.rect(self.win, BTN_BORDER,
                                 pygame.Rect(x, y, 28, 28), width=1, border_radius=6)
                n = font_rule.render(num, True, ACCENT)
                self.win.blit(n, (x + 14 - n.get_width() // 2, y + 4))
 
                t = font_rule.render(text, True, TEXT_LIGHT)
                self.win.blit(t, (x + 36, y + 5))
 
            # Tips
            ty = 360
            pygame.draw.line(self.win, BORDER_COLOR, (80, ty), (WIN_W - 80, ty), 1)
            ty += 14
            for tip in tips:
                ts = font_sm.render(tip, True, TEXT_DIM)
                self.win.blit(ts, (WIN_W // 2 - ts.get_width() // 2, ty))
                ty += 26
 
            back_btn.draw(self.win)
            pygame.display.update()
 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.draw_menu(); return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if back_btn.is_clicked(event.pos):
                        self.draw_menu(); return
            self.clock.tick(60)
 
 
def run_menu():
    menu = Menu()
    menu.draw_menu()



























# import pygame
# import sys
# from GUI.othello_gui import OthelloGUI
# from GUI.button_gui import Button

# # Constants and colors
# WIDTH, HEIGHT = 480, 560
# WHITE_COLOR = (255, 255, 255)
# BLACK_COLOR = (0, 0, 0)
# GREEN_COLOR = (0, 128, 0)
# SUBMENU_SPACING = 75
# BACKGROUND_IMAGE_PATH = "./utils/pictures/othello_blurred.jpg"


# class Menu:
#     def __init__(self):
#         self.win = self.initialize_pygame()
#         self.menu_font = pygame.font.SysFont(None, 36)

#         self.menu_items = ["Start Game", "Game Rules", "Exit"]

#         self.submenu_items = [
#             "Multi-player\n(Play with Friend)",
#             "Single-player\n(Play with AI)",
#             "Return to Main Menu",
#         ]

#         self.difficulty_items = ["Easy", "Medium", "Hard", "Back"]

#         self.return_button = None

#         self.background_image = pygame.image.load(BACKGROUND_IMAGE_PATH)
#         self.background_image = pygame.transform.scale(
#             self.background_image, (WIDTH, HEIGHT)
#         )

#     def initialize_pygame(self):
#         pygame.init()
#         win = pygame.display.set_mode((WIDTH, HEIGHT))
#         pygame.display.set_caption("Othello - Main Menu")
#         return win

#     # ---------------- MAIN MENU ----------------
#     def draw_menu(self):
#         self.win.blit(self.background_image, (0, 0))

#         buttons = []
#         for i, item in enumerate(self.menu_items):
#             button = Button(WIDTH // 2, 200 + i * 50, 200, 40, item, self.menu_font)
#             buttons.append(button)
#             button.draw(self.win)

#         pygame.display.update()
#         self.handle_input_menu(buttons)

#     # ---------------- SUBMENU ----------------
#     def draw_submenu(self):
#         self.win.blit(self.background_image, (0, 0))

#         buttons = []
#         num_items = len(self.submenu_items)
#         submenu_height = num_items * SUBMENU_SPACING
#         top_margin = (HEIGHT - submenu_height) // 2

#         for i, item in enumerate(self.submenu_items):
#             y = top_margin + i * SUBMENU_SPACING
#             button = Button(WIDTH // 2, y, 200, 30, item, self.menu_font)
#             buttons.append(button)
#             button.draw(self.win)

#         pygame.display.update()
#         self.handle_input_submenu(buttons)

#     # ---------------- DIFFICULTY MENU ----------------
#     def draw_difficulty_menu(self):
#         self.win.blit(self.background_image, (0, 0))

#         buttons = []
#         for i, item in enumerate(self.difficulty_items):
#             button = Button(WIDTH // 2, 200 + i * 60, 200, 40, item, self.menu_font)
#             buttons.append(button)
#             button.draw(self.win)

#         pygame.display.update()
#         self.handle_input_difficulty(buttons)



#     def draw_rules(self):
#         self.win.blit(self.background_image, (0, 0))

#         rules = [
#         "OTHELLO GAME RULES",
#         "",
#         "1. Played on an 8x8 board",
#         "2. Black always moves first",
#         "3. Capture opponent discs by trapping them",
#         "4. Trapped discs flip to your color",
#         "5. You must play a valid move if available",
#         "6. Game ends when no moves remain",
#         "7. Player with most discs wins",
#     ]

#         font = pygame.font.SysFont(None, 24)

#         for i, line in enumerate(rules):
#             text_surface = font.render(line, True, BLACK_COLOR)
#             self.win.blit(text_surface, (40, 100 + i * 30))

    
#         back_button = Button(
#             WIDTH // 2,
#             HEIGHT - 80,
#             200,
#             40,
#             "Back",
#             self.menu_font,
#             self.draw_menu
#     )
#         back_button.draw(self.win)

#         pygame.display.update()

#     # Handle clicks
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()

#                 if event.type == pygame.MOUSEBUTTONDOWN:
#                     if back_button.check_collision(event.pos):
#                         self.draw_menu()

#     # ---------------- CREDIT ----------------
#     # def draw_credit(self):
#     #     self.win.blit(self.background_image, (0, 0))

#     #     credit_text = "Written and Developed by AmirHossein Roodaki"
#     #     github_link = "GitHub: /Roodaki"

#     #     font = pygame.font.SysFont(None, 24)

#     #     credit_surface = font.render(credit_text, True, BLACK_COLOR)
#     #     github_surface = font.render(github_link, True, BLACK_COLOR)

#     #     self.win.blit(credit_surface, (50, HEIGHT // 2 - 40))
#     #     self.win.blit(github_surface, (50, HEIGHT // 2))

#     #     self.return_button = Button(
#     #         WIDTH // 2, HEIGHT // 2 + 80, 200, 40,
#     #         "Return to Main Menu", self.menu_font, self.draw_menu
#     #     )
#     #     self.return_button.draw(self.win)

#     #     pygame.display.update()
#     #     self.handle_input_credit()

#     # ---------------- INPUT HANDLERS ----------------
#     def handle_input_menu(self, buttons):
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()

#                 if event.type == pygame.MOUSEBUTTONDOWN:
#                     for button in buttons:
#                         if button.check_collision(event.pos):
#                             if button.text == "Start Game":
#                                 self.draw_submenu()
#                             elif button.text == "Game Rules":
#                                 self.draw_rules()
#                             elif button.text == "Exit":
#                                 pygame.quit()
#                                 sys.exit()

#     def handle_input_submenu(self, buttons):
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()

#                 if event.type == pygame.MOUSEBUTTONDOWN:
#                     for button in buttons:
#                         if button.check_collision(event.pos):

#                             if button.text == "Multi-player\n(Play with Friend)":
#                                 game = OthelloGUI()
#                                 game.run_game(return_to_menu_callback=self.draw_menu)

#                             elif button.text == "Single-player\n(Play with AI)":
#                                 self.draw_difficulty_menu()   # 🔥 KEY FIX

#                             elif button.text == "Return to Main Menu":
#                                 self.draw_menu()

#     def handle_input_difficulty(self, buttons):
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()

#                 if event.type == pygame.MOUSEBUTTONDOWN:
#                     for button in buttons:
#                         if button.check_collision(event.pos):

#                             if button.text == "Easy":
#                                 game = OthelloGUI(player_mode="ai")
#                                 game.run_game(return_to_menu_callback=self.draw_menu)

#                             elif button.text == "Medium":
#                                 game = OthelloGUI(player_mode="ai")
#                                 game.run_game(return_to_menu_callback=self.draw_menu)

#                             elif button.text == "Hard":
#                                 game = OthelloGUI(player_mode="ai")
#                                 game.run_game(return_to_menu_callback=self.draw_menu)

#                             elif button.text == "Back":
#                                 self.draw_submenu()

#     def handle_input_credit(self):
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()

#                 if event.type == pygame.MOUSEBUTTONDOWN:
#                     if self.return_button.check_collision(event.pos):
#                         self.draw_menu()


# def run_menu():
#     menu = Menu()
#     menu.draw_menu()







































# import pygame
# import sys
# from GUI.othello_gui import OthelloGUI, run_game
# from GUI.button_gui import Button

# # Constants and colors
# WIDTH, HEIGHT = 480, 560
# WHITE_COLOR = (255, 255, 255)
# BLACK_COLOR = (0, 0, 0)
# GREEN_COLOR = (0, 128, 0)
# SUBMENU_SPACING = 75  # Increase the vertical spacing between submenu buttons
# BACKGROUND_IMAGE_PATH = "./utils/pictures/othello_blurred.jpg"


# class Menu:
#     def __init__(self):
#         """
#         A class representing the main menu of the Othello game.

#         Attributes:
#             win (pygame.Surface): The Pygame window.
#             menu_font (pygame.font.Font): The font used for rendering the menu items.
#             menu_items (list): The list of menu items displayed on the main menu.
#             submenu_items (list): The list of submenu items displayed after selecting "Start Game".
#             return_button (Button): The button to return to the main menu from the credit screen.
#         """
#         self.difficulty_items = ["Easy", "Medium", "Hard", "Back"]
#         self.win = self.initialize_pygame()
#         self.menu_font = pygame.font.SysFont(None, 36)
#         self.menu_items = ["Start Game", "Credit", "Exit"]
#         self.submenu_items = [
#             "Multi-player\n(Play with Friend)",
#             "Single-player\n(Play with AI)",
#             "Return to Main Menu",  # Add "Return to Main Menu" option
#         ]
#         self.return_button = None
#         self.background_image = pygame.image.load(BACKGROUND_IMAGE_PATH)
#         self.background_image = pygame.transform.scale(
#             self.background_image, (WIDTH, HEIGHT)
#         )

#     def initialize_pygame(self):
#         """
#         Initialize Pygame and create a window for the main menu.

#         Returns:
#             pygame.Surface: The Pygame window.
#         """
#         pygame.init()
#         win = pygame.display.set_mode((WIDTH, HEIGHT))
#         pygame.display.set_caption("Othello - Main Menu")
#         return win

#     def draw_menu(self):
#         """
#         Draw the main menu on the Pygame window.
#         """
#         self.win.blit(self.background_image, (0, 0))  # Draw the background image

#         buttons = []
#         for i, item in enumerate(self.menu_items):
#             button = Button(
#                 WIDTH // 2, 200 + i * 50, 200, 40, item, self.menu_font
#             )  # Adjust vertical position to accommodate the picture
#             buttons.append(button)
#             button.draw(self.win)

#         pygame.display.update()
#         self.handle_input_menu(buttons)

#     def draw_submenu(self):
#         """
#         Draw the submenu on the Pygame window.
#         """
#         def draw_difficulty_menu(self):
#             self.win.blit(self.background_image, (0, 0))

#             buttons = []
#             for i, item in enumerate(self.difficulty_items):
#                 button = Button(WIDTH // 2, 200 + i * 60, 200, 40, item, self.menu_font)
#                 buttons.append(button)
#                 button.draw(self.win)

#             pygame.display.update()
#             self.handle_input_difficulty(buttons)


#         self.win.blit(self.background_image, (0, 0))  # Draw the background image

#         buttons = []
#         num_submenu_items = len(self.submenu_items)
#         submenu_height = num_submenu_items * SUBMENU_SPACING
#         submenu_top_margin = (HEIGHT - submenu_height) // 2

#         for i, item in enumerate(self.submenu_items):
#             button_y = submenu_top_margin + i * SUBMENU_SPACING
#             button = Button(
#                 WIDTH // 2, button_y, 200, 30, item, self.menu_font
#             )  # Adjust height to 30
#             buttons.append(button)
#             button.draw(self.win)

#         pygame.display.update()
#         self.handle_input_submenu(buttons)

#     def draw_credit(self):
#         """
#         Draw the credit screen on the Pygame window.
#         """
#         self.win.blit(self.background_image, (0, 0))  # Draw the background image

#         credit_text = "Written and Developed by AmirHossein Roodaki"
#         github_link = "GitHub: /Roodaki"
#         return_button_text = "Return to Main Menu"

#         credit_font = pygame.font.SysFont(None, 24)
#         github_font = pygame.font.SysFont(None, 20)
#         return_button_font = pygame.font.SysFont(None, 30)

#         credit_surface = credit_font.render(credit_text, True, BLACK_COLOR)
#         github_surface = github_font.render(github_link, True, BLACK_COLOR)

#         credit_rect = credit_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
#         github_rect = github_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))

#         self.return_button = Button(
#             WIDTH // 2,
#             HEIGHT // 2 + 40,
#             200,
#             40,
#             return_button_text,
#             return_button_font,
#             self.draw_menu,
#         )
#         self.return_button.draw(self.win)

#         # Wrap and render the credit text if it exceeds the window width
#         credit_lines = []
#         words = credit_text.split()
#         current_line = ""
#         for word in words:
#             if (
#                 credit_font.size(current_line + word)[0] > WIDTH - 40
#             ):  # 40 is the padding
#                 credit_lines.append(current_line)
#                 current_line = word + " "
#             else:
#                 current_line += word + " "
#         credit_lines.append(current_line)

#         # Display the credit text line by line
#         for i, line in enumerate(credit_lines):
#             line_surface = credit_font.render(line, True, BLACK_COLOR)
#             line_rect = line_surface.get_rect(
#                 center=(WIDTH // 2, HEIGHT // 2 - 40 + i * 30)
#             )
#             self.win.blit(line_surface, line_rect)

#         self.win.blit(github_surface, github_rect)

#         pygame.display.update()
#         self.handle_input_credit()

#     def handle_input_menu(self, buttons):
#         """
#         Handle input events for the main menu.

#         Parameters:
#             buttons (list): The list of buttons in the main menu.
#         """
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()

#                 if event.type == pygame.MOUSEBUTTONDOWN:
#                     x, y = event.pos
#                     for button in buttons:
#                         if button.check_collision((x, y)):
#                             if button.text == "Start Game":
#                                 self.draw_submenu()
#                             elif button.text == "Credit":
#                                 self.draw_credit()
#                             elif button.text == "Exit":
#                                 pygame.quit()
#                                 sys.exit()
#     def handle_input_difficulty(self, buttons):
#     while True:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()

#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 x, y = event.pos
#                 for button in buttons:
#                     if button.check_collision((x, y)):

#                         if button.text == "Easy":
#                             othello_gui = OthelloGUI(player_mode="ai", difficulty="easy")
#                             othello_gui.run_game(return_to_menu_callback=self.draw_menu)

#                         elif button.text == "Medium":
#                             othello_gui = OthelloGUI(player_mode="ai", difficulty="medium")
#                             othello_gui.run_game(return_to_menu_callback=self.draw_menu)

#                         elif button.text == "Hard":
#                             othello_gui = OthelloGUI(player_mode="ai", difficulty="hard")
#                             othello_gui.run_game(return_to_menu_callback=self.draw_menu)

#                         elif button.text == "Back":
#                             self.draw_submenu()

#     # def handle_input_submenu(self, buttons):
#     #     """
#     #     Handle input events for the submenu.

#     #     Parameters:
#     #         buttons (list): The list of buttons in the submenu.
#     #     """
#     #     while True:
#     #         for event in pygame.event.get():
#     #             if event.type == pygame.QUIT:
#     #                 pygame.quit()
#     #                 sys.exit()

#     #             if event.type == pygame.MOUSEBUTTONDOWN:
#     #                 x, y = event.pos
#     #                 for button in buttons:
#     #                     if button.check_collision((x, y)):
#     #                         if button.text == "Multi-player\n(Play with Friend)":
#     #                             othello_gui = OthelloGUI()
#     #                             # Pass the draw_menu function as a callback to return to the main menu
#     #                             othello_gui.run_game(
#     #                                 return_to_menu_callback=self.draw_menu
#     #                             )

#     #                         elif button.text == "Single-player\n(Play with AI)":
#     #                             othello_gui = OthelloGUI(player_mode="ai")
#     #                             # Pass the draw_menu function as a callback to return to the main menu
#     #                             othello_gui.run_game(
#     #                                 return_to_menu_callback=self.draw_menu
#     #                             )

#     #                         elif button.text == "Return to Main Menu":
#     #                             self.draw_menu()  # Go back to the main menu

#     def run_single_player_game(self):
#         """
#         Start a single-player game with AI.
#         """
#         # Pass "ai" as the player_mode to indicate the single-player mode with AI
#         othello_gui = OthelloGUI(player_mode="ai")
#         othello_gui.run_game()

#     def handle_input_credit(self):
#         """
#         Handle input events for the credit screen.
#         """
#         while True:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     pygame.quit()
#                     sys.exit()

#                 if event.type == pygame.MOUSEBUTTONDOWN:
#                     x, y = event.pos
#                     if self.return_button.check_collision((x, y)):
#                         self.perform_action(self.return_button.action)

#     def perform_action(self, action):
#         """
#         Perform the specified action.

#         Parameters:
#             action (callable): The function to be called as the action.
#         """
#         if action is None:
#             pygame.quit()
#             sys.exit()
#         else:
#             action()


# def run_menu():
#     """
#     Start the main menu of the Othello game.
#     """
#     menu = Menu()
#     menu.draw_menu()
