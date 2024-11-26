import tkinter as tk
from tkinter import messagebox


class CheckersGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Jeu de Dames")
        self.board_size = 8
        self.cell_size = 60
        self.board = []
        self.selected_piece = None
        self.current_turn = "white"

        self.canvas = tk.Canvas(
            root, width=self.board_size * self.cell_size, height=self.board_size * self.cell_size
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.init_board()
        self.draw_board()

    def init_board(self):
        self.board = [["" for _ in range(self.board_size)] for _ in range(self.board_size)]

        for row in range(self.board_size):
            for col in range(self.board_size):
                if (row + col) % 2 == 1:
                    if row < 3:
                        self.board[row][col] = "black"
                    elif row > 4:
                        self.board[row][col] = "white"

    def draw_board(self):
        self.canvas.delete("all")
        for row in range(self.board_size):
            for col in range(self.board_size):
                x1 = col * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                fill_color = "white" if (row + col) % 2 == 0 else "gray"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color)

                piece = self.board[row][col]
                if piece:
                    color = "white" if piece.startswith("white") else "black"
                    outline = "gold" if "king" in piece else "blue"
                    self.canvas.create_oval(
                        x1 + 10, y1 + 10, x2 - 10, y2 - 10, fill=color, outline=outline, width=2
                    )

    def on_click(self, event):
        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if self.selected_piece:
            self.move_piece(row, col)
        elif self.board[row][col].startswith(self.current_turn):
            self.selected_piece = (row, col)

    def move_piece(self, new_row, new_col):
        old_row, old_col = self.selected_piece
        if self.is_valid_move(old_row, old_col, new_row, new_col):
            piece = self.board[old_row][old_col]
            self.board[new_row][new_col] = piece
            self.board[old_row][old_col] = ""

            if abs(new_row - old_row) > 1:  # Capture
                middle_row = (old_row + new_row) // 2
                middle_col = (old_col + new_col) // 2
                self.board[middle_row][middle_col] = ""

            self.promote_to_king(new_row, new_col)

            # Vérifier si une capture supplémentaire est possible
            if self.can_capture(new_row, new_col):
                self.selected_piece = (new_row, new_col)
                self.draw_board()
                return

            self.switch_turn()
        else:
            messagebox.showerror("Erreur", "Mouvement non valide !")

        self.selected_piece = None
        self.draw_board()
        self.check_game_over()

    def is_valid_move(self, old_row, old_col, new_row, new_col):
        piece = self.board[old_row][old_col]

        if self.board[new_row][new_col] != "":
            return False

        if "king" in piece:  # Dame
            return self.is_valid_king_move(old_row, old_col, new_row, new_col)

        # Pièces normales
        if abs(new_row - old_row) == 1 and abs(new_col - old_col) == 1:
            return not self.must_capture()
        if abs(new_row - old_row) == 2 and abs(new_col - old_col) == 2:
            middle_row = (old_row + new_row) // 2
            middle_col = (old_col + new_col) // 2
            return (
                self.board[middle_row][middle_col].startswith(
                    "black" if self.current_turn == "white" else "white"
                )
                and self.board[new_row][new_col] == ""
            )
        return False

    def is_valid_king_move(self, old_row, old_col, new_row, new_col):
        if abs(new_row - old_row) != abs(new_col - old_col):
            return False
        step_row = 1 if new_row > old_row else -1
        step_col = 1 if new_col > old_col else -1
        r, c = old_row + step_row, old_col + step_col
        encountered_pieces = 0
        while r != new_row and c != new_col:
            if self.board[r][c] != "":
                encountered_pieces += 1
            r += step_row
            c += step_col
        return encountered_pieces == 1

    def must_capture(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col].startswith(self.current_turn):
                    if self.can_capture(row, col):
                        return True
        return False

    def can_capture(self, row, col):
        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        piece = self.board[row][col]

        if "king" in piece:  # Vérifier toutes les directions possibles pour une dame
            for step_row, step_col in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                r, c = row + step_row, col + step_col
                while 0 <= r < self.board_size and 0 <= c < self.board_size:
                    if self.board[r][c] == "":
                        r += step_row
                        c += step_col
                        continue
                    if self.board[r][c].startswith(
                        "black" if self.current_turn == "white" else "white"
                    ):
                        r += step_row
                        c += step_col
                        if 0 <= r < self.board_size and 0 <= c < self.board_size and self.board[r][c] == "":
                            return True
                    break
        else:  # Pièces normales
            for dr, dc in directions:
                middle_row = row + dr // 2
                middle_col = col + dc // 2
                new_row, new_col = row + dr, col + dc
                if (
                    0 <= new_row < self.board_size
                    and 0 <= new_col < self.board_size
                    and self.board[middle_row][middle_col].startswith(
                        "black" if self.current_turn == "white" else "white"
                    )
                    and self.board[new_row][new_col] == ""
                ):
                    return True
        return False

    def promote_to_king(self, row, col):
        if row == 0 and self.board[row][col] == "white":
            self.board[row][col] = "white_king"
        elif row == self.board_size - 1 and self.board[row][col] == "black":
            self.board[row][col] = "black_king"

    def switch_turn(self):
        self.current_turn = "white" if self.current_turn == "black" else "black"
        self.root.title(f"Tour : {self.current_turn}")

    def check_game_over(self):
        white_pieces = sum(row.count("white") + row.count("white_king") for row in self.board)
        black_pieces = sum(row.count("black") + row.count("black_king") for row in self.board)
        if white_pieces == 0 or black_pieces == 0:
            winner = "Noir" if white_pieces == 0 else "Blanc"
            messagebox.showinfo("Fin de la partie", f"Le joueur {winner} a gagné !")
            self.root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    game = CheckersGame(root)
    root.mainloop()