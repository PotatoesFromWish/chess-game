import pygame
from PIL import Image

board_size = 8

class Piece:
    SPRITE = {}

    def __init__(self, color: str):
        self.color = color

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
        self.hasmoved = False
    
    def get_legal_moves(self, from_row, from_col, board):
        moves = []
        directions = []
        attacks = []
        move_by = 2

        if not self.hasmoved:
            move_by = 3

        if self.color == "white":
            directions.append((-1, 0))
            if from_col > 0 and board[from_row - 1][from_col - 1] is not None:
                attacks.append((-1, -1))
            if from_col < 7 and board[from_row - 1][from_col + 1] is not None:
                attacks.append((-1, 1))
        elif self.color == "black":
            directions.append((1, 0))
            if from_col > 0 and board[from_row + 1][from_col - 1] is not None:
                attacks.append((1, -1))
            if from_col < 7 and board[from_row + 1][from_col + 1] is not None:
                attacks.append((1, 1))

        moves = self.move_validating(directions, move_by, from_row, from_col, board)
        
        for row_step, col_step in attacks:
            row = from_row + row_step
            col = from_col + col_step
            if board[row][col].color is not self.color:
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

        self.selected    = None
        self.previous_selected = None
        self.valid_moves = []
        self.turn = "white"

        w, h = screen.get_size()
        Game_square.update_size(w, h)
        self.square_size = Game_square.size


        self.reload_sprites()

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
                elif (row, col) in self.valid_moves:
                    color = Game_square.highlight_color
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

                piece = self.board[row][col]
                if piece:
                    sprite      = piece.sprite
                    sprite_rect = sprite.get_rect(
                        center=(x1 + sz // 2, y1 + sz // 2)
                    )
                    self.screen.blit(sprite, sprite_rect)

        pygame.display.flip()

    def move_piece(self, from_row, from_col, to_row, to_col):
            piece = self.board[from_row][from_col]
            self.board[to_row][to_col] = piece
            self.board[from_row][from_col] = None
            piece.square = self.squares[to_row][to_col] 

    def legal_move(self, from_row, from_col, to_row, to_col):
        piece = self.board[from_row][from_col]
        self.valid_moves = piece.get_legal_moves(from_row, from_col, self.board)

        if (to_row, to_col) not in self.valid_moves:
            return False
    
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
                for row in game.squares:
                    for sq in row:
                        if sq.hitbox.collidepoint(event.pos):
                            piece = game.board[sq.row][sq.col]
                            if game.selected is None:
                            # first click selects a piece
                                if piece:
                                    game.selected = (sq.row, sq.col)
                                    game.valid_moves = piece.get_legal_moves(sq.row, sq.col, game.board)
                            elif game.selected == (sq.row, sq.col):
                                game.selected = None
                                game.valid_moves = []

                            else:
                                # second click moves the piece to this square
                                from_row, from_col = game.selected
                                moving_piece = game.board[from_row][from_col] 
                                if game.legal_move(from_row, from_col, sq.row, sq.col):
                                    game.move_piece(from_row, from_col, sq.row, sq.col)
                                    if isinstance(moving_piece, Pawn):
                                        moving_piece.hasmoved = True
                                game.selected = None
                                game.valid_moves = []



        game.draw_board()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()