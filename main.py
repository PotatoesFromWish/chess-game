import pygame
from PIL import Image
import sys
import os

# Returns the correct file path whether running from source or a compiled executable
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

#Decides how many squares are created, the number written is multiplied by it self and that decides how many squares
board_size = 8


class Piece:
    SPRITE = {}
    _id_counter = 1

    #Initialises important piece information
    def __init__(self, color: str):
        self.color = color
        self.has_moved = False
        self.movement_enabled = True
        #Gives the piece a unique id by reading the current counter value then incrementing it for the next piece
        self.id = Piece._id_counter
        Piece._id_counter += 1
        self.in_check = False

    #Finds available moves by getting the directions from the subclass aka "Pawn", "Queen" and takes the first part of the direction and searches in that direction one square at a time and checks if it can go there if it can it writes the coordinates of the square to moves and sends them to the function caling it for more thourough search if it is legal.
    def move_validating(self, directions, move_by, from_row, from_col, board):
        moves = []
        for row_step, col_step in directions:
            for i in range(1, move_by):
                row = from_row + row_step * i
                col = from_col + col_step * i
                #Stops the code from searching through squares that dont exist
                if not (0 <= row <= board_size - 1 and 0 <= col <= board_size - 1):
                    break
                if board[row][col] is None:
                    moves.append((row, col))
                #Checks if the square contains a piece and checks its color.
                if board[row][col] is not None:
                    if board[row][col].color == self.color:
                        break
                    if board[row][col].color is not self.color and not isinstance(self, Pawn):
                        moves.append((row, col))
                        break
        return moves

    #Sets the pieces sprite from the sub class
    @property
    def sprite(self) -> pygame.Surface:
        return self.SPRITE[self.color]


class Pawn(Piece):
    PATHS = {"white": "assets/sprites/W_pawn.png", "black": "assets/sprites/B_pawn.png"}
    sound = "assets/sounds/Pawn.wav"

    def __init__(self, color: str):
        super().__init__(color)
        # Tracks whether this pawn just moved two squares, used to allow en passant by an adjacent pawn next turn
        self.has_moved_2 = False

    #Handles the pawns moves
    def get_legal_moves(self, from_row, from_col, board):
        moves = []
        directions = []
        attacks = []
        move_by = 2

        #Lets the pawn move two squares ahead on first move
        if not self.has_moved:
            move_by = 3

        #Handles diagonal attacks for white
        if self.color == "white":
            directions.append((-1, 0))
            # Adds a normal diagonal capture if an enemy piece is present on that square
            if from_row - 1 >= 0:
                if from_col > 0 and board[from_row - 1][from_col - 1] is not None:
                    attacks.append((-1, -1))
                if from_col < 7 and board[from_row - 1][from_col + 1] is not None:
                    attacks.append((-1, 1))
            # Adds en passant capture if the adjacent piece is a pawn that just moved two squares
            if from_col > 0 and isinstance(board[from_row][from_col - 1], Pawn) and board[from_row][from_col - 1].has_moved_2:
                attacks.append((-1, -1))
            if from_col < 7 and isinstance(board[from_row][from_col + 1], Pawn) and board[from_row][from_col + 1].has_moved_2:
                attacks.append((-1, 1))

        #Handles diagonal attacks for black
        elif self.color == "black":
            directions.append((1, 0))
            # Adds a normal diagonal capture if an enemy piece is present on that square
            if from_row + 1 <= 7:
                if from_col > 0 and board[from_row + 1][from_col - 1] is not None:
                    attacks.append((1, -1))
                if from_col < 7 and board[from_row + 1][from_col + 1] is not None:
                    attacks.append((1, 1))
            # Adds en passant capture if the adjacent piece is a pawn that just moved two squares
            if from_col > 0 and isinstance(board[from_row][from_col - 1], Pawn) and board[from_row][from_col - 1].has_moved_2:
                attacks.append((1, -1))
            if from_col < 7 and isinstance(board[from_row][from_col + 1], Pawn) and board[from_row][from_col + 1].has_moved_2:
                attacks.append((1, 1))

        moves = self.move_validating(directions, move_by, from_row, from_col, board)

        # Converts each attack direction into a board coordinate and adds it to moves if the target is a valid capture
        for row_step, col_step in attacks:
            row = from_row + row_step
            col = from_col + col_step
            target = board[row][col]
            if target is not None and target.color is not self.color:
                moves.append((row, col))
            elif target is None:
                moves.append((row, col))

        return moves


