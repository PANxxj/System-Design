"""
SNAKE AND LADDER GAME - Interview Level
========================================

Problem Statement:
Design a Snake and Ladder board game.

Requirements:
1. Board with configurable size
2. Snakes and ladders
3. Multiple players
4. Dice rolling
5. Turn management
6. Win condition
7. Game state tracking

Design Patterns:
- Builder (Board creation)
- Strategy (Dice rolling)
- Template Method (Game flow)

Time Complexity: O(1) for moves
Space Complexity: O(n) for board
"""

import random
from typing import Dict, List, Optional
from enum import Enum


class Dice:
    """Represents a dice"""

    def __init__(self, num_faces: int = 6):
        self.num_faces = num_faces

    def roll(self) -> int:
        """Roll the dice"""
        return random.randint(1, self.num_faces)


class Snake:
    """Represents a snake"""

    def __init__(self, head: int, tail: int):
        if head <= tail:
            raise ValueError("Snake head must be greater than tail!")
        self.head = head
        self.tail = tail

    def __str__(self):
        return f"Snake: {self.head} → {self.tail}"


class Ladder:
    """Represents a ladder"""

    def __init__(self, start: int, end: int):
        if start >= end:
            raise ValueError("Ladder start must be less than end!")
        self.start = start
        self.end = end

    def __str__(self):
        return f"Ladder: {self.start} → {self.end}"


class Player:
    """Represents a player"""

    def __init__(self, name: str, player_id: int):
        self.name = name
        self.player_id = player_id
        self.position = 0  # Starting position (off board)

    def move(self, steps: int):
        """Move player by given steps"""
        self.position += steps

    def __str__(self):
        return f"{self.name} (Position: {self.position})"


class Board:
    """Represents the game board"""

    def __init__(self, size: int = 100):
        self.size = size
        self.snakes: Dict[int, Snake] = {}  # head -> Snake
        self.ladders: Dict[int, Ladder] = {}  # start -> Ladder

    def add_snake(self, snake: Snake):
        """Add a snake to the board"""
        if snake.head > self.size or snake.tail < 1:
            raise ValueError(f"Snake positions out of board range!")
        self.snakes[snake.head] = snake

    def add_ladder(self, ladder: Ladder):
        """Add a ladder to the board"""
        if ladder.end > self.size or ladder.start < 1:
            raise ValueError(f"Ladder positions out of board range!")
        self.ladders[ladder.start] = ladder

    def get_final_position(self, position: int) -> int:
        """Get final position after snakes/ladders"""
        # Check for snake
        if position in self.snakes:
            snake = self.snakes[position]
            print(f"    🐍 Snake bite! {position} → {snake.tail}")
            return snake.tail

        # Check for ladder
        if position in self.ladders:
            ladder = self.ladders[position]
            print(f"    🪜 Ladder climb! {position} → {ladder.end}")
            return ladder.end

        return position

    def display_snakes_and_ladders(self):
        """Display all snakes and ladders"""
        print("\n" + "="*50)
        print("BOARD CONFIGURATION")
        print("="*50)

        print(f"\nBoard Size: {self.size} squares\n")

        print("Snakes:")
        if not self.snakes:
            print("  None")
        else:
            for snake in self.snakes.values():
                print(f"  {snake}")

        print("\nLadders:")
        if not self.ladders:
            print("  None")
        else:
            for ladder in self.ladders.values():
                print(f"  {ladder}")

        print("="*50 + "\n")


class Game:
    """Main game class"""

    def __init__(self, board: Board, players: List[Player]):
        self.board = board
        self.players = players
        self.dice = Dice(6)
        self.current_player_index = 0
        self.winner: Optional[Player] = None
        self.turn_count = 0

    def get_current_player(self) -> Player:
        """Get current player"""
        return self.players[self.current_player_index]

    def next_player(self):
        """Move to next player"""
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def play_turn(self) -> bool:
        """Play one turn. Returns True if game is over"""
        self.turn_count += 1
        player = self.get_current_player()

        print(f"\nTurn {self.turn_count}: {player.name}'s turn (Position: {player.position})")

        # Roll dice
        dice_value = self.dice.roll()
        print(f"  🎲 Rolled: {dice_value}")

        # Calculate new position
        new_position = player.position + dice_value

        # Check if exceeds board size
        if new_position > self.board.size:
            print(f"  ❌ Cannot move! Need exact roll to win. (Would reach {new_position})")
            self.next_player()
            return False

        # Move player
        player.position = new_position
        print(f"  Moved to: {player.position}")

        # Check for snakes/ladders
        final_position = self.board.get_final_position(player.position)
        player.position = final_position

        # Check for win
        if player.position == self.board.size:
            self.winner = player
            print(f"\n🎉 {player.name} WINS! 🎉")
            return True

        print(f"  Final position: {player.position}")

        # Next player
        self.next_player()
        return False

    def play_game(self, max_turns: int = 100):
        """Play the complete game"""
        print("\n" + "="*60)
        print("GAME START!".center(60))
        print("="*60)

        print("\nPlayers:")
        for player in self.players:
            print(f"  - {player.name}")

        self.board.display_snakes_and_ladders()

        # Play turns until someone wins or max turns reached
        game_over = False
        while not game_over and self.turn_count < max_turns:
            game_over = self.play_turn()

        if self.winner:
            print("\n" + "="*60)
            print(f"WINNER: {self.winner.name}".center(60))
            print(f"Turns taken: {self.turn_count}".center(60))
            print("="*60 + "\n")
        else:
            print(f"\n⚠️  Game ended after {max_turns} turns without a winner.")

        # Display final positions
        print("\nFinal Positions:")
        sorted_players = sorted(self.players, key=lambda p: p.position, reverse=True)
        for i, player in enumerate(sorted_players, 1):
            print(f"  {i}. {player}")

    def reset(self):
        """Reset the game"""
        for player in self.players:
            player.position = 0
        self.current_player_index = 0
        self.winner = None
        self.turn_count = 0


