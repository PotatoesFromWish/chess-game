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
                if  board[row][col] is None:
                    moves.append((row, col))
                else:
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
            # normal capture
            if target is not None and target.color is not self.color:
                moves.append((row, col))
            # en passant
            elif target is None:
                moves.append((row, col))

        return moves



class Bishop(Piece):
    PATHS = {"white": "assets/W_bishop.png", "black": "assets/B_bishop.png"}

    def get_legal_moves(self, from_row, from_col, board):
        move_by = board_size

        directions = [
            (-1, -1),  # up left
            (-1,  1),  # up right
            ( 1, -1),  # down left
            ( 1,  1),  # down right
        ]

        return self.move_validating(directions, move_by, from_row, from_col, board)

class Horse(Piece):
    PATHS = {"white": "assets/W_horse.png", "black": "assets/B_horse.png"}

    def get_legal_moves(self, from_row, from_col, board):
        move_by = 2

        directions = [
            (-2,  1),  # up
            (-2,  -1),  # down
            ( 2, 1),  # left
            ( 2,  -1),  # right
            (-1, 2),  # up left
            (-1,  -2),  # up right
            ( 1, 2),  # down left
            ( 1,  -2),  # down right
        ]

        return self.move_validating(directions, move_by, from_row, from_col, board)

class Rook(Piece):
    PATHS = {"white": "assets/W_rook.png", "black": "assets/B_rook.png"}

    def get_legal_moves(self, from_row, from_col, board):
        move_by = board_size

        directions = [
            (-1,  0),  # up
            ( 1,  0),  # down
            ( 0, -1),  # left
            ( 0,  1),  # right
        ]

        return self.move_validating(directions, move_by, from_row, from_col, board)

class Queen(Piece):
    PATHS = {"white": "assets/W_queen.png", "black": "assets/B_queen.png"}

    def get_legal_moves(self, from_row, from_col, board):
        move_by = board_size

        directions = [
            (-1,  0),  # up
            ( 1,  0),  # down
            ( 0, -1),  # left
            ( 0,  1),  # right
            (-1, -1),  # up left
            (-1,  1),  # up right
            ( 1, -1),  # down left
            ( 1,  1),  # down right
        ]

        return self.move_validating(directions, move_by, from_row, from_col, board)

class King(Piece):
    PATHS = {"white": "assets/W_king.png", "black": "assets/B_king.png"}

    def get_legal_moves(self, from_row, from_col, board):
        move_by = 2

        directions = [
            (-1,  0),  # up
            ( 1,  0),  # down
            ( 0, -1),  # left
            ( 0,  1),  # right
            (-1, -1),  # up left
            (-1,  1),  # up right
            ( 1, -1),  # down left
            ( 1,  1),  # down right
        ]

        return self.move_validating(directions, move_by, from_row, from_col, board)



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


    light_color = "#EDE398"
    dark_color = "#431C07"
    highlight_color = "#AAD751"
    selected_color = "#4B9545"
    in_check_color = "#FF0000"
    promotion_color = "#FFFFFF"
    files = "abcdefgh"

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.notation = self.files[col] + str(board_size - row)

    @classmethod
    def update_size(cls, width: int, height: int):
        cls.size = min(width, height) // board_size
    
    @property
    def hitbox(self) -> pygame.Rect:
        return pygame.Rect(self.col * self.size, self.row * self.size, self.size, self.size)