class Bishop(Piece):
    PATHS = {"white": "assets/sprites/W_bishop.png", "black": "assets/sprites/B_bishop.png"}
    sound = "assets/sounds/Bishop.wav"

    def get_legal_moves(self, from_row, from_col, board):
        #Sets the pieces directions that it can move
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self.move_validating(directions, board_size, from_row, from_col, board)


class Horse(Piece):
    PATHS = {"white": "assets/sprites/W_horse.png", "black": "assets/sprites/B_horse.png"}
    sound = "assets/sounds/Horse.wav"

    def get_legal_moves(self, from_row, from_col, board):
        #Sets the pieces directions that it can move
        directions = [(-2, 1), (-2, -1), (2, 1), (2, -1), (-1, 2), (-1, -2), (1, 2), (1, -2)]
        # Move_by is 2 so the loop runs only once per direction, giving the knight its fixed L-shaped jump
        return self.move_validating(directions, 2, from_row, from_col, board)


class Rook(Piece):
    PATHS = {"white": "assets/sprites/W_rook.png", "black": "assets/sprites/B_rook.png"}
    sound = "assets/sounds/Rook.wav"

    def get_legal_moves(self, from_row, from_col, board):
        #Sets the pieces directions that it can move
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return self.move_validating(directions, board_size, from_row, from_col, board)


class Queen(Piece):
    PATHS = {"white": "assets/sprites/W_queen.png", "black": "assets/sprites/B_queen.png"}
    sound = "assets/sounds/Queen.wav"

    def get_legal_moves(self, from_row, from_col, board):
        #Sets the pieces directions that it can move
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self.move_validating(directions, board_size, from_row, from_col, board)


class King(Piece):
    PATHS = {"white": "assets/sprites/W_king.png", "black": "assets/sprites/B_king.png"}
    sound = "assets/sounds/King.wav"

    def get_legal_moves(self, from_row, from_col, board):
        #Sets the pieces directions that it can move
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        # Move_by is 2 so the king only steps one square per direction
        moves = self.move_validating(directions, 2, from_row, from_col, board)

        # Checks for castling rights, the king and the relevant rook must not have moved and the squares between them must be empty
        if not self.has_moved:
            kingside_rook = board[from_row][7]
            if (isinstance(kingside_rook, Rook) and not kingside_rook.has_moved
                    and all(board[from_row][c] is None for c in range(from_col + 1, 7))):
                moves.append((from_row, from_col + 2))

            queenside_rook = board[from_row][0]
            if (isinstance(queenside_rook, Rook) and not queenside_rook.has_moved
                    and all(board[from_row][c] is None for c in range(1, from_col))):
                moves.append((from_row, from_col - 2))

        return moves

#Creates the board and puts the pieces on the right places
def make_board() -> list:
    W, B = "white", "black"
    back_row = [Rook, Horse, Bishop, Queen, King, Bishop, Horse, Rook]
    board = [[None] * board_size for _ in range(board_size)]
    # Places the back rank pieces for both colors then fills the second and seventh rows with pawns
    for col, cls in enumerate(back_row):
        board[0][col] = cls(B)
        board[7][col] = cls(W)
    for col in range(board_size):
        board[1][col] = Pawn(B)
        board[6][col] = Pawn(W)
    return board