class GameBuilder:
    """Builder for creating game with custom configuration"""

    def __init__(self):
        self.board_size = 100
        self.snakes = []
        self.ladders = []
        self.players = []

    def set_board_size(self, size: int):
        """Set board size"""
        self.board_size = size
        return self

    def add_snake(self, head: int, tail: int):
        """Add a snake"""
        self.snakes.append(Snake(head, tail))
        return self

    def add_ladder(self, start: int, end: int):
        """Add a ladder"""
        self.ladders.append(Ladder(start, end))
        return self

    def add_player(self, name: str):
        """Add a player"""
        player_id = len(self.players) + 1
        self.players.append(Player(name, player_id))
        return self

    def build(self) -> Game:
        """Build and return the game"""
        # Create board
        board = Board(self.board_size)

        # Add snakes
        for snake in self.snakes:
            board.add_snake(snake)

        # Add ladders
        for ladder in self.ladders:
            board.add_ladder(ladder)

        # Create game
        return Game(board, self.players)


def run_demo():
    """Run snake and ladder demo"""
    print("\n" + "="*70)
    print("SNAKE AND LADDER GAME - DEMO".center(70))
    print("="*70 + "\n")

    # Build game using builder pattern
    game = (GameBuilder()
            .set_board_size(100)
            # Add snakes
            .add_snake(99, 54)
            .add_snake(70, 55)
            .add_snake(52, 42)
            .add_snake(25, 2)
            .add_snake(95, 72)
            # Add ladders
            .add_ladder(6, 25)
            .add_ladder(11, 40)
            .add_ladder(60, 85)
            .add_ladder(46, 90)
            .add_ladder(17, 69)
            # Add players
            .add_player("Alice")
            .add_player("Bob")
            .add_player("Charlie")
            .build())

    # Play the game
    game.play_game(max_turns=200)

    print("\n" + "="*70)
    print("DEMO COMPLETE".center(70))
    print("="*70 + "\n")


def run_custom_demo():
    """Run a small demo for quick testing"""
    print("\n" + "="*70)
    print("SNAKE AND LADDER - QUICK DEMO".center(70))
    print("="*70 + "\n")

    # Small board for quick game
    game = (GameBuilder()
            .set_board_size(30)
            .add_snake(28, 10)
            .add_snake(21, 9)
            .add_ladder(4, 14)
            .add_ladder(12, 26)
            .add_player("Player 1")
            .add_player("Player 2")
            .build())

    game.play_game(max_turns=50)


if __name__ == "__main__":
    # Run full demo
    run_demo()

    # Uncomment for quick demo
    # run_custom_demo()


"""
INTERVIEW DISCUSSION POINTS:
=============================

1. REQUIREMENTS CLARIFICATION:
   - Board size (standard is 100)?
   - Number of players?
   - Dice type (1 or 2 dice)?
   - Exact roll needed to win?
   - Multiple snakes/ladders per square?

2. DESIGN CHOICES:
   - Builder pattern for game creation
   - Separate Snake, Ladder, Board, Player classes
   - Dictionary for O(1) snake/ladder lookup
   - Turn-based gameplay with round-robin

3. RULES VARIATIONS:
   - Exact roll to win vs overshoot allowed
   - Multiple dice
   - Special squares (lose turn, extra roll)
   - Power-ups
   - Team mode

4. EXTENSIONS:
   - Save/load game state
   - Multiplayer online
   - Custom board designer
   - Statistics tracking
   - Replay functionality
   - AI players
   - Animated GUI

5. OPTIMIZATIONS:
   - Cache snake/ladder positions
   - Validate board configuration
   - Prevent snake-ladder loops
   - Random board generation

6. EDGE CASES:
   - Snake head on finish square
   - Ladder end on finish square
   - Overlapping snakes/ladders
   - Single player game
   - No snakes/no ladders

7. COMPLEXITY:
   - Play turn: O(1)
   - Check snake/ladder: O(1) with dictionary
   - Complete game: O(k) where k=number of turns

8. VARIATIONS:
   - Chutes and Ladders (American version)
   - Different board layouts
   - Theme-based boards
   - Educational versions (math facts on ladders)

9. REAL-WORLD:
   - Mobile app
   - Multiplayer with friends
   - Achievements and leaderboards
   - In-app purchases (board themes)
   - Social media integration
"""