class ChessGame:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        self.squares = [
            [Game_square(row, col) for col in range(board_size)]
            for row in range(board_size)
        ]

        self.board  = make_board()

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

        self.white_moves = []
        self.black_moves = []

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

                surface = pygame.image.fromstring(
                    pil_img.tobytes(), pil_img.size, "RGBA"
                ).convert_alpha()
                cls.SPRITE[color] = surface

    def draw_board(self):
        self.screen.fill((0, 0, 0))
        sz   = Game_square.size
        font = pygame.font.SysFont("Helvetica", max(board_size, sz // 6))

        for row in range(board_size):
            for col in range(board_size):
                sq = self.squares[row][col]
                x1, y1 = col * sz, row * sz

                if (row, col) == self.selected:
                    color = Game_square.selected_color
                elif (row, col) == self.in_check:
                    color = Game_square.in_check_color
                elif (row, col) in self.valid_moves:
                    color = Game_square.highlight_color
                elif (row, col) in self.promotion_squares:
                    color = Game_square.promotion_color
                else:
                    color = (
                        Game_square.light_color
                        if (row + col) % 2 == 0
                        else Game_square.dark_color
                    )

                pygame.draw.rect(self.screen, color, (x1, y1, sz, sz))

                text_color = (
                    Game_square.dark_color
                    if (row + col) % 2 == 0
                    else Game_square.light_color
                )
                label = font.render(sq.notation, True, text_color)
                label_rect = label.get_rect(bottomleft=(x1 + 4, y1 + sz - 4))
                self.screen.blit(label, label_rect)

                if (row, col) in self.promotion_squares:
                    cls = self.promotion_squares[(row, col)]
                    promoting_color = self.board[self.promotion_pending[0]][self.promotion_pending[1]].color
                    sprite = cls.SPRITE[promoting_color]
                    sprite_rect = sprite.get_rect(center=(x1 + sz // 2, y1 + sz // 2))
                    self.screen.blit(sprite, sprite_rect)
                else:
                    piece = self.board[row][col]
                    if piece:
                        sprite = piece.sprite
                        sprite_rect = sprite.get_rect(
                            center=(x1 + sz // 2, y1 + sz // 2)
                        )
                        self.screen.blit(sprite, sprite_rect)

        pygame.display.flip()

    def compute_all_moves(self):
        self.white_moves = {}
        self.black_moves = {}
        for row in range(board_size):
            for col in range(board_size):
                piece = self.board[row][col]
                if piece:
                    moves = piece.get_legal_moves(row, col, self.board)
                    if piece.color == "white":
                        self.white_moves[piece.id] = moves
                    else:
                        self.black_moves[piece.id] = moves

    def start_promotion(self, row, col):
        self.promotion_pending = (row, col)
        self.promotion_squares = {}
        options = [Queen, Rook, Bishop, Horse]
        direction = 1 if row == 0 else -1  # white promotes at row 0, go down; black at row 7, go up
        for i, cls in enumerate(options):
            target_row = row + direction * (i + 1)
            self.promotion_squares[(target_row, col)] = cls

    def move_piece(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]

        # resets has_moved_2 on all pawns before applying the new move
        for r in range(board_size):
            for c in range(board_size):
                if isinstance(self.board[r][c], Pawn):
                    self.board[r][c].has_moved_2 = False

        # en passant
        if isinstance(piece, Pawn) and from_col != to_col and self.board[to_row][to_col] is None:
            self.board[from_row][to_col] = None

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
        
        self.compute_all_moves()


    def legal_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        self.valid_moves = piece.get_legal_moves(from_row, from_col, self.board)

        if (to_row, to_col) not in self.valid_moves:
            return False
        #elif self.in_check and not isinstance(piece, King):
            #return False
        #elif self.turn != piece.color:
            #return False
        return True
        


def main():
    pygame.init()
    screen = pygame.display.set_mode((600, 600), pygame.RESIZABLE)
    pygame.display.set_caption("Chess")

    game = ChessGame(screen)

    clock   = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE
                )
                game.screen = screen
                game.on_resize(event.w, event.h)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if game.promotion_pending is not None:
                    for row in game.squares:
                        for sq in row:
                            if sq.hitbox.collidepoint(event.pos) and (sq.row, sq.col) in game.promotion_squares:
                                pawn_row, pawn_col = game.promotion_pending
                                chosen_cls = game.promotion_squares[(sq.row, sq.col)]
                                promoting_color = game.board[pawn_row][pawn_col].color
                                game.board[pawn_row][pawn_col] = chosen_cls(promoting_color)
                                game.promotion_pending = None
                                game.promotion_squares = {}
                                game.turn = "black" if game.turn == "white" else "white"
                else:
                    for row in game.squares:
                        for sq in row:
                            if sq.hitbox.collidepoint(event.pos):
                                piece = game.board[sq.row][sq.col]
                                if game.selected is None:
                                    if piece:
                                        if piece.color == game.turn:
                                            game.selected = (sq.row, sq.col)
                                            game.valid_moves = piece.get_legal_moves(sq.row, sq.col, game.board)
                                elif game.selected == (sq.row, sq.col):
                                    game.selected = None
                                    game.valid_moves = []
                                else:
                                    from_row, from_col = game.selected
                                    moving_piece = game.board[from_row][from_col]
                                    if moving_piece.movement_enabled:
                                        if game.legal_move(from_row, from_col, sq.row, sq.col):
                                            game.move_piece(from_row, from_col, sq.row, sq.col)

                                            game.compute_all_moves()

                                            for row in range(board_size):
                                                for col in range(board_size):
                                                    piece = game.board[row][col]
                                                    if isinstance(piece, King):
                                                        opponent_moves = game.black_moves if piece.color == "white" else game.white_moves
                                                        is_attacked = any((row, col) in moves for moves in opponent_moves.values())
                                                        if is_attacked:
                                                            game.in_check = (row, col)
                                                        else:
                                                            game.in_check = None
                                            
                                            if game.turn == "white":
                                                game.turn = "black"
                                            elif game.turn == "black":
                                                game.turn = "white"
                                            

                                            moving_piece.has_moved = True
                                    game.selected = None
                                    game.valid_moves = []



        game.draw_board()         
        clock.tick(120)

    pygame.quit()


if __name__ == "__main__":
    main()