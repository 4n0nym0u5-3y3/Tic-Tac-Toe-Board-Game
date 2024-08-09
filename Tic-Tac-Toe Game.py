import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple

class Competitor(NamedTuple):
    symbol: str
    color: str

class Position(NamedTuple):
    row: int
    col: int
    symbol: str = ""

GRID_SIZE = 3
DEFAULT_COMPETITORS = (
    Competitor(symbol="X", color="blue"),
    Competitor(symbol="O", color="green"),
)

class TicTacToe:
    def __init__(self, competitors=DEFAULT_COMPETITORS, grid_size=GRID_SIZE):
        self._competitors = cycle(competitors)
        self.grid_size = grid_size
        self.active_competitor = next(self._competitors)
        self.winning_positions = []
        self._current_board = []
        self._game_won = False
        self._winning_combinations = []
        self._initialize_grid()

    def _initialize_grid(self):
        self._current_board = [
            [Position(row, col) for col in range(self.grid_size)]
            for row in range(self.grid_size)
        ]
        self._winning_combinations = self._calculate_winning_combinations()

    def _calculate_winning_combinations(self):
        rows = [
            [(position.row, position.col) for position in row]
            for row in self._current_board
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]

    def switch_competitor(self):
        """Switch to the next competitor."""
        self.active_competitor = next(self._competitors)

    def is_move_allowed(self, position):
        """Check if the move is allowed."""
        row, col = position.row, position.col
        position_not_filled = self._current_board[row][col].symbol == ""
        no_winner_yet = not self._game_won
        return no_winner_yet and position_not_filled

    def execute_move(self, position):
        """Execute the current move and check for a win."""
        row, col = position.row, position.col
        self._current_board[row][col] = position
        for combo in self._winning_combinations:
            symbols_in_combo = set(self._current_board[n][m].symbol for n, m in combo)
            is_win = (len(symbols_in_combo) == 1) and ("" not in symbols_in_combo)
            if is_win:
                self._game_won = True
                self.winning_positions = combo
                break

    def check_winner(self):
        """Return True if there is a winner, otherwise False."""
        return self._game_won

    def check_draw(self):
        """Return True if the game is a draw, otherwise False."""
        no_winner = not self._game_won
        all_positions_filled = (
            position.symbol for row in self._current_board for position in row
        )
        return no_winner and all(all_positions_filled)

    def restart_game(self):
        """Reset the game state for a new round."""
        for row, row_content in enumerate(self._current_board):
            for col, _ in enumerate(row_content):
                row_content[col] = Position(row, col)
        self._game_won = False
        self.winning_positions = []

class TicTacToeInterface(tk.Tk):
    def __init__(self, game):
        super().__init__()
        self.title("Tic-Tac-Toe Game")
        self._cells = {}
        self._game = game
        self._build_menu()
        self._build_display()
        self._build_grid()

    def _build_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(label="Restart Game", command=self.restart_grid)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

    def _build_display(self):
        display_frame = tk.Frame(master=self)
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master=display_frame,
            text="Ready to play?",
            font=font.Font(size=28, weight="bold"),
        )
        self.display.pack()

    def _build_grid(self):
        grid_frame = tk.Frame(master=self)
        grid_frame.pack()
        for row in range(self._game.grid_size):
            self.rowconfigure(row, weight=1, minsize=50)
            self.columnconfigure(row, weight=1, minsize=75)
            for col in range(self._game.grid_size):
                button = tk.Button(
                    master=grid_frame,
                    text="",
                    font=font.Font(size=36, weight="bold"),
                    fg="black",
                    width=3,
                    height=2,
                    highlightbackground="lightblue",
                )
                self._cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self.make_move)
                button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

    def make_move(self, event):
        """Process a player's move."""
        clicked_btn = event.widget
        row, col = self._cells[clicked_btn]
        position = Position(row, col, self._game.active_competitor.symbol)
        if self._game.is_move_allowed(position):
            self._update_button(clicked_btn)
            self._game.execute_move(position)
            if self._game.check_draw():
                self._update_display(msg="It's a draw!", color="red")
            elif self._game.check_winner():
                self._highlight_winning_positions()
                msg = f'Player "{self._game.active_competitor.symbol}" wins!'
                color = self._game.active_competitor.color
                self._update_display(msg, color)
            else:
                self._game.switch_competitor()
                msg = f"{self._game.active_competitor.symbol}'s turn"
                self._update_display(msg)

    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.active_competitor.symbol)
        clicked_btn.config(fg=self._game.active_competitor.color)

    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

    def _highlight_winning_positions(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winning_positions:
                button.config(highlightbackground="red")

    def restart_grid(self):
        """Reset the grid to start a new game."""
        self._game.restart_game()
        self._update_display(msg="Ready to play?")
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")

def start_game():
    """Initialize and start the Tic-Tac-Toe game."""
    game = TicTacToe()
    interface = TicTacToeInterface(game)
    interface.mainloop()

if __name__ == "__main__":
    start_game()