class Restart_button:
    def __init__(self):
        # Initialises with an empty rect that gets properly sized once the window dimensions are known
        self.rect = pygame.Rect(0, 0, 0, 0)

    def update_layout(self, board_px, win_w, win_h):
        # Positions the button in the strip below the board, centered horizontally
        self.rect = pygame.Rect(win_w // 4, board_px + 5, win_w // 2, win_h - board_px - 10)

    #Draws the restart button
    def draw(self, screen):
        pygame.draw.rect(screen, "#8B3A00", self.rect, border_radius=6)
        font = pygame.font.SysFont("Georgia", self.rect.height // 2)
        screen.blit(font.render("Restart", True, "white"),
                    font.render("Restart", True, "white").get_rect(center=self.rect.center))

    # Returns True if the given mouse position is inside the button
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


class Game_square:
    size = 600 // board_size
    num_created_squares = 1
    light_color = "#EDE398"
    dark_color = "#431C07"
    highlight_color_light = "#AAD751"
    highlight_color_dark = "#576E29"
    selected_color = "#EDD11B"
    in_check_color = "#FF0000"
    promotion_color = "#FFFFFF"
    files = "abcdefgh"

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        # Builds the standard chess notation label for this square, e.g. "e4"
        self.notation = self.files[col] + str(board_size - row)
        self.init_color = self.num_created_squares
        self.num_created_squares += 1

    # Recalculates the square size so the board fills the available window space
    @classmethod
    def update_size(cls, width: int, height: int):
        cls.size = min(width, height - 50) // board_size

    # Returns the screen rectangle for this square based on its row and column position
    @property
    def hitbox(self) -> pygame.Rect:
        return pygame.Rect(self.col * self.size, self.row * self.size, self.size, self.size)


class ChessGame:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.squares = [[Game_square(row, col) for col in range(board_size)] for row in range(board_size)]
        self.board = make_board()

        # Links each piece to the square it starts on
        for row in range(board_size):
            for col in range(board_size):
                piece = self.board[row][col]
                if piece:
                    piece.square = self.squares[row][col]

        self.promotion_squares = {}
        self.selected = None
        self.in_check = None
        self.previous_selected = None
        self.valid_moves = []
        self.turn = "white"
        self.promotion_pending = None
        self.flipped = False
        self.white_moves = {}
        self.black_moves = {}

        # Game-over state: None means ongoing, "checkmate_white" / "checkmate_black" / "stalemate"
        self.game_over = False
        self.game_result = None

        w, h = screen.get_size()
        Game_square.update_size(w, h)
        self.restart_button = Restart_button()
        self.restart_button.update_layout(Game_square.size * board_size, w, h)
        self.square_size = Game_square.size
        self.reload_sprites()
        self.load_sounds()
        self.compute_all_moves()

    # Loads each piece's sound file and falls back to None silently if any file is missing
    def load_sounds(self):
        try:
            for cls in (Pawn, Bishop, Horse, Rook, Queen, King):
                cls.sound = pygame.mixer.Sound(resource_path(cls.sound))
        except Exception:
            for cls in (Pawn, Bishop, Horse, Rook, Queen, King):
                cls.sound = None

    # Recalculates layout and reloads sprites to match the new window size after a resize event
    def on_resize(self, width: int, height: int):
        Game_square.update_size(width, height)
        self.square_size = Game_square.size
        self.restart_button.update_layout(Game_square.size * board_size, width, height)
        self.reload_sprites()

    # Loads and scales all piece sprites to the current square size
    def reload_sprites(self):
        sz = self.square_size
        for cls in (Pawn, Bishop, Horse, Rook, Queen, King):
            cls.SPRITE = {}
            for color, path in cls.PATHS.items():
                pil_img = Image.open(resource_path(path)).resize((sz, sz)).convert("RGBA")
                surface = pygame.image.fromstring(pil_img.tobytes(), pil_img.size, "RGBA").convert_alpha()
                cls.SPRITE[color] = surface

    # Converts a board row and column to the screen pixel position, accounting for whether the board is flipped
    def board_to_screen(self, row: int, col: int) -> tuple[int, int]:
        sz = Game_square.size
        if self.flipped:
            return (board_size - 1 - col) * sz, (board_size - 1 - row) * sz
        return col * sz, row * sz

    # Converts a screen pixel position to a board row and column, accounting for whether the board is flipped
    def screen_to_board(self, mx: int, my: int) -> tuple[int, int]:
        sz = Game_square.size
        screen_col = max(0, min(board_size - 1, mx // sz))
        screen_row = max(0, min(board_size - 1, my // sz))
        if self.flipped:
            return board_size - 1 - screen_row, board_size - 1 - screen_col
        return screen_row, screen_col

    # Draws all squares, piece sprites, labels, the restart button and any active overlay
    def draw_board(self):
        self.screen.fill((0, 0, 0))
        sz = Game_square.size
        font = pygame.font.SysFont("Helvetica", max(board_size, sz // 6))

        for row in range(board_size):
            for col in range(board_size):
                sq = self.squares[row][col]
                x1, y1 = self.board_to_screen(row, col)

                # Picks the correct highlight color based on the squares current state
                if (row, col) == self.selected:
                    color = Game_square.selected_color
                elif (row, col) in self.valid_moves:
                    color = Game_square.highlight_color_light if (row + col) % 2 == 0 else Game_square.highlight_color_dark
                elif (row, col) == self.in_check:
                    color = Game_square.in_check_color
                elif (row, col) in self.promotion_squares:
                    color = Game_square.promotion_color
                else:
                    color = Game_square.light_color if (row + col) % 2 == 0 else Game_square.dark_color

                pygame.draw.rect(self.screen, color, (x1, y1, sz, sz))

                # Draws the square notation label in the bottom left corner using an inverted color so it is always readable
                text_color = Game_square.dark_color if (row + col) % 2 == 0 else Game_square.light_color
                label = font.render(sq.notation, True, text_color)
                self.screen.blit(label, label.get_rect(bottomleft=(x1 + 4, y1 + sz - 4)))

                # Draws the promotion piece options on top of their highlighted squares, otherwise draws the normal piece
                if (row, col) in self.promotion_squares:
                    cls = self.promotion_squares[(row, col)]
                    promoting_color = self.board[self.promotion_pending[0]][self.promotion_pending[1]].color
                    sprite = cls.SPRITE[promoting_color]
                    self.screen.blit(sprite, sprite.get_rect(center=(x1 + sz // 2, y1 + sz // 2)))
                else:
                    piece = self.board[row][col]
                    if piece:
                        self.screen.blit(piece.sprite, piece.sprite.get_rect(center=(x1 + sz // 2, y1 + sz // 2)))

        self.restart_button.draw(self.screen)

        # Draws the game over banner on top of everything if the game has ended
        if self.game_over:
            self._draw_game_over_overlay()

        pygame.display.flip()

    def _draw_game_over_overlay(self):
        board_px = Game_square.size * board_size
        w, h = self.screen.get_size()

        #Checks the game results and sets the information for the game end overlay
        if self.game_result == "stalemate":
            title_text = "DRAW"
            sub_text = "No legal moves"
            title_color = "#EDE398"
            accent_color = "#A08000"
        elif self.game_result == "checkmate_white":
            title_text = "CHECKMATE"
            sub_text = "Black wins!"
            title_color = "#FFFFFF"
            accent_color = "#CC3333"
        else:
            title_text = "CHECKMATE"
            sub_text = "White wins!"
            title_color = "#FFFFFF"
            accent_color = "#CC3333"

        #Creates the game end banner
        banner_h = board_px // 3
        banner_rect = pygame.Rect(w // 8, board_px // 2 - banner_h // 2, w * 6 // 8, banner_h)
        pygame.draw.rect(self.screen, "#1A0A00", banner_rect, border_radius=12)
        pygame.draw.rect(self.screen, accent_color, banner_rect, width=3, border_radius=12)

        #Creates the "CHECKMATE" and "DRAW" text
        title_font_size = int(max(24, banner_h // 2 * 0.5))
        title_font = pygame.font.SysFont("Georgia", title_font_size, bold=True)
        title_surf = title_font.render(title_text, True, title_color)
        self.screen.blit(title_surf, title_surf.get_rect(centerx=w // 2, centery=banner_rect.centery - banner_h // 8))

        #Creates the explanation for the win
        sub_font_size = max(12, banner_h // 4)
        sub_font = pygame.font.SysFont("Georgia", sub_font_size)
        sub_surf = sub_font.render(sub_text, True, accent_color)
        self.screen.blit(sub_surf, sub_surf.get_rect(centerx=w // 2, centery=banner_rect.centery + banner_h // 4))

    def compute_all_moves(self):
        #Resets the lists for the white and black moves
        self.white_moves = {}
        self.black_moves = {}

        #Filter the moves and puts them in the right dictionary based on color
        for row in range(board_size):
            for col in range(board_size):
                piece = self.board[row][col]
                if piece:
                    raw_moves = piece.get_legal_moves(row, col, self.board)
                    moves = self.filter_legal_moves(row, col, raw_moves)
                    if piece.color == "white":
                        self.white_moves[piece.id] = moves
                    else:
                        self.black_moves[piece.id] = moves

        current_moves = self.white_moves if self.turn == "white" else self.black_moves
        #Goes through game end states when a player has no legal moves
        if not any(current_moves.values()):
            opponent_color = "black" if self.turn == "white" else "white"

            # Find the current player's king
            king_pos = None
            for r in range(board_size):
                for c in range(board_size):
                    p = self.board[r][c]
                    if isinstance(p, King) and p.color == self.turn:
                        king_pos = (r, c)
                        break

            # Collect all squares the opponent attacks
            opponent_attacks = []
            for r in range(board_size):
                for c in range(board_size):
                    p = self.board[r][c]
                    if p and p.color == opponent_color:
                        opponent_attacks += p.get_legal_moves(r, c, self.board)

            #Checks if the king is in checkmate by checking if the the kings position is in the opposite colors attacks
            if king_pos in opponent_attacks:
                self.game_result = "checkmate_white" if self.turn == "white" else "checkmate_black"
            else:
                self.game_result = "stalemate"
            self.game_over = True

    #Starts promotion for pawns
    def start_promotion(self, row, col):
        self.promotion_pending = (row, col)
        self.promotion_squares = {}
        #Sets the pieces a pawn can promote to
        options = [Queen, Rook, Bishop, Horse]
        #Changes the dicrection of the white squares based on piece position so if white the squares under in a row is turned white and the opposite goes for black
        direction = 1 if row == 0 else -1
        for i, cls in enumerate(options):
            self.promotion_squares[(row + direction * (i + 1), col)] = cls

    #Moves a piece
    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]

        #Goes through every piece and checks if the piece moved is a pawn and if it is it stops it from moving 2 steps the next turn
        for r in range(board_size):
            for c in range(board_size):
                if isinstance(self.board[r][c], Pawn):
                    self.board[r][c].has_moved_2 = False

        # Removes the captured pawn from the board when en passant is played, since the target square is empty
        if isinstance(piece, Pawn) and from_col != to_col and self.board[to_row][to_col] is None:
            self.board[from_row][to_col] = None

        # Moves the rook to the correct square when the king castles kingside or queenside
        if isinstance(piece, King) and abs(to_col - from_col) == 2:
            if to_col == 6:
                castling_rook = self.board[from_row][7]
                self.board[from_row][5] = castling_rook
                self.board[from_row][7] = None
                castling_rook.square = self.squares[from_row][5]
                castling_rook.has_moved = True
            elif to_col == 2:
                castling_rook = self.board[from_row][0]
                self.board[from_row][3] = castling_rook
                self.board[from_row][0] = None
                castling_rook.square = self.squares[from_row][3]
                castling_rook.has_moved = True

        # Places the piece on the destination square and clears the square it came from
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.square = self.squares[to_row][to_col]

        # Records that the pawn moved two squares so adjacent pawns can attempt en passant on the next turn
        if isinstance(piece, Pawn) and abs(to_row - from_row) == 2:
            piece.has_moved_2 = True

        # Triggers promotion if a pawn has reached the far end of the board
        if isinstance(piece, Pawn):
            if piece.color == "white" and to_row == 0:
                self.start_promotion(to_row, to_col)
            if piece.color == "black" and to_row == board_size - 1:
                self.start_promotion(to_row, to_col)

        # Plays the sound for the piece that just moved
        if piece.sound:
            piece.sound.play()

    # Resets all game state back to the starting position
    def reset_game(self):
        self.board = make_board()
        self.squares = [[Game_square(row, col) for col in range(board_size)] for row in range(board_size)]
        for row in range(board_size):
            for col in range(board_size):
                piece = self.board[row][col]
                if piece:
                    piece.square = self.squares[row][col]
        self.promotion_squares = {}
        self.selected = None
        self.in_check = None
        self.previous_selected = None
        self.valid_moves = []
        self.turn = "white"
        self.promotion_pending = None
        self.flipped = False
        self.white_moves = {}
        self.black_moves = {}
        self.game_over = False
        self.game_result = None
        self.compute_all_moves()

    # Checks whether a specific move is legal and updates the valid moves list for highlighting
    def legal_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        raw_moves = piece.get_legal_moves(from_row, from_col, self.board)
        self.valid_moves = self.filter_legal_moves(from_row, from_col, raw_moves)
        return (to_row, to_col) in self.valid_moves

    # Removes any move from the list that would leave the moving players king in check
    def filter_legal_moves(self, from_row, from_col, moves):
        piece = self.board[from_row][from_col]
        legal = []
        opponent_color = "black" if piece.color == "white" else "white"

        for to_row, to_col in moves:
            # Extra check for castling: the king must not pass through or start on an attacked square
            if isinstance(piece, King) and abs(to_col - from_col) == 2:
                mid_col = from_col + (1 if to_col > from_col else -1)

                # Checks that the kings starting square is not under attack before allowing castling
                cur_attacks = []
                for r in range(board_size):
                    for c in range(board_size):
                        p = self.board[r][c]
                        if p and p.color == opponent_color:
                            cur_attacks += p.get_legal_moves(r, c, self.board)
                if (from_row, from_col) in cur_attacks:
                    continue

                # Checks that the square the king passes through is not under attack
                board_mid = [row[:] for row in self.board]
                board_mid[from_row][mid_col] = board_mid[from_row][from_col]
                board_mid[from_row][from_col] = None
                mid_attacks = []
                for r in range(board_size):
                    for c in range(board_size):
                        p = board_mid[r][c]
                        if p and p.color == opponent_color:
                            mid_attacks += p.get_legal_moves(r, c, board_mid)
                if (from_row, mid_col) in mid_attacks:
                    continue

            # Simulates the move on a copy of the board to check whether the king ends up in check
            board_copy = [row[:] for row in self.board]
            board_copy[to_row][to_col] = board_copy[from_row][from_col]
            board_copy[from_row][from_col] = None

            # Finds the moving players king on the copied board after the simulated move
            king_pos = None
            for r in range(board_size):
                for c in range(board_size):
                    p = board_copy[r][c]
                    if isinstance(p, King) and p.color == piece.color:
                        king_pos = (r, c)
                        break

            # Collects all squares the opponent can attack on the copied board
            opponent_attacks = []
            for r in range(board_size):
                for c in range(board_size):
                    p = board_copy[r][c]
                    if p and p.color == opponent_color:
                        opponent_attacks += p.get_legal_moves(r, c, board_copy)

            # Only adds the move to the legal list if the king is not in check after it
            if king_pos not in opponent_attacks:
                legal.append((to_row, to_col))

        return legal


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 650), pygame.RESIZABLE)
    pygame.display.set_caption("Chess")

    game = ChessGame(screen)
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                game.screen = screen
                game.on_resize(event.w, event.h)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game.restart_button.is_clicked(event.pos):
                    game.reset_game()
                elif not game.game_over:
                    board_row, board_col = game.screen_to_board(*event.pos)
                    sq = game.squares[board_row][board_col]

                    # Handles a click during promotion: picks the chosen piece and completes the turn
                    if game.promotion_pending is not None:
                        if (sq.row, sq.col) in game.promotion_squares:
                            pawn_row, pawn_col = game.promotion_pending
                            chosen_cls = game.promotion_squares[(sq.row, sq.col)]
                            promoting_color = game.board[pawn_row][pawn_col].color
                            game.board[pawn_row][pawn_col] = chosen_cls(promoting_color)
                            game.promotion_pending = None
                            game.promotion_squares = {}

                            game.compute_all_moves()

                            # Checks whether either king is now in check after the promotion
                            game.in_check = None
                            for row in range(board_size):
                                for col in range(board_size):
                                    p = game.board[row][col]
                                    if isinstance(p, King):
                                        opp_moves = game.black_moves if p.color == "white" else game.white_moves
                                        if any((row, col) in m for m in opp_moves.values()):
                                            game.in_check = (row, col)

                            # Draws the board and waits before flipping so both players can see the result
                            if not game.game_over:
                                game.draw_board()
                                pygame.time.wait(500)
                                game.flipped = not game.flipped
                    else:
                        piece = game.board[sq.row][sq.col]
                        # Selects a piece on the first click if it belongs to the active player
                        if game.selected is None:
                            if piece and piece.color == game.turn:
                                game.selected = (sq.row, sq.col)
                                raw_moves = piece.get_legal_moves(sq.row, sq.col, game.board)
                                game.valid_moves = game.filter_legal_moves(sq.row, sq.col, raw_moves)
                        # Clicking the already selected square deselects it
                        elif game.selected == (sq.row, sq.col):
                            game.selected = None
                            game.valid_moves = []
                        else:
                            from_row, from_col = game.selected
                            moving_piece = game.board[from_row][from_col]
                            if moving_piece.movement_enabled:
                                if game.legal_move(from_row, from_col, sq.row, sq.col):
                                    game.move_piece(from_row, from_col, sq.row, sq.col)
                                    moving_piece.has_moved = True

                                    # Switches the active turn to the other player
                                    game.turn = "black" if game.turn == "white" else "white"

                                    game.compute_all_moves()

                                    # Checks whether either king is now in check after the move
                                    game.in_check = None
                                    for row in range(board_size):
                                        for col in range(board_size):
                                            p = game.board[row][col]
                                            if isinstance(p, King):
                                                opp_moves = game.black_moves if p.color == "white" else game.white_moves
                                                if any((row, col) in m for m in opp_moves.values()):
                                                    game.in_check = (row, col)

                                    # Draws the board and waits before flipping so both players can see the move
                                    if game.promotion_pending is None and not game.game_over:
                                        game.draw_board()
                                        pygame.time.wait(500)
                                        game.flipped = not game.flipped

                            # Clears the selection regardless of whether the move was legal
                            game.selected = None
                            game.valid_moves = []

        game.draw_board()
        clock.tick(120)

    pygame.quit()


if __name__ == "__main__":
    main()