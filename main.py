import pygame
from PIL import Image

board_size = 8


class Piece:
    SPRITE = {}
    _id_counter = 1

    def __init__(self, color: str):
        self.color = color
        self.has_moved = False
        self.movement_enabled = True
        self.id = Piece._id_counter
        Piece._id_counter += 1
        self.in_check = False

    def move_validating(self, directions, move_by, from_row, from_col, board):
        moves = []
        for row_step, col_step in directions:
            for i in range(1, move_by):
                row = from_row + row_step * i
                col = from_col + col_step * i
                if not (0 <= row <= board_size - 1 and 0 <= col <= board_size - 1):
                    break
                if board[row][col] is None:
                    moves.append((row, col))
                if board[row][col] is not None:
                    if board[row][col].color == self.color:
                        break
                    if board[row][col].color is not self.color and not isinstance(self, Pawn):
                        moves.append((row, col))
                        break
        return moves

    @property
    def sprite(self) -> pygame.Surface:
        return self.SPRITE[self.color]


class Pawn(Piece):
    PATHS = {"white": "assets/W_pawn.png", "black": "assets/B_pawn.png"}

    def __init__(self, color: str):
        super().__init__(color)
        self.has_moved_2 = False

    def get_legal_moves(self, from_row, from_col, board):
        moves = []
        directions = []
        attacks = []
        move_by = 2

        if not self.has_moved:
            move_by = 3

        if self.color == "white":
            directions.append((-1, 0))
            if from_row - 1 >= 0: 
                if from_col > 0 and board[from_row - 1][from_col - 1] is not None:
                    attacks.append((-1, -1))
                if from_col < 7 and board[from_row - 1][from_col + 1] is not None:
                    attacks.append((-1, 1))
            if from_col > 0 and isinstance(board[from_row][from_col - 1], Pawn) and board[from_row][from_col - 1].has_moved_2:
                attacks.append((-1, -1))
            if from_col < 7 and isinstance(board[from_row][from_col + 1], Pawn) and board[from_row][from_col + 1].has_moved_2:
                attacks.append((-1, 1))

        elif self.color == "black":
            directions.append((1, 0))
            if from_row + 1 <= 7: 
                if from_col > 0 and board[from_row + 1][from_col - 1] is not None:
                    attacks.append((1, -1))
                if from_col < 7 and board[from_row + 1][from_col + 1] is not None:
                    attacks.append((1, 1))
            if from_col > 0 and isinstance(board[from_row][from_col - 1], Pawn) and board[from_row][from_col - 1].has_moved_2:
                attacks.append((1, -1))
            if from_col < 7 and isinstance(board[from_row][from_col + 1], Pawn) and board[from_row][from_col + 1].has_moved_2:
                attacks.append((1, 1))

        moves = self.move_validating(directions, move_by, from_row, from_col, board)

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
    PATHS = {"white": "assets/W_bishop.png", "black": "assets/B_bishop.png"}

    def get_legal_moves(self, from_row, from_col, board):
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self.move_validating(directions, board_size, from_row, from_col, board)


class Horse(Piece):
    PATHS = {"white": "assets/W_horse.png", "black": "assets/B_horse.png"}

    def get_legal_moves(self, from_row, from_col, board):
        directions = [(-2, 1), (-2, -1), (2, 1), (2, -1), (-1, 2), (-1, -2), (1, 2), (1, -2)]
        return self.move_validating(directions, 2, from_row, from_col, board)


class Rook(Piece):
    PATHS = {"white": "assets/W_rook.png", "black": "assets/B_rook.png"}

    def get_legal_moves(self, from_row, from_col, board):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        return self.move_validating(directions, board_size, from_row, from_col, board)


class Queen(Piece):
    PATHS = {"white": "assets/W_queen.png", "black": "assets/B_queen.png"}

    def get_legal_moves(self, from_row, from_col, board):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        return self.move_validating(directions, board_size, from_row, from_col, board)


class King(Piece):
    PATHS = {"white": "assets/W_king.png", "black": "assets/B_king.png"}

    def get_legal_moves(self, from_row, from_col, board):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        moves = self.move_validating(directions, 2, from_row, from_col, board)

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


