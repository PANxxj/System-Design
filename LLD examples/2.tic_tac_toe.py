"""
TIC-TAC-TOE GAME - Interview Level
===================================

Problem Statement:
Design a Tic-Tac-Toe game for 2 players.

Requirements:
1. 3x3 board
2. Two players (X and O)
3. Turn-based gameplay
4. Win detection (row, column, diagonal)
5. Draw detection
6. Input validation

Design Patterns:
- Strategy (Win detection algorithms)
- Template Method (Game flow)

Time Complexity: O(1) for each move, O(n) for win check
Space Complexity: O(n²) for board
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from enum import Enum


class Symbol(Enum):
    X = "X"
    O = "O"
    EMPTY = " "


class Player:
    def __init__(self, name: str, symbol: Symbol):
        self.name = name
        self.symbol = symbol

    def __str__(self):
        return f"{self.name} ({self.symbol.value})"


class Board:
    def __init__(self, size: int = 3):
        self.size = size
        self.grid = [[Symbol.EMPTY for _ in range(size)] for _ in range(size)]
        self.moves_count = 0

    def is_valid_move(self, row: int, col: int) -> bool:
        """Check if move is valid"""
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
        return self.grid[row][col] == Symbol.EMPTY

    def make_move(self, row: int, col: int, symbol: Symbol) -> bool:
        """Place symbol on board"""
        if self.is_valid_move(row, col):
            self.grid[row][col] = symbol
            self.moves_count += 1
            return True
        return False

    def is_full(self) -> bool:
        """Check if board is full"""
        return self.moves_count == self.size * self.size

    def check_winner(self, symbol: Symbol) -> bool:
        """Check if given symbol has won"""
        # Check rows
        for row in self.grid:
            if all(cell == symbol for cell in row):
                return True

        # Check columns
        for col in range(self.size):
            if all(self.grid[row][col] == symbol for row in range(self.size)):
                return True

        # Check diagonals
        if all(self.grid[i][i] == symbol for i in range(self.size)):
            return True
        if all(self.grid[i][self.size - 1 - i] == symbol for i in range(self.size)):
            return True

        return False

    def reset(self):
        """Reset the board"""
        self.grid = [[Symbol.EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.moves_count = 0

    def display(self):
        """Display the board"""
        print("\n" + "=" * 13)
        for i, row in enumerate(self.grid):
            print(f" {row[0].value} | {row[1].value} | {row[2].value} ")
            if i < self.size - 1:
                print("---|---|---")
        print("=" * 13 + "\n")


class Game:
    def __init__(self, player1: Player, player2: Player):
        self.board = Board()
        self.players = [player1, player2]
        self.current_player_index = 0
        self.winner: Optional[Player] = None
        self.is_draw = False

    def get_current_player(self) -> Player:
        """Get current player"""
        return self.players[self.current_player_index]

    def switch_player(self):
        """Switch to next player"""
        self.current_player_index = 1 - self.current_player_index

    def play_turn(self, row: int, col: int) -> bool:
        """Play a turn"""
        current_player = self.get_current_player()

        # Validate and make move
        if not self.board.make_move(row, col, current_player.symbol):
            print("❌ Invalid move! Try again.")
            return False

        print(f"✓ {current_player.name} placed {current_player.symbol.value} at ({row}, {col})")
        self.board.display()

        # Check for winner
        if self.board.check_winner(current_player.symbol):
            self.winner = current_player
            return True

        # Check for draw
        if self.board.is_full():
            self.is_draw = True
            return True

        # Switch player
        self.switch_player()
        return False

    def is_game_over(self) -> bool:
        """Check if game is over"""
        return self.winner is not None or self.is_draw

    def get_result(self) -> str:
        """Get game result"""
        if self.winner:
            return f"🎉 {self.winner.name} wins!"
        elif self.is_draw:
            return "🤝 It's a draw!"
        return "Game in progress"

    def reset(self):
        """Reset the game"""
        self.board.reset()
        self.current_player_index = 0
        self.winner = None
        self.is_draw = False


def run_demo():
    """Run automated demo"""
    print("\n" + "="*50)
    print("TIC-TAC-TOE GAME - DEMO".center(50))
    print("="*50 + "\n")

    # Create players
    player1 = Player("Alice", Symbol.X)
    player2 = Player("Bob", Symbol.O)

    # Create game
    game = Game(player1, player2)

    print(f"Players: {player1} vs {player2}\n")
    print("Initial Board:")
    game.board.display()

    # Simulated game moves
    # X | O | X
    # O | X | O
    # O | X | X
    moves = [
        (0, 0),  # X
        (0, 1),  # O
        (1, 1),  # X
        (1, 0),  # O
        (0, 2),  # X
        (1, 2),  # O
        (2, 1),  # X - Wins (middle column)
    ]

    print("Playing automated game...\n")
    for i, (row, col) in enumerate(moves):
        print(f"Move {i + 1}: {game.get_current_player().name}'s turn")
        game_over = game.play_turn(row, col)

        if game_over:
            break

    print(game.get_result())

    # Demo 2: Draw game
    print("\n" + "="*50)
    print("DEMO 2: DRAW GAME".center(50))
    print("="*50 + "\n")

    game.reset()
    print("Board reset. Playing draw game...\n")

    # X | O | X
    # X | O | O
    # O | X | X
    draw_moves = [
        (0, 0),  # X
        (0, 1),  # O
        (0, 2),  # X
        (1, 2),  # O
        (1, 1),  # X
        (1, 0),  # O - hmm, this would win
        (2, 1),  # X
        (2, 0),  # O
        (2, 2),  # X
    ]

    # Better draw scenario
    # X | X | O
    # O | O | X
    # X | O | X
    draw_moves = [
        (0, 0),  # X
        (0, 2),  # O
        (1, 2),  # X
        (1, 0),  # O
        (2, 2),  # X
        (1, 1),  # O
        (0, 1),  # X
        (2, 0),  # O - this would win actually

        # Let's do proper draw
    ]

    # Proper draw: X | X | O
    #              O | O | X
    #              X | X | O
    draw_moves = [
        (0, 0),  # X
        (0, 2),  # O
        (0, 1),  # X
        (1, 0),  # O
        (1, 2),  # X
        (1, 1),  # O
        (2, 0),  # X
        (2, 2),  # O
        (2, 1),  # X - Draw
    ]

    for i, (row, col) in enumerate(draw_moves):
        print(f"Move {i + 1}: {game.get_current_player().name}'s turn")
        game_over = game.play_turn(row, col)
        if game_over:
            break

    print(game.get_result())

    print("\n" + "="*50)
    print("DEMO COMPLETE".center(50))
    print("="*50 + "\n")


def run_interactive():
    """Run interactive game"""
    print("\n" + "="*50)
    print("TIC-TAC-TOE GAME - INTERACTIVE MODE".center(50))
    print("="*50 + "\n")

    # Get player names
    name1 = input("Enter Player 1 name: ").strip() or "Player 1"
    name2 = input("Enter Player 2 name: ").strip() or "Player 2"

    player1 = Player(name1, Symbol.X)
    player2 = Player(name2, Symbol.O)

    game = Game(player1, player2)

    print(f"\n{player1} vs {player2}")
    print("Enter moves as: row col (e.g., '0 0' for top-left)")
    print("Board positions:")
    print("  0 1 2")
    print("0 . . .")
    print("1 . . .")
    print("2 . . .")

    game.board.display()

    while not game.is_game_over():
        current_player = game.get_current_player()
        print(f"{current_player}'s turn")

        try:
            move = input("Enter move (row col): ").strip().split()
            if len(move) != 2:
                print("❌ Invalid input! Enter row and column separated by space.")
                continue

            row, col = int(move[0]), int(move[1])
            game.play_turn(row, col)

        except ValueError:
            print("❌ Invalid input! Enter numbers only.")
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\n" + "="*50)
    print(game.get_result())
    print("="*50 + "\n")


if __name__ == "__main__":
    # Run demo
    run_demo()

    # Uncomment to play interactively
    # run_interactive()


"""
INTERVIEW DISCUSSION POINTS:
=============================

1. REQUIREMENTS CLARIFICATION:
   - Board size (3x3 standard, or NxN?)
   - Number of players (2 standard, or more?)
   - AI player needed?
   - Undo/Redo feature?

2. DESIGN CHOICES:
   - Separate Board and Game classes (SRP)
   - Enum for symbols (type safety)
   - Simple win detection O(n) per check

3. EXTENSIONS:
   - Variable board size (NxN)
   - AI player with minimax algorithm
   - Undo last move
   - Game history/replay
   - Network multiplayer
   - Tournament mode

4. OPTIMIZATIONS:
   - Cache win conditions
   - Early termination in win check
   - Bitboard representation for large boards

5. TIME COMPLEXITY:
   - Make move: O(1)
   - Check winner: O(n) where n=board size
   - Total game: O(n³) worst case

6. SPACE COMPLEXITY:
   - Board: O(n²)
   - Game state: O(1)
"""
