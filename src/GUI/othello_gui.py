import pygame
import sys
from othello_game import OthelloGame
from ai_agent import get_best_move
 
# ── Colours ──────────────────────────────────────────────
BLACK_COLOR   = (0,   0,   0)
WHITE_COLOR   = (255, 255, 255)
BOARD_GREEN   = (30,  110,  50)   # richer green
GRID_COLOR    = (20,   80,  35)
BG_COLOR      = (18,   18,  30)   # dark sidebar bg
PANEL_COLOR   = (28,   28,  46)
ACCENT        = (88,  166, 255)   # blue highlight
VALID_COLOR   = (255, 220,  50, 120)  # translucent yellow hint
TEXT_LIGHT    = (220, 220, 220)
TEXT_DIM      = (140, 140, 160)
BLACK_DISC    = (30,   30,  30)
WHITE_DISC    = (240, 240, 240)
SHADOW_COLOR  = (0,    0,   0, 80)
 
BOARD_CELLS   = 8
SQUARE_SIZE   = 72          # each cell
BOARD_PX      = BOARD_CELLS * SQUARE_SIZE   # 576
SIDE_W        = 220         # right panel width
TOP_H         = 60          # top bar height
WIN_W         = BOARD_PX + SIDE_W           # 796
WIN_H         = BOARD_PX + TOP_H            # 636
 
 
class OthelloGUI:
    def __init__(self, player_mode="human", difficulty="medium"):
        self.player_mode = player_mode
        self.difficulty  = difficulty
        self.depth = {"easy": 2, "medium": 3, "hard": 5}.get(difficulty, 3)
 
        self.win = self._init_pygame()
        self.game = OthelloGame(player_mode=player_mode)
 
        self.font_lg  = pygame.font.SysFont("segoeui", 28, bold=True)
        self.font_md  = pygame.font.SysFont("segoeui", 22)
        self.font_sm  = pygame.font.SysFont("segoeui", 17)
 
        self.message         = ""
        self.invalid_message = ""
        self.back_button_rect = pygame.Rect(0, 0, 0, 0)
 
        self.flip_sound     = pygame.mixer.Sound("./utils/sounds/disk_flip.mp3")
        self.end_game_sound = pygame.mixer.Sound("./utils/sounds/end_game.mp3")
        self.invalid_sound  = pygame.mixer.Sound("./utils/sounds/invalid_play.mp3")
 
    # ── Setup ───────────────────────────────────────────────
    def _init_pygame(self):
        pygame.init()
        # win = pygame.display.set_mode((WIN_W, WIN_H))  
        win = pygame.display.set_mode((1100, 720)) # normal windowed — taskbar stays!
        pygame.display.set_caption("Othello  ·  Minimax AI")
        return win
 
    # ── Board origin (offset by top bar) ────────────────────
    def _cell_origin(self, row, col):
        x = col * SQUARE_SIZE
        y = TOP_H + row * SQUARE_SIZE
        return x, y
 
    def _cell_from_mouse(self, mx, my):
        if mx >= BOARD_PX or my < TOP_H:
            return None, None
        col = mx // SQUARE_SIZE
        row = (my - TOP_H) // SQUARE_SIZE
        if 0 <= row < BOARD_CELLS and 0 <= col < BOARD_CELLS:
            return row, col
        return None, None
 
    # ── Drawing ──────────────────────────────────────────────
    def draw_board(self):
        self.win.fill(BG_COLOR)
        self._draw_top_bar()
        self._draw_grid()
        self._draw_valid_hints()
        self._draw_discs()
        self._draw_side_panel()
        pygame.display.update()
 
    def _draw_top_bar(self):
        bar = pygame.Rect(0, 0, WIN_W, TOP_H)
        pygame.draw.rect(self.win, PANEL_COLOR, bar)
 
        # Title
        title = self.font_lg.render("OTHELLO", True, ACCENT)
        self.win.blit(title, (16, 15))
 
        # Whose turn
        turn_name = "Black" if self.game.current_player == 1 else "White"
        turn_color = (60, 60, 60) if self.game.current_player == 1 else (230, 230, 230)
 
        pygame.draw.circle(self.win, turn_color, (200, 30), 12)
        pygame.draw.circle(self.win, (180, 180, 180), (200, 30), 12, 2)
 
        lbl = self.font_md.render(f"{turn_name}'s Turn", True, TEXT_LIGHT)
        self.win.blit(lbl, (220, 18))
 
        # Status message (AI thinking / invalid)
        if self.message:
            msg = self.font_sm.render(self.message, True, ACCENT)
            self.win.blit(msg, (420, 20))
        if self.invalid_message:
            msg = self.font_sm.render(self.invalid_message, True, (255, 100, 100))
            self.win.blit(msg, (420, 20))
 
    def _draw_grid(self):
        for row in range(BOARD_CELLS):
            for col in range(BOARD_CELLS):
                x, y = self._cell_origin(row, col)
                # Alternate cell shading
                shade = (32, 115, 52) if (row + col) % 2 == 0 else BOARD_GREEN
                pygame.draw.rect(self.win, shade, (x, y, SQUARE_SIZE, SQUARE_SIZE))
                pygame.draw.rect(self.win, GRID_COLOR, (x, y, SQUARE_SIZE, SQUARE_SIZE), 1)
 
        # Corner dots
        for r, c in [(2,2),(2,6),(6,2),(6,6)]:
            x, y = self._cell_origin(r, c)
            cx = x + SQUARE_SIZE // 2
            cy = y + SQUARE_SIZE // 2
            pygame.draw.circle(self.win, GRID_COLOR, (cx, cy), 4)
 
    def _draw_valid_hints(self):
        valid_moves = [
            (r, c) for r in range(BOARD_CELLS)
            for c in range(BOARD_CELLS)
            if self.game.is_valid_move(r, c)
        ]
        hint_surf = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(hint_surf, (255, 220, 50, 90),
                           (SQUARE_SIZE//2, SQUARE_SIZE//2), 10)
        for row, col in valid_moves:
            x, y = self._cell_origin(row, col)
            self.win.blit(hint_surf, (x, y))
 
    def _draw_discs(self):
        for row in range(BOARD_CELLS):
            for col in range(BOARD_CELLS):
                val = self.game.board[row][col]
                if val == 0:
                    continue
                x, y = self._cell_origin(row, col)
                cx = x + SQUARE_SIZE // 2
                cy = y + SQUARE_SIZE // 2
                r  = SQUARE_SIZE // 2 - 6
 
                # Shadow
                shadow = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE), pygame.SRCALPHA)
                pygame.draw.circle(shadow, (0, 0, 0, 70), (SQUARE_SIZE//2 + 3, SQUARE_SIZE//2 + 3), r)
                self.win.blit(shadow, (x, y))
 
                color = BLACK_DISC if val == 1 else WHITE_DISC
                pygame.draw.circle(self.win, color, (cx, cy), r)
 
                # Sheen highlight
                highlight = (80, 80, 80) if val == 1 else (255, 255, 255)
                pygame.draw.circle(self.win, highlight, (cx - r//4, cy - r//4), r//4)
 
    def _draw_side_panel(self):
        px = BOARD_PX
        panel = pygame.Rect(px, 0, SIDE_W, WIN_H)
        pygame.draw.rect(self.win, PANEL_COLOR, panel)
        pygame.draw.line(self.win, ACCENT, (px, 0), (px, WIN_H), 2)
 
        black_count = sum(
            1 for r in range(BOARD_CELLS)
            for c in range(BOARD_CELLS) if self.game.board[r][c] == 1
        )
        white_count = sum(
            1 for r in range(BOARD_CELLS)
            for c in range(BOARD_CELLS) if self.game.board[r][c] == -1
        )
        total = black_count + white_count or 1
 
        y = 80
        # ── Score header
        hdr = self.font_md.render("SCORE", True, ACCENT)
        self.win.blit(hdr, (px + 70, y)); y += 40
 
        # Black score
        pygame.draw.circle(self.win, BLACK_DISC, (px + 36, y + 14), 14)
        pygame.draw.circle(self.win, (120,120,120), (px + 36, y + 14), 14, 2)
        b_lbl = self.font_lg.render(str(black_count), True, TEXT_LIGHT)
        self.win.blit(b_lbl, (px + 60, y + 2)); y += 46
 
        # White score
        pygame.draw.circle(self.win, WHITE_DISC, (px + 36, y + 14), 14)
        pygame.draw.circle(self.win, (120,120,120), (px + 36, y + 14), 14, 2)
        w_lbl = self.font_lg.render(str(white_count), True, TEXT_LIGHT)
        self.win.blit(w_lbl, (px + 60, y + 2)); y += 54
 
        # Progress bar
        bar_bg = pygame.Rect(px + 16, y, SIDE_W - 32, 14)
        pygame.draw.rect(self.win, WHITE_DISC, bar_bg, border_radius=7)
        black_w = int((SIDE_W - 32) * black_count / total)
        if black_w:
            pygame.draw.rect(self.win, BLACK_DISC,
                             pygame.Rect(px+16, y, black_w, 14), border_radius=7)
        y += 40
 
        # Difficulty badge
        diff_text = f"Difficulty: {self.difficulty.capitalize()}"
        diff_lbl = self.font_sm.render(diff_text, True, TEXT_DIM)
        self.win.blit(diff_lbl, (px + 16, y)); y += 34
 
        # Mode badge
        mode_text = "vs AI" if self.player_mode == "ai" else "2 Players"
        mode_lbl = self.font_sm.render(mode_text, True, TEXT_DIM)
        self.win.blit(mode_lbl, (px + 16, y)); y += 50
 
        # Back button
        self.back_button_rect = pygame.Rect(px + 30, WIN_H - 70, SIDE_W - 60, 44)
        pygame.draw.rect(self.win, ACCENT, self.back_button_rect, border_radius=10)
        btn_lbl = self.font_md.render("← Back", True, BLACK_COLOR)
        self.win.blit(btn_lbl, (px + 62, WIN_H - 58))
 
    # ── Input ────────────────────────────────────────────────
    def handle_input(self, return_to_menu_callback=None):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
 
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if return_to_menu_callback:
                    return_to_menu_callback()
                return
 
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
 
                if self.back_button_rect.collidepoint(mx, my):
                    if return_to_menu_callback:
                        return_to_menu_callback()
                    return
 
                row, col = self._cell_from_mouse(mx, my)
                if row is None:
                    return
 
                if self.game.is_valid_move(row, col):
                    self.game.make_move(row, col)
                    self.invalid_message = ""
                    self.flip_sound.play()
                else:
                    self.invalid_message = "Invalid move!"
                    self.invalid_sound.play()
 
    # ── Main loop ────────────────────────────────────────────
    def run_game(self, return_to_menu_callback=None):
        while not self.game.is_game_over():
            self.handle_input(return_to_menu_callback)
 
            if self.game.player_mode == "ai" and self.game.current_player == -1:
                self.message = "AI is thinking…"
                self.draw_board()
                # move = get_best_move(self.game, self.depth)
                # pygame.time.delay(300)
                # self.game.make_move(*move)
                move = get_best_move(self.game, self.depth)
                pygame.time.delay(300)
                if move is not None:
                    self.game.make_move(*move)
                else:
        # AI has no valid moves, skip its turn
                    self.game.current_player *= -1
                self.message = ""
 
            self.draw_board()
 
        # Game over
        winner = self.game.get_winner()
        self.message = {1: "⬛ Black wins!", -1: "⬜ White wins!"}.get(winner, "It's a Draw!")
        self.invalid_message = ""
        self.draw_board()
        self.end_game_sound.play()
        pygame.time.delay(2500)
 
        if return_to_menu_callback:
            return_to_menu_callback()
 
 
def run_game():
    game = OthelloGUI()
    game.run_game()

























# import pygame
# import sys
# from othello_game import OthelloGame
# from ai_agent import get_best_move

# BLACK_COLOR = (0, 0, 0)
# WHITE_COLOR = (255, 255, 255)
# GREEN_COLOR = (0, 128, 0)


# class OthelloGUI:
#     def __init__(self, player_mode="human", difficulty="medium"):
#         self.player_mode = player_mode
#         self.difficulty = difficulty

#         if self.difficulty == "easy":
#             self.depth = 2
#         elif self.difficulty == "medium":
#             self.depth = 3
#         else:
#             self.depth = 5

#         self.win = self.initialize_pygame()
#         self.WIDTH, self.HEIGHT = self.win.get_size()

#         self.BOARD_SIZE = 8
#         self.SQUARE_SIZE = (self.HEIGHT - 100) // self.BOARD_SIZE

#         self.game = OthelloGame(player_mode=player_mode)

#         self.message_font = pygame.font.SysFont(None, 24)
#         self.message = ""
#         self.invalid_move_message = ""

#         self.flip_sound = pygame.mixer.Sound("./utils/sounds/disk_flip.mp3")
#         self.end_game_sound = pygame.mixer.Sound("./utils/sounds/end_game.mp3")
#         self.invalid_play_sound = pygame.mixer.Sound("./utils/sounds/invalid_play.mp3")

#     def initialize_pygame(self):
#         pygame.init()
#         # win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#         win = pygame.display.set_mode((900, 900))
#         pygame.display.set_caption("Othello")
#         return win

#     def draw_board(self):
#         self.win.fill(GREEN_COLOR)

#         # -------- BOARD --------
#         for row in range(self.BOARD_SIZE):
#             for col in range(self.BOARD_SIZE):
#                 x = col * self.SQUARE_SIZE
#                 y = row * self.SQUARE_SIZE

#                 pygame.draw.rect(
#                     self.win,
#                     BLACK_COLOR,
#                     (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE),
#                     1,
#                 )

#                 if self.game.board[row][col] == 1:
#                     pygame.draw.circle(
#                         self.win,
#                         BLACK_COLOR,
#                         (int(x + self.SQUARE_SIZE / 2), int(y + self.SQUARE_SIZE / 2)),
#                         self.SQUARE_SIZE // 2 - 4,
#                     )
#                 elif self.game.board[row][col] == -1:
#                     pygame.draw.circle(
#                         self.win,
#                         WHITE_COLOR,
#                         (int(x + self.SQUARE_SIZE / 2), int(y + self.SQUARE_SIZE / 2)),
#                         self.SQUARE_SIZE // 2 - 4,
#                     )

#         # -------- MESSAGE AREA --------
#         message_area_rect = pygame.Rect(
#             0,
#             self.BOARD_SIZE * self.SQUARE_SIZE,
#             self.WIDTH,
#             self.HEIGHT - (self.BOARD_SIZE * self.SQUARE_SIZE),
#         )
#         pygame.draw.rect(self.win, WHITE_COLOR, message_area_rect)

#         # Turn message
#         turn = "Black" if self.game.current_player == 1 else "White"
#         text = self.message_font.render(f"{turn}'s turn", True, BLACK_COLOR)
#         self.win.blit(text, (20, self.BOARD_SIZE * self.SQUARE_SIZE + 10))

#         # Invalid message
#         if self.invalid_move_message:
#             text = self.message_font.render(self.invalid_move_message, True, BLACK_COLOR)
#             self.win.blit(text, (20, self.BOARD_SIZE * self.SQUARE_SIZE + 40))

#         # -------- BACK BUTTON --------
#         button_y = self.BOARD_SIZE * self.SQUARE_SIZE + 10
#         self.back_button_rect = pygame.Rect(self.WIDTH - 140, button_y, 120, 40)

#         pygame.draw.rect(self.win, (70, 130, 180), self.back_button_rect)
#         font = pygame.font.SysFont(None, 28)
#         text = font.render("Back", True, (0, 0, 0))
#         self.win.blit(text, (self.WIDTH - 110, button_y + 8))

#         pygame.display.update()

#     def handle_input(self, return_to_menu_callback=None):
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()

#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 x, y = event.pos

#                 # Back button
#                 if self.back_button_rect.collidepoint(x, y):
#                     if return_to_menu_callback:
#                         return_to_menu_callback()
#                     return

#                 col = x // self.SQUARE_SIZE
#                 row = y // self.SQUARE_SIZE

#                 if self.game.is_valid_move(row, col):
#                     self.game.make_move(row, col)
#                     self.invalid_move_message = ""
#                     self.flip_sound.play()
#                 else:
#                     self.invalid_move_message = "Invalid move!"
#                     self.invalid_play_sound.play()

#     def run_game(self, return_to_menu_callback=None):
#         running = True

#         while running and not self.game.is_game_over():
#             self.handle_input(return_to_menu_callback)

#             if self.game.player_mode == "ai" and self.game.current_player == -1:
#                 self.message = "AI thinking..."
#                 self.draw_board()

#                 move = get_best_move(self.game, self.depth)
#                 pygame.time.delay(300)
#                 self.game.make_move(*move)

#             self.draw_board()

#         # -------- GAME OVER --------
#         winner = self.game.get_winner()

#         if winner == 1:
#             self.message = "Black wins!"
#         elif winner == -1:
#             self.message = "White wins!"
#         else:
#             self.message = "Draw!"

#         self.draw_board()
#         self.end_game_sound.play()
#         pygame.time.delay(2000)

#         # ✅ FIX: RETURN TO MENU INSTEAD OF EXIT
#         if return_to_menu_callback:
#             return_to_menu_callback()


# def run_game():
#     game = OthelloGUI()
#     game.run_game()








# import pygame
# import sys
# from othello_game import OthelloGame
# from ai_agent import get_best_move

# # Constants and colors
# # WIDTH, HEIGHT = 480, 560
# # self.WIDTH, self.HEIGHT = win.get_size()
# # BOARD_SIZE = 8
# SQUARE_SIZE = (HEIGHT - 80) // BOARD_SIZE


# BLACK_COLOR = (0, 0, 0)
# WHITE_COLOR = (255, 255, 255)
# GREEN_COLOR = (0, 128, 0)


# class OthelloGUI:
#     def __init__(self, player_mode="human", difficulty="medium"):
#         self.player_mode = player_mode
#         self.difficulty = difficulty
#         if self.difficulty == "easy":
#             self.depth = 2
#         elif self.difficulty == "medium":
#             self.depth = 3
#         else:
#             self.depth = 5
#         self.win = self.initialize_pygame()
#         self.WIDTH, self.HEIGHT = self.win.get_size()  
#         self.BOARD_SIZE = 8
#         BOARD_WIDTH = int(self.WIDTH * 0.6)
#         PANEL_WIDTH = self.WIDTH - BOARD_WIDTH
#         SQUARE_SIZE = BOARD_WIDTH // 8 
#         self.game = OthelloGame(player_mode=player_mode)
#         self.message_font = pygame.font.SysFont(None, 24)
#         self.message = ""
#         self.invalid_move_message = ""
#         self.flip_sound = pygame.mixer.Sound("./utils/sounds/disk_flip.mp3")
#         self.end_game_sound = pygame.mixer.Sound("./utils/sounds/end_game.mp3")
#         self.invalid_play_sound = pygame.mixer.Sound("./utils/sounds/invalid_play.mp3")

#     def initialize_pygame(self):
#         """
#         Initialize the Pygame library and create the game window.

#         Returns:
#             pygame.Surface: The Pygame surface representing the game window.
#         """
#         pygame.init()
#         win = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
#         pygame.display.set_caption("Othello")
#         return win

#     def draw_board(self):
#         """
#         Draw the Othello game board and messaging area on the window.
#         """

#         # Back button
        
#         self.win.fill((30, 30, 30))  # dark background

#         # Draw board grid and disks
#         for row in range(self.BOARD_SIZE):
#             for col in range(self.BOARD_SIZE):
#                 x = col * SQUARE_SIZE
#                 y = row * SQUARE_SIZE
#                 pygame.draw.rect(
#                     self.win,
#                     BLACK_COLOR,
#                     (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
#                     1,
#                 )
#                 if self.game.board[row][col] == 1:
#                     pygame.draw.circle(
#                         self.win,
#                         BLACK_COLOR,
#                         ((col + 0.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE),
#                         SQUARE_SIZE // 2 - 4,
#                     )
#                 elif self.game.board[row][col] == -1:
#                     pygame.draw.circle(
#                         self.win,
#                         WHITE_COLOR,
#                         ((col + 0.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE),
#                         SQUARE_SIZE // 2 - 4,
#                     )

#         # Draw messaging area
#         message_area_rect = pygame.Rect(
#             0, BOARD_SIZE * SQUARE_SIZE, WIDTH, HEIGHT - (BOARD_SIZE * SQUARE_SIZE)
#         )
#         pygame.draw.rect(self.win, WHITE_COLOR, message_area_rect)

#         # Draw player's turn message
#         player_turn = "Black's" if self.game.current_player == 1 else "White's"
#         turn_message = f"{player_turn} turn"
#         message_surface = self.message_font.render(turn_message, True, BLACK_COLOR)
#         message_rect = message_surface.get_rect(
#             center=(WIDTH // 2, (HEIGHT + BOARD_SIZE * SQUARE_SIZE) // 2 - 20)
#         )
#         self.win.blit(message_surface, message_rect)

#         # Draw invalid move message
#         if self.message:
#             invalid_move_message = self.message
#             message_surface = self.message_font.render(
#                 invalid_move_message, True, BLACK_COLOR
#             )
#             message_rect = message_surface.get_rect(
#                 center=(WIDTH // 2, (HEIGHT + BOARD_SIZE * SQUARE_SIZE) // 2 + 20)
#             )
#             self.win.blit(message_surface, message_rect)

#         # Draw invalid move message
#         if self.invalid_move_message:
#             message_surface = self.message_font.render(
#                 self.invalid_move_message, True, BLACK_COLOR
#             )
#             message_rect = message_surface.get_rect(
#                 center=(WIDTH // 2, (HEIGHT + BOARD_SIZE * SQUARE_SIZE) // 2 + 20)
#             )
#             self.win.blit(message_surface, message_rect)

        
#         # self.back_button_rect = pygame.Rect(10, 10, 120, 40)
#         # # pygame.draw.rect(self.win, (200, 200, 200), self.back_button_rect)
#         # pygame.draw.rect(self.win, (70, 130, 180), self.back_button_rect)

#         # font = pygame.font.SysFont(None, 24)
#         # text = font.render("Back", True, (0, 0, 0))
#         # self.win.blit(text, (20, 20))
#         # Back button inside message area
#         button_y = BOARD_SIZE * SQUARE_SIZE + 20

#         self.back_button_rect = pygame.Rect(WIDTH - 140, button_y, 120, 40)
#         # pygame.draw.rect(self.win, (70, 130, 180), self.back_button_rect)
#         pygame.draw.rect(self.win, (255, 0, 0), self.back_button_rect)
#         font = pygame.font.SysFont(None, 28)
#         text = font.render("Back", True, (255, 255, 255))
#         self.win.blit(text, (WIDTH - 110, button_y + 10))

#         # -------- RIGHT PANEL --------
#         panel_x = BOARD_WIDTH
#         pygame.draw.rect(self.win, (50, 50, 50), (panel_x, 0, PANEL_WIDTH, self.HEIGHT))
        
#         font = pygame.font.SysFont(None, 28)
        
#         # Title
#         title = font.render("Game Panel", True, (255, 255, 255))
#         self.win.blit(title, (panel_x + 20, 20))
        
#         # Current turn
#         turn = "Black" if self.game.current_player == 1 else "White"
#         turn_text = font.render(f"Turn: {turn}", True, (255, 255, 255))
#         self.win.blit(turn_text, (panel_x + 20, 70))

# # ai analysis
#         analysis = font.render("AI Analysis:", True, (255, 255, 255))
#         self.win.blit(analysis, (panel_x + 20, 130))
        
#         eval_text = font.render("Score: TBD", True, (200, 200, 200))
#         self.win.blit(eval_text, (panel_x + 20, 160))

# # coach
#         coach = font.render("Coach:", True, (255, 255, 255))
#         self.win.blit(coach, (panel_x + 20, 220))
        
#         tip = font.render("Try corners!", True, (200, 200, 200))
#         self.win.blit(tip, (panel_x + 20, 250))

# # analytics
#         analytics = font.render("Analytics:", True, (255, 255, 255))
#         self.win.blit(analytics, (panel_x + 20, 310))
        
#         moves = font.render("Moves: TBD", True, (200, 200, 200))
#         self.win.blit(moves, (panel_x + 20, 340))
# # controls
#         controls = font.render("Controls:", True, (255, 255, 255))
#         self.win.blit(controls, (panel_x + 20, 400))
        
#         ctrl_text = font.render("Click to place", True, (200, 200, 200))
#         self.win.blit(ctrl_text, (panel_x + 20, 430))


#         pygame.display.update()

#     def handle_input(self, return_to_menu_callback=None):
#         """
#         Handle user input events such as mouse clicks and game quitting.
#         """
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()

#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 x, y = event.pos
#                 # Back button click
#                 if self.back_button_rect.collidepoint(x, y):
#                     if return_to_menu_callback:
#                         return_to_menu_callback()
#                     return
#                 col = x // SQUARE_SIZE
#                 row = y // SQUARE_SIZE
#                 if self.game.is_valid_move(row, col):
#                     self.game.make_move(row, col)
#                     self.invalid_move_message = (
#                         ""  # Clear any previous invalid move message
#                     )
#                     self.flip_sound.play()  # Play flip sound effect
#                 else:
#                     self.invalid_move_message = "Invalid move! Try again."
#                     self.invalid_play_sound.play()  # Play invalid play sound effect

#     def run_game(self, return_to_menu_callback=None):
#         """
#         Run the main game loop until the game is over and display the result.
#         """
#         running = True
#         while running and not self.game.is_game_over():
#             self.handle_input(return_to_menu_callback)

#             # If it's the AI player's turn
#             if self.game.player_mode == "ai" and self.game.current_player == -1:
#                 self.message = "AI is thinking..."
#                 self.draw_board()  # Display the thinking message
#                 ai_move = get_best_move(self.game, self.depth)
#                 pygame.time.delay(500)  # Wait for a short time to show the message
#                 self.game.make_move(*ai_move)

#             self.message = ""  # Clear any previous messages
#             self.draw_board()

#         winner = self.game.get_winner()
#         if winner == 1:
#             self.message = "Black wins!"
#         elif winner == -1:
#             self.message = "White wins!"
#         else:
#             self.message = "It's a tie!"

#         self.draw_board()
#         self.end_game_sound.play()  # Play end game sound effect
#         pygame.time.delay(3000)  # Display the result for 2 seconds before returning

#         # Call the return_to_menu_callback if provided
#         if return_to_menu_callback:
#             running = False
#             return_to_menu_callback()


# def run_game():
#     """
#     Start and run the Othello game.
#     """
#     othello_gui = OthelloGUI()
#     othello_gui.run_game()