def make_board() -> list:
    W, B = "white", "black"
    back_row = [Rook, Horse, Bishop, Queen, King, Bishop, Horse, Rook]
    board = [[None] * board_size for _ in range(board_size)]
    for col, cls in enumerate(back_row):
        board[0][col] = cls(B)
        board[7][col] = cls(W)
    for col in range(board_size):
        board[1][col] = Pawn(B)
        board[6][col] = Pawn(W)
    return board


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
        self.notation = self.files[col] + str(board_size - row)
        self.init_color = self.num_created_squares
        self.num_created_squares += 1

    @classmethod
    def update_size(cls, width: int, height: int):
        cls.size = min(width, height) // board_size

    @property
    def hitbox(self) -> pygame.Rect:
        return pygame.Rect(self.col * self.size, self.row * self.size, self.size, self.size)


class ChessGame:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.squares = [[Game_square(row, col) for col in range(board_size)] for row in range(board_size)]
        self.board = make_board()

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

        w, h = screen.get_size()
        Game_square.update_size(w, h)
        self.square_size = Game_square.size
        self.reload_sprites()
        self.compute_all_moves()

    def on_resize(self, width: int, height: int):
        Game_square.update_size(width, height)
        self.square_size = Game_square.size
        self.reload_sprites()

    def reload_sprites(self):
        sz = self.square_size
        for cls in (Pawn, Bishop, Horse, Rook, Queen, King):
            cls.SPRITE = {}
            for color, path in cls.PATHS.items():
                pil_img = Image.open(path).resize((sz, sz)).convert("RGBA")
                surface = pygame.image.fromstring(pil_img.tobytes(), pil_img.size, "RGBA").convert_alpha()
                cls.SPRITE[color] = surface

    def board_to_screen(self, row: int, col: int) -> tuple[int, int]:
        sz = Game_square.size
        if self.flipped:
            return (board_size - 1 - col) * sz, (board_size - 1 - row) * sz
        return col * sz, row * sz

    def screen_to_board(self, mx: int, my: int) -> tuple[int, int]:
        sz = Game_square.size
        screen_col = max(0, min(board_size - 1, mx // sz))
        screen_row = max(0, min(board_size - 1, my // sz))
        if self.flipped:
            return board_size - 1 - screen_row, board_size - 1 - screen_col
        return screen_row, screen_col

    def draw_board(self):
        self.screen.fill((0, 0, 0))
        sz = Game_square.size
        font = pygame.font.SysFont("Helvetica", max(board_size, sz // 6))

        for row in range(board_size):
            for col in range(board_size):
                sq = self.squares[row][col]
                x1, y1 = self.board_to_screen(row, col)

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

                text_color = Game_square.dark_color if (row + col) % 2 == 0 else Game_square.light_color
                label = font.render(sq.notation, True, text_color)
                self.screen.blit(label, label.get_rect(bottomleft=(x1 + 4, y1 + sz - 4)))

                if (row, col) in self.promotion_squares:
                    cls = self.promotion_squares[(row, col)]
                    promoting_color = self.board[self.promotion_pending[0]][self.promotion_pending[1]].color
                    sprite = cls.SPRITE[promoting_color]
                    self.screen.blit(sprite, sprite.get_rect(center=(x1 + sz // 2, y1 + sz // 2)))
                else:
                    piece = self.board[row][col]
                    if piece:
                        self.screen.blit(piece.sprite, piece.sprite.get_rect(center=(x1 + sz // 2, y1 + sz // 2)))

        pygame.display.flip()

    def compute_all_moves(self):
        self.white_moves = {}
        self.black_moves = {}
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

        # Check the player whose turn it currently is
        current_moves = self.white_moves if self.turn == "white" else self.black_moves
        if not any(current_moves.values()):
            self.reset_game()
            self.flipped = not self.flipped

    def start_promotion(self, row, col):
        self.promotion_pending = (row, col)
        self.promotion_squares = {}
        options = [Queen, Rook, Bishop, Horse]
        direction = 1 if row == 0 else -1
        for i, cls in enumerate(options):
            self.promotion_squares[(row + direction * (i + 1), col)] = cls

    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]

        for r in range(board_size):
            for c in range(board_size):
                if isinstance(self.board[r][c], Pawn):
                    self.board[r][c].has_moved_2 = False

        # en passant
        if isinstance(piece, Pawn) and from_col != to_col and self.board[to_row][to_col] is None:
            self.board[from_row][to_col] = None

        # castling
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

        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = None
        piece.square = self.squares[to_row][to_col]

        if isinstance(piece, Pawn) and abs(to_row - from_row) == 2:
            piece.has_moved_2 = True

        if isinstance(piece, Pawn):
            if piece.color == "white" and to_row == 0:
                self.start_promotion(to_row, to_col)
            if piece.color == "black" and to_row == board_size - 1:
                self.start_promotion(to_row, to_col)

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
        self.compute_all_moves()

    def legal_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        raw_moves = piece.get_legal_moves(from_row, from_col, self.board)
        self.valid_moves = self.filter_legal_moves(from_row, from_col, raw_moves)
        return (to_row, to_col) in self.valid_moves

    def filter_legal_moves(self, from_row, from_col, moves):
        piece = self.board[from_row][from_col]
        legal = []
        opponent_color = "black" if piece.color == "white" else "white"

        for to_row, to_col in moves:
            if isinstance(piece, King) and abs(to_col - from_col) == 2:
                mid_col = from_col + (1 if to_col > from_col else -1)

                cur_attacks = []
                for r in range(board_size):
                    for c in range(board_size):
                        p = self.board[r][c]
                        if p and p.color == opponent_color:
                            cur_attacks += p.get_legal_moves(r, c, self.board)
                if (from_row, from_col) in cur_attacks:
                    continue

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

            board_copy = [row[:] for row in self.board]
            board_copy[to_row][to_col] = board_copy[from_row][from_col]
            board_copy[from_row][from_col] = None

            king_pos = None
            for r in range(board_size):
                for c in range(board_size):
                    p = board_copy[r][c]
                    if isinstance(p, King) and p.color == piece.color:
                        king_pos = (r, c)
                        break

            opponent_attacks = []
            for r in range(board_size):
                for c in range(board_size):
                    p = board_copy[r][c]
                    if p and p.color == opponent_color:
                        opponent_attacks += p.get_legal_moves(r, c, board_copy)

            if king_pos not in opponent_attacks:
                legal.append((to_row, to_col))

        return legal


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
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
                board_row, board_col = game.screen_to_board(*event.pos)
                sq = game.squares[board_row][board_col]

                if game.promotion_pending is not None:
                    if (sq.row, sq.col) in game.promotion_squares:
                        pawn_row, pawn_col = game.promotion_pending
                        chosen_cls = game.promotion_squares[(sq.row, sq.col)]
                        promoting_color = game.board[pawn_row][pawn_col].color
                        game.board[pawn_row][pawn_col] = chosen_cls(promoting_color)
                        game.promotion_pending = None
                        game.promotion_squares = {}
                        game.draw_board()
                        pygame.time.wait(500)
                        game.flipped = not game.flipped
                else:
                    piece = game.board[sq.row][sq.col]
                    if game.selected is None:
                        if piece and piece.color == game.turn:
                            game.selected = (sq.row, sq.col)
                            raw_moves = piece.get_legal_moves(sq.row, sq.col, game.board)
                            game.valid_moves = game.filter_legal_moves(sq.row, sq.col, raw_moves)
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


                                # detection evaluates the correct (next) player
                                game.turn = "black" if game.turn == "white" else "white"

                                # Resets if new current player has none
                                game.compute_all_moves()

                                # Check detection
                                game.in_check = None
                                for row in range(board_size):
                                    for col in range(board_size):
                                        p = game.board[row][col]
                                        if isinstance(p, King):
                                            opp_moves = game.black_moves if p.color == "white" else game.white_moves
                                            if any((row, col) in m for m in opp_moves.values()):
                                                game.in_check = (row, col)

                                
                                if game.promotion_pending is None:
                                    game.draw_board()
                                    pygame.time.wait(500)
                                    game.flipped = not game.flipped

                        game.selected = None
                        game.valid_moves = []

        game.draw_board()
        clock.tick(120)

    pygame.quit()


if __name__ == "__main__":
    main()
