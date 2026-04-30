import tkinter as tk
from PIL import Image, ImageTk

class Piece:
    SPRITE = {}

    def __init__(self, color: str):
        self.color = color

    @property

    def sprite(self) -> str:
        return self.SPRITE[self.color]

class Pawn(Piece):
    PATHS = {"white": "assets/W_pawn.png", "black": "assets/B_pawn.png"}

class Bishop(Piece):
    PATHS = {"white": "assets/W_bishop.png", "black": "assets/B_bishop.png"}

class Horse(Piece):
    PATHS = {"white": "assets/W_horse.png", "black": "assets/B_horse.png"}

class Rook(Piece):
    PATHS = {"white": "assets/W_rook.png", "black": "assets/B_rook.png"}

class Queen(Piece):
    PATHS = {"white": "assets/W_queen.png", "black": "assets/B_queen.png"}

class King(Piece):
    PATHS = {"white": "assets/W_king.png", "black": "assets/B_king.png"}


def load_sprites():
    for cls in (Pawn, Bishop, Horse, Rook, Queen, King):
        cls.SPRITE = {}
        for color, path in cls.PATHS.items():
            img = Image.open(path)
            img = img.resize((square_size, square_size))
            cls.SPRITE[color] = ImageTk.PhotoImage(img)



LIGHT = "#EF93D7"
DARK = "#00401A"
HIGHLIGHT = "#AAD751"
SELECTED = "#F6F669"

square_size   = 150
board_size = 8

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


class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess")
        self.board = make_board()
        self.selected = None    
        self.valid_moves = []
        self.turn = "white"

        size = square_size * board_size
        self.canvas = tk.Canvas(root, width=size, height=size)
        self.canvas.pack()


        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(board_size):
            for col in range(board_size):
                x1, y1 = col * square_size  , row * square_size  
                x2, y2 = x1 + square_size  , y1 + square_size  

                if (row, col) == self.selected:
                    color = SELECTED
                elif (row, col) in self.valid_moves:
                    color = HIGHLIGHT
                else:
                    color = LIGHT if (row + col) % 2 == 0 else DARK

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                piece = self.board[row][col]
                if piece:
                    self.canvas.create_image(
                    x1 + square_size // 2,
                    y1 + square_size // 2,
                    image=piece.sprite,
    )
                    
                
if __name__ == "__main__":
    root = tk.Tk()
    load_sprites() 
    ChessGame(root)
    root.mainloop()