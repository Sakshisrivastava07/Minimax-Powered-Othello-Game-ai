import pygame
import sys
from othello_game import OthelloGame
from ai_agent import get_best_move

# Constants and colors
WIDTH, HEIGHT = 480, 560
BOARD_SIZE = 8
SQUARE_SIZE = (HEIGHT - 80) // BOARD_SIZE
BLACK_COLOR = (0, 0, 0)
WHITE_COLOR = (255, 255, 255)
GREEN_COLOR = (0, 128, 0)


class OthelloGUI:
    def __init__(self, player_mode="human", difficulty="medium"):
        self.player_mode = player_mode
        self.difficulty = difficulty
        if self.difficulty == "easy":
            self.depth = 2
        elif self.difficulty == "medium":
            self.depth = 3
        else:
            self.depth = 5
        self.win = self.initialize_pygame()
        self.game = OthelloGame(player_mode=player_mode)
        self.message_font = pygame.font.SysFont(None, 24)
        self.message = ""
        self.invalid_move_message = ""
        self.flip_sound = pygame.mixer.Sound("./utils/sounds/disk_flip.mp3")
        self.end_game_sound = pygame.mixer.Sound("./utils/sounds/end_game.mp3")
        self.invalid_play_sound = pygame.mixer.Sound("./utils/sounds/invalid_play.mp3")

    def initialize_pygame(self):
        """
        Initialize the Pygame library and create the game window.

        Returns:
            pygame.Surface: The Pygame surface representing the game window.
        """
        pygame.init()
        win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Othello")
        return win

    def draw_board(self):
        """
        Draw the Othello game board and messaging area on the window.
        """

        # Back button
        
        self.win.fill(GREEN_COLOR)

        # Draw board grid and disks
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                pygame.draw.rect(
                    self.win,
                    BLACK_COLOR,
                    (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
                    1,
                )
                if self.game.board[row][col] == 1:
                    pygame.draw.circle(
                        self.win,
                        BLACK_COLOR,
                        ((col + 0.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE),
                        SQUARE_SIZE // 2 - 4,
                    )
                elif self.game.board[row][col] == -1:
                    pygame.draw.circle(
                        self.win,
                        WHITE_COLOR,
                        ((col + 0.5) * SQUARE_SIZE, (row + 0.5) * SQUARE_SIZE),
                        SQUARE_SIZE // 2 - 4,
                    )

        # Draw messaging area
        message_area_rect = pygame.Rect(
            0, BOARD_SIZE * SQUARE_SIZE, WIDTH, HEIGHT - (BOARD_SIZE * SQUARE_SIZE)
        )
        pygame.draw.rect(self.win, WHITE_COLOR, message_area_rect)

        # Draw player's turn message
        player_turn = "Black's" if self.game.current_player == 1 else "White's"
        turn_message = f"{player_turn} turn"
        message_surface = self.message_font.render(turn_message, True, BLACK_COLOR)
        message_rect = message_surface.get_rect(
            center=(WIDTH // 2, (HEIGHT + BOARD_SIZE * SQUARE_SIZE) // 2 - 20)
        )
        self.win.blit(message_surface, message_rect)

        # Draw invalid move message
        if self.message:
            invalid_move_message = self.message
            message_surface = self.message_font.render(
                invalid_move_message, True, BLACK_COLOR
            )
            message_rect = message_surface.get_rect(
                center=(WIDTH // 2, (HEIGHT + BOARD_SIZE * SQUARE_SIZE) // 2 + 20)
            )
            self.win.blit(message_surface, message_rect)

        # Draw invalid move message
        if self.invalid_move_message:
            message_surface = self.message_font.render(
                self.invalid_move_message, True, BLACK_COLOR
            )
            message_rect = message_surface.get_rect(
                center=(WIDTH // 2, (HEIGHT + BOARD_SIZE * SQUARE_SIZE) // 2 + 20)
            )
            self.win.blit(message_surface, message_rect)

        
        # self.back_button_rect = pygame.Rect(10, 10, 120, 40)
        # # pygame.draw.rect(self.win, (200, 200, 200), self.back_button_rect)
        # pygame.draw.rect(self.win, (70, 130, 180), self.back_button_rect)

        # font = pygame.font.SysFont(None, 24)
        # text = font.render("Back", True, (0, 0, 0))
        # self.win.blit(text, (20, 20))
        # Back button inside message area
        button_y = BOARD_SIZE * SQUARE_SIZE + 20

        self.back_button_rect = pygame.Rect(WIDTH - 140, button_y, 120, 40)
        # pygame.draw.rect(self.win, (70, 130, 180), self.back_button_rect)
        pygame.draw.rect(self.win, (255, 0, 0), self.back_button_rect)
        font = pygame.font.SysFont(None, 28)
        text = font.render("Back", True, (255, 255, 255))
        self.win.blit(text, (WIDTH - 110, button_y + 10))

        pygame.display.update()

    def handle_input(self, return_to_menu_callback=None):
        """
        Handle user input events such as mouse clicks and game quitting.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                # Back button click
                if self.back_button_rect.collidepoint(x, y):
                    if return_to_menu_callback:
                        return_to_menu_callback()
                    return
                col = x // SQUARE_SIZE
                row = y // SQUARE_SIZE
                if self.game.is_valid_move(row, col):
                    self.game.make_move(row, col)
                    self.invalid_move_message = (
                        ""  # Clear any previous invalid move message
                    )
                    self.flip_sound.play()  # Play flip sound effect
                else:
                    self.invalid_move_message = "Invalid move! Try again."
                    self.invalid_play_sound.play()  # Play invalid play sound effect

    def run_game(self, return_to_menu_callback=None):
        """
        Run the main game loop until the game is over and display the result.
        """
        running = True
        while running and not self.game.is_game_over():
            self.handle_input(return_to_menu_callback)

            # If it's the AI player's turn
            if self.game.player_mode == "ai" and self.game.current_player == -1:
                self.message = "AI is thinking..."
                self.draw_board()  # Display the thinking message
                ai_move = get_best_move(self.game, self.depth)
                pygame.time.delay(500)  # Wait for a short time to show the message
                self.game.make_move(*ai_move)

            self.message = ""  # Clear any previous messages
            self.draw_board()

        winner = self.game.get_winner()
        if winner == 1:
            self.message = "Black wins!"
        elif winner == -1:
            self.message = "White wins!"
        else:
            self.message = "It's a tie!"

        self.draw_board()
        self.end_game_sound.play()  # Play end game sound effect
        pygame.time.delay(3000)  # Display the result for 2 seconds before returning

        # Call the return_to_menu_callback if provided
        if return_to_menu_callback:
            running = False
            return_to_menu_callback()


def run_game():
    """
    Start and run the Othello game.
    """
    othello_gui = OthelloGUI()
    othello_gui.run_game()
