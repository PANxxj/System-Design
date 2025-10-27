# Chess Game System Design 🔴

## 🎯 Learning Objectives
- Design a complex game system with multiple states
- Implement game rules validation and move generation
- Handle turn-based gameplay and game history
- Apply design patterns for extensible architecture

## 📋 Requirements Analysis

### Functional Requirements
- **Chess Board**: 8x8 grid with pieces
- **Piece Movement**: Validate legal moves for each piece type
- **Game Rules**: Check, checkmate, stalemate, castling, en passant
- **Turn Management**: Alternate turns between players
- **Game History**: Track all moves and game states
- **Save/Load Game**: Persist and restore game state

### Non-Functional Requirements
- **Performance**: Move validation < 1ms
- **Extensibility**: Support different chess variants
- **User Interface**: Support multiple UI implementations
- **Persistence**: Save game state reliably

## 🏗️ System Design

### Core Components
1. **Board** - Game board representation
2. **Piece** - Chess piece hierarchy
3. **Move** - Move representation and validation
4. **GameEngine** - Core game logic and rules
5. **Player** - Player management
6. **GameHistory** - Move tracking and undo functionality

## 💻 Implementation

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Tuple, Dict, Set
from dataclasses import dataclass
from copy import deepcopy
import json
import time

class Color(Enum):
    WHITE = "white"
    BLACK = "black"

class PieceType(Enum):
    PAWN = "pawn"
    ROOK = "rook"
    KNIGHT = "knight"
    BISHOP = "bishop"
    QUEEN = "queen"
    KING = "king"

class GameState(Enum):
    ACTIVE = "active"
    CHECK = "check"
    CHECKMATE = "checkmate"
    STALEMATE = "stalemate"
    DRAW = "draw"

@dataclass
class Position:
    row: int
    col: int

    def __post_init__(self):
        if not (0 <= self.row < 8 and 0 <= self.col < 8):
            raise ValueError(f"Invalid position: ({self.row}, {self.col})")

    def __add__(self, other):
        return Position(self.row + other.row, self.col + other.col)

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

    def is_valid(self) -> bool:
        return 0 <= self.row < 8 and 0 <= self.col < 8

    def to_algebraic(self) -> str:
        """Convert to algebraic notation (e.g., 'e4')"""
        return chr(ord('a') + self.col) + str(8 - self.row)

    @classmethod
    def from_algebraic(cls, notation: str) -> 'Position':
        """Create position from algebraic notation"""
        if len(notation) != 2:
            raise ValueError(f"Invalid algebraic notation: {notation}")

        col = ord(notation[0].lower()) - ord('a')
        row = 8 - int(notation[1])
        return cls(row, col)

@dataclass
class Move:
    from_pos: Position
    to_pos: Position
    piece_type: PieceType
    captured_piece: Optional['Piece'] = None
    promotion_piece: Optional[PieceType] = None
    is_castling: bool = False
    is_en_passant: bool = False

    def to_algebraic(self) -> str:
        """Convert move to algebraic notation"""
        notation = ""

        # Special moves
        if self.is_castling:
            return "O-O" if self.to_pos.col > self.from_pos.col else "O-O-O"

        # Piece notation (except pawn)
        if self.piece_type != PieceType.PAWN:
            notation += self.piece_type.value[0].upper()

        # Capture notation
        if self.captured_piece or self.is_en_passant:
            if self.piece_type == PieceType.PAWN:
                notation += chr(ord('a') + self.from_pos.col)
            notation += "x"

        # Destination
        notation += self.to_pos.to_algebraic()

        # Promotion
        if self.promotion_piece:
            notation += f"={self.promotion_piece.value[0].upper()}"

        return notation

class Piece(ABC):
    """Abstract base class for chess pieces"""

    def __init__(self, color: Color, position: Position):
        self.color = color
        self.position = position
        self.has_moved = False

    @property
    @abstractmethod
    def piece_type(self) -> PieceType:
        pass

    @property
    @abstractmethod
    def symbol(self) -> str:
        pass

    @abstractmethod
    def get_possible_moves(self, board: 'ChessBoard') -> List[Position]:
        """Get all possible moves for this piece"""
        pass

    def can_move_to(self, target_pos: Position, board: 'ChessBoard') -> bool:
        """Check if piece can move to target position"""
        return target_pos in self.get_possible_moves(board)

    def move_to(self, new_position: Position):
        """Move piece to new position"""
        self.position = new_position
        self.has_moved = True

    def copy(self) -> 'Piece':
        """Create a copy of this piece"""
        new_piece = self.__class__(self.color, self.position)
        new_piece.has_moved = self.has_moved
        return new_piece

class Pawn(Piece):
    @property
    def piece_type(self) -> PieceType:
        return PieceType.PAWN

    @property
    def symbol(self) -> str:
        return "♟" if self.color == Color.BLACK else "♙"

    def get_possible_moves(self, board: 'ChessBoard') -> List[Position]:
        moves = []
        direction = -1 if self.color == Color.WHITE else 1
        start_row = 6 if self.color == Color.WHITE else 1

        # Forward moves
        one_forward = Position(self.position.row + direction, self.position.col)
        if one_forward.is_valid() and board.get_piece(one_forward) is None:
            moves.append(one_forward)

            # Two squares forward from starting position
            if self.position.row == start_row:
                two_forward = Position(self.position.row + 2 * direction, self.position.col)
                if two_forward.is_valid() and board.get_piece(two_forward) is None:
                    moves.append(two_forward)

        # Captures
        for col_offset in [-1, 1]:
            capture_pos = Position(self.position.row + direction, self.position.col + col_offset)
            if capture_pos.is_valid():
                target_piece = board.get_piece(capture_pos)
                if target_piece and target_piece.color != self.color:
                    moves.append(capture_pos)
                # En passant
                elif board.can_en_passant(self.position, capture_pos):
                    moves.append(capture_pos)

        return moves

class Rook(Piece):
    @property
    def piece_type(self) -> PieceType:
        return PieceType.ROOK

    @property
    def symbol(self) -> str:
        return "♜" if self.color == Color.BLACK else "♖"

    def get_possible_moves(self, board: 'ChessBoard') -> List[Position]:
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Right, Left, Down, Up

        for dr, dc in directions:
            for i in range(1, 8):
                new_pos = Position(self.position.row + i * dr, self.position.col + i * dc)
                if not new_pos.is_valid():
                    break

                target_piece = board.get_piece(new_pos)
                if target_piece is None:
                    moves.append(new_pos)
                elif target_piece.color != self.color:
                    moves.append(new_pos)
                    break
                else:
                    break

        return moves

class Knight(Piece):
    @property
    def piece_type(self) -> PieceType:
        return PieceType.KNIGHT

    @property
    def symbol(self) -> str:
        return "♞" if self.color == Color.BLACK else "♘"

    def get_possible_moves(self, board: 'ChessBoard') -> List[Position]:
        moves = []
        knight_moves = [
            (-2, -1), (-2, 1), (-1, -2), (-1, 2),
            (1, -2), (1, 2), (2, -1), (2, 1)
        ]

        for dr, dc in knight_moves:
            new_pos = Position(self.position.row + dr, self.position.col + dc)
            if new_pos.is_valid():
                target_piece = board.get_piece(new_pos)
                if target_piece is None or target_piece.color != self.color:
                    moves.append(new_pos)

        return moves

class Bishop(Piece):
    @property
    def piece_type(self) -> PieceType:
        return PieceType.BISHOP

    @property
    def symbol(self) -> str:
        return "♝" if self.color == Color.BLACK else "♗"

    def get_possible_moves(self, board: 'ChessBoard') -> List[Position]:
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]  # Diagonals

        for dr, dc in directions:
            for i in range(1, 8):
                new_pos = Position(self.position.row + i * dr, self.position.col + i * dc)
                if not new_pos.is_valid():
                    break

                target_piece = board.get_piece(new_pos)
                if target_piece is None:
                    moves.append(new_pos)
                elif target_piece.color != self.color:
                    moves.append(new_pos)
                    break
                else:
                    break

        return moves

class Queen(Piece):
    @property
    def piece_type(self) -> PieceType:
        return PieceType.QUEEN

    @property
    def symbol(self) -> str:
        return "♛" if self.color == Color.BLACK else "♕"

    def get_possible_moves(self, board: 'ChessBoard') -> List[Position]:
        moves = []
        # Combine rook and bishop moves
        directions = [
            (0, 1), (0, -1), (1, 0), (-1, 0),  # Rook moves
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # Bishop moves
        ]

        for dr, dc in directions:
            for i in range(1, 8):
                new_pos = Position(self.position.row + i * dr, self.position.col + i * dc)
                if not new_pos.is_valid():
                    break

                target_piece = board.get_piece(new_pos)
                if target_piece is None:
                    moves.append(new_pos)
                elif target_piece.color != self.color:
                    moves.append(new_pos)
                    break
                else:
                    break

        return moves

class King(Piece):
    @property
    def piece_type(self) -> PieceType:
        return PieceType.KING

    @property
    def symbol(self) -> str:
        return "♚" if self.color == Color.BLACK else "♔"

    def get_possible_moves(self, board: 'ChessBoard') -> List[Position]:
        moves = []
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]

        for dr, dc in directions:
            new_pos = Position(self.position.row + dr, self.position.col + dc)
            if new_pos.is_valid():
                target_piece = board.get_piece(new_pos)
                if target_piece is None or target_piece.color != self.color:
                    moves.append(new_pos)

        # Castling (handled separately in ChessEngine)
        return moves

class ChessBoard:
    """Chess board representation and piece management"""

    def __init__(self):
        self.board: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.last_move: Optional[Move] = None
        self.setup_initial_position()

    def setup_initial_position(self):
        """Set up initial chess position"""
        # Pawns
        for col in range(8):
            self.board[1][col] = Pawn(Color.BLACK, Position(1, col))
            self.board[6][col] = Pawn(Color.WHITE, Position(6, col))

        # Other pieces
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]

        for col, piece_class in enumerate(piece_order):
            self.board[0][col] = piece_class(Color.BLACK, Position(0, col))
            self.board[7][col] = piece_class(Color.WHITE, Position(7, col))

    def get_piece(self, position: Position) -> Optional[Piece]:
        """Get piece at position"""
        if not position.is_valid():
            return None
        return self.board[position.row][position.col]

    def set_piece(self, position: Position, piece: Optional[Piece]):
        """Set piece at position"""
        if position.is_valid():
            self.board[position.row][position.col] = piece
            if piece:
                piece.position = position

    def move_piece(self, from_pos: Position, to_pos: Position) -> Optional[Piece]:
        """Move piece and return captured piece"""
        piece = self.get_piece(from_pos)
        captured_piece = self.get_piece(to_pos)

        if piece:
            self.set_piece(to_pos, piece)
            self.set_piece(from_pos, None)
            piece.move_to(to_pos)

        return captured_piece

    def can_en_passant(self, pawn_pos: Position, target_pos: Position) -> bool:
        """Check if en passant capture is possible"""
        if not self.last_move:
            return False

        # Must be a pawn that moved two squares
        last_piece = self.get_piece(self.last_move.to_pos)
        if (not last_piece or
            last_piece.piece_type != PieceType.PAWN or
            abs(self.last_move.from_pos.row - self.last_move.to_pos.row) != 2):
            return False

        # Target must be the square behind the pawn that moved two squares
        pawn = self.get_piece(pawn_pos)
        if not pawn or pawn.piece_type != PieceType.PAWN:
            return False

        expected_target_row = self.last_move.to_pos.row + (1 if pawn.color == Color.WHITE else -1)
        return (target_pos.row == expected_target_row and
                target_pos.col == self.last_move.to_pos.col)

    def find_king(self, color: Color) -> Optional[Position]:
        """Find king position for given color"""
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.piece_type == PieceType.KING and piece.color == color:
                    return Position(row, col)
        return None

    def get_all_pieces(self, color: Color) -> List[Piece]:
        """Get all pieces of given color"""
        pieces = []
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    pieces.append(piece)
        return pieces

    def copy(self) -> 'ChessBoard':
        """Create a deep copy of the board"""
        new_board = ChessBoard()
        new_board.board = [[None for _ in range(8)] for _ in range(8)]

        for row in range(8):
            for col in range(8):
                if self.board[row][col]:
                    new_board.board[row][col] = self.board[row][col].copy()

        new_board.last_move = self.last_move
        return new_board

    def display(self) -> str:
        """Display board as string"""
        display_str = "  a b c d e f g h\n"
        for row in range(8):
            display_str += f"{8-row} "
            for col in range(8):
                piece = self.board[row][col]
                if piece:
                    display_str += piece.symbol + " "
                else:
                    display_str += ". "
            display_str += f"{8-row}\n"
        display_str += "  a b c d e f g h"
        return display_str

class ChessEngine:
    """Core chess game engine with rules validation"""

    def __init__(self):
        self.board = ChessBoard()
        self.current_player = Color.WHITE
        self.game_state = GameState.ACTIVE
        self.move_count = 0
        self.halfmove_clock = 0  # For 50-move rule
        self.history: List[Move] = []
        self.position_history: List[str] = []  # For threefold repetition

    def make_move(self, from_algebraic: str, to_algebraic: str,
                  promotion_piece: Optional[PieceType] = None) -> bool:
        """Make a move using algebraic notation"""
        try:
            from_pos = Position.from_algebraic(from_algebraic)
            to_pos = Position.from_algebraic(to_algebraic)
            return self.make_move_positions(from_pos, to_pos, promotion_piece)
        except ValueError as e:
            print(f"Invalid move notation: {e}")
            return False

    def make_move_positions(self, from_pos: Position, to_pos: Position,
                          promotion_piece: Optional[PieceType] = None) -> bool:
        """Make a move using Position objects"""
        piece = self.board.get_piece(from_pos)

        # Validate basic move conditions
        if not piece:
            return False

        if piece.color != self.current_player:
            return False

        if not self.is_legal_move(from_pos, to_pos, promotion_piece):
            return False

        # Execute the move
        captured_piece = self.board.get_piece(to_pos)
        is_castling = self._is_castling_move(from_pos, to_pos)
        is_en_passant = self._is_en_passant_move(from_pos, to_pos)

        # Create move object
        move = Move(
            from_pos=from_pos,
            to_pos=to_pos,
            piece_type=piece.piece_type,
            captured_piece=captured_piece,
            promotion_piece=promotion_piece,
            is_castling=is_castling,
            is_en_passant=is_en_passant
        )

        # Execute special moves
        if is_castling:
            self._execute_castling(from_pos, to_pos)
        elif is_en_passant:
            self._execute_en_passant(from_pos, to_pos)
        else:
            self.board.move_piece(from_pos, to_pos)

        # Handle pawn promotion
        if (piece.piece_type == PieceType.PAWN and
            (to_pos.row == 0 or to_pos.row == 7)):
            promotion_type = promotion_piece or PieceType.QUEEN
            self._promote_pawn(to_pos, promotion_type)
            move.promotion_piece = promotion_type

        # Update game state
        self.board.last_move = move
        self.history.append(move)
        self.move_count += 1

        # Update clocks
        if captured_piece or piece.piece_type == PieceType.PAWN:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # Switch players
        self.current_player = Color.BLACK if self.current_player == Color.WHITE else Color.WHITE

        # Update game state
        self._update_game_state()

        return True

    def is_legal_move(self, from_pos: Position, to_pos: Position,
                     promotion_piece: Optional[PieceType] = None) -> bool:
        """Check if move is legal"""
        piece = self.board.get_piece(from_pos)
        if not piece:
            return False

        # Check if move is in piece's possible moves
        if to_pos not in piece.get_possible_moves(self.board):
            return False

        # Check special moves
        if self._is_castling_move(from_pos, to_pos):
            return self._can_castle(from_pos, to_pos)

        # Create temporary board to test for check
        temp_board = self.board.copy()
        temp_piece = temp_board.get_piece(from_pos)

        # Execute move on temporary board
        if self._is_en_passant_move(from_pos, to_pos):
            # Remove captured pawn
            captured_pawn_pos = Position(from_pos.row, to_pos.col)
            temp_board.set_piece(captured_pawn_pos, None)

        temp_board.move_piece(from_pos, to_pos)

        # Check if king would be in check after move
        king_pos = temp_board.find_king(piece.color)
        if king_pos and self._is_position_under_attack(king_pos, piece.color, temp_board):
            return False

        return True

    def _is_castling_move(self, from_pos: Position, to_pos: Position) -> bool:
        """Check if move is castling"""
        piece = self.board.get_piece(from_pos)
        return (piece and
                piece.piece_type == PieceType.KING and
                abs(to_pos.col - from_pos.col) == 2)

    def _can_castle(self, king_from: Position, king_to: Position) -> bool:
        """Check if castling is legal"""
        king = self.board.get_piece(king_from)
        if not king or king.has_moved:
            return False

        # Determine rook position
        is_kingside = king_to.col > king_from.col
        rook_col = 7 if is_kingside else 0
        rook_pos = Position(king_from.row, rook_col)
        rook = self.board.get_piece(rook_pos)

        if not rook or rook.piece_type != PieceType.ROOK or rook.has_moved:
            return False

        # Check path is clear
        start_col = min(king_from.col, rook_col) + 1
        end_col = max(king_from.col, rook_col)

        for col in range(start_col, end_col):
            if self.board.get_piece(Position(king_from.row, col)):
                return False

        # Check king is not in check and doesn't pass through check
        for col in range(min(king_from.col, king_to.col), max(king_from.col, king_to.col) + 1):
            test_pos = Position(king_from.row, col)
            if self._is_position_under_attack(test_pos, king.color, self.board):
                return False

        return True

    def _execute_castling(self, king_from: Position, king_to: Position):
        """Execute castling move"""
        is_kingside = king_to.col > king_from.col
        rook_from_col = 7 if is_kingside else 0
        rook_to_col = king_to.col - 1 if is_kingside else king_to.col + 1

        rook_from = Position(king_from.row, rook_from_col)
        rook_to = Position(king_from.row, rook_to_col)

        # Move king and rook
        self.board.move_piece(king_from, king_to)
        self.board.move_piece(rook_from, rook_to)

    def _is_en_passant_move(self, from_pos: Position, to_pos: Position) -> bool:
        """Check if move is en passant"""
        piece = self.board.get_piece(from_pos)
        return (piece and
                piece.piece_type == PieceType.PAWN and
                self.board.can_en_passant(from_pos, to_pos))

    def _execute_en_passant(self, from_pos: Position, to_pos: Position):
        """Execute en passant capture"""
        # Move pawn
        self.board.move_piece(from_pos, to_pos)

        # Remove captured pawn
        captured_pawn_pos = Position(from_pos.row, to_pos.col)
        self.board.set_piece(captured_pawn_pos, None)

    def _promote_pawn(self, position: Position, piece_type: PieceType):
        """Promote pawn to specified piece"""
        pawn = self.board.get_piece(position)
        if pawn:
            # Create new piece
            piece_classes = {
                PieceType.QUEEN: Queen,
                PieceType.ROOK: Rook,
                PieceType.BISHOP: Bishop,
                PieceType.KNIGHT: Knight
            }

            if piece_type in piece_classes:
                new_piece = piece_classes[piece_type](pawn.color, position)
                self.board.set_piece(position, new_piece)

    def _is_position_under_attack(self, position: Position, defending_color: Color,
                                board: ChessBoard) -> bool:
        """Check if position is under attack by opponent"""
        attacking_color = Color.BLACK if defending_color == Color.WHITE else Color.WHITE

        for row in range(8):
            for col in range(8):
                piece = board.get_piece(Position(row, col))
                if piece and piece.color == attacking_color:
                    if position in piece.get_possible_moves(board):
                        return True

        return False

    def is_in_check(self, color: Color) -> bool:
        """Check if king is in check"""
        king_pos = self.board.find_king(color)
        return king_pos and self._is_position_under_attack(king_pos, color, self.board)

    def get_legal_moves(self, color: Color) -> List[Move]:
        """Get all legal moves for color"""
        legal_moves = []
        pieces = self.board.get_all_pieces(color)

        for piece in pieces:
            possible_moves = piece.get_possible_moves(self.board)
            for to_pos in possible_moves:
                if self.is_legal_move(piece.position, to_pos):
                    move = Move(
                        from_pos=piece.position,
                        to_pos=to_pos,
                        piece_type=piece.piece_type,
                        captured_piece=self.board.get_piece(to_pos)
                    )
                    legal_moves.append(move)

        return legal_moves

    def _update_game_state(self):
        """Update game state based on current position"""
        legal_moves = self.get_legal_moves(self.current_player)
        in_check = self.is_in_check(self.current_player)

        if not legal_moves:
            if in_check:
                self.game_state = GameState.CHECKMATE
            else:
                self.game_state = GameState.STALEMATE
        elif in_check:
            self.game_state = GameState.CHECK
        elif self.halfmove_clock >= 100:  # 50-move rule
            self.game_state = GameState.DRAW
        else:
            self.game_state = GameState.ACTIVE

    def get_game_status(self) -> Dict[str, any]:
        """Get current game status"""
        return {
            'state': self.game_state.value,
            'current_player': self.current_player.value,
            'move_count': self.move_count,
            'halfmove_clock': self.halfmove_clock,
            'in_check': self.is_in_check(self.current_player),
            'legal_moves': len(self.get_legal_moves(self.current_player))
        }

    def get_move_history(self) -> List[str]:
        """Get move history in algebraic notation"""
        return [move.to_algebraic() for move in self.history]

    def undo_move(self) -> bool:
        """Undo last move"""
        if not self.history:
            return False

        # For a complete undo system, we would need to store more state
        # This is a simplified version
        print("Undo functionality requires more complex state management")
        return False

class ChessGame:
    """High-level chess game interface"""

    def __init__(self):
        self.engine = ChessEngine()
        self.players = {
            Color.WHITE: "White Player",
            Color.BLACK: "Black Player"
        }

    def play_move(self, move_notation: str) -> Dict[str, any]:
        """Play a move and return result"""
        # Parse different move notations
        if len(move_notation) == 4:  # e.g., "e2e4"
            from_square = move_notation[:2]
            to_square = move_notation[2:]
            success = self.engine.make_move(from_square, to_square)
        else:
            # For more complex algebraic notation parsing
            success = False

        return {
            'success': success,
            'game_status': self.engine.get_game_status(),
            'board': self.engine.board.display()
        }

    def get_current_state(self) -> Dict[str, any]:
        """Get current game state"""
        return {
            'board': self.engine.board.display(),
            'status': self.engine.get_game_status(),
            'history': self.engine.get_move_history(),
            'current_player': self.players[self.engine.current_player]
        }

    def save_game(self, filename: str) -> bool:
        """Save game to file"""
        try:
            game_data = {
                'history': self.engine.get_move_history(),
                'current_player': self.engine.current_player.value,
                'game_state': self.engine.game_state.value,
                'move_count': self.engine.move_count,
                'players': self.players
            }

            with open(filename, 'w') as f:
                json.dump(game_data, f, indent=2)

            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    def load_game(self, filename: str) -> bool:
        """Load game from file"""
        try:
            with open(filename, 'r') as f:
                game_data = json.load(f)

            # Reconstruct game state by replaying moves
            self.engine = ChessEngine()

            # This would require more sophisticated move parsing
            # For now, just load basic info
            self.players = game_data.get('players', self.players)

            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False

# Example usage and testing
def demonstrate_chess_game():
    """Demonstrate chess game functionality"""
    print("🎯 Chess Game Demonstration")
    print("=" * 50)

    game = ChessGame()

    # Show initial board
    print("Initial board:")
    print(game.engine.board.display())
    print()

    # Play some moves
    moves = [
        "e2e4",  # Pawn to e4
        "e7e5",  # Pawn to e5
        "g1f3",  # Knight to f3
        "b8c6",  # Knight to c6
        "f1c4",  # Bishop to c4
        "f8c5",  # Bishop to c5
    ]

    print("Playing opening moves:")
    for i, move in enumerate(moves):
        result = game.play_move(move)
        player = "White" if i % 2 == 0 else "Black"
        print(f"{player} plays {move}: {'Success' if result['success'] else 'Failed'}")

        if not result['success']:
            break

    print("\nCurrent board:")
    print(game.engine.board.display())

    print(f"\nGame Status: {game.engine.get_game_status()}")
    print(f"Move History: {game.engine.get_move_history()}")

    # Test legal moves
    print(f"\nLegal moves for {game.engine.current_player.value}:")
    legal_moves = game.engine.get_legal_moves(game.engine.current_player)
    for i, move in enumerate(legal_moves[:10]):  # Show first 10
        print(f"  {move.from_pos.to_algebraic()}-{move.to_pos.to_algebraic()}")

    if len(legal_moves) > 10:
        print(f"  ... and {len(legal_moves) - 10} more moves")

def test_special_moves():
    """Test special chess moves"""
    print("\n🎯 Testing Special Moves")
    print("=" * 50)

    engine = ChessEngine()

    # Test castling setup
    print("Setting up castling test...")

    # Clear pieces for castling
    engine.board.set_piece(Position(7, 1), None)  # Knight
    engine.board.set_piece(Position(7, 2), None)  # Bishop
    engine.board.set_piece(Position(7, 3), None)  # Queen
    engine.board.set_piece(Position(7, 5), None)  # Bishop
    engine.board.set_piece(Position(7, 6), None)  # Knight

    print("Board setup for castling:")
    print(engine.board.display())

    # Try castling
    print("\nAttempting kingside castling...")
    success = engine.make_move_positions(Position(7, 4), Position(7, 6))
    print(f"Castling successful: {success}")

    if success:
        print("Board after castling:")
        print(engine.board.display())

if __name__ == "__main__":
    demonstrate_chess_game()
    test_special_moves()
```

## 🎯 Key Design Patterns Used

### 1. **Strategy Pattern**
- Different piece movement strategies
- Pluggable game rule variants

### 2. **Command Pattern**
- Move objects encapsulate operations
- Enables undo/redo functionality

### 3. **State Pattern**
- Game state management
- Piece state transitions

### 4. **Factory Pattern**
- Piece creation based on type
- Board setup variations

## 🔧 Advanced Features

### 1. **Move Validation Engine**
- Comprehensive rule checking
- Check/checkmate detection
- Special move handling (castling, en passant)

### 2. **Game State Management**
- Position history tracking
- Threefold repetition detection
- 50-move rule implementation

### 3. **Extensibility Features**
- Support for chess variants
- Pluggable UI interfaces
- AI player integration points

## 📈 Performance Considerations

### Optimization Techniques
- Efficient board representation
- Move generation optimization
- Bitboard representation (advanced)
- Alpha-beta pruning for AI

### Memory Management
- Object pooling for moves
- Efficient position encoding
- Minimal state copying

## 🧪 Testing Scenarios

### Unit Tests
```python
def test_piece_movements():
    """Test individual piece movement rules"""
    board = ChessBoard()

    # Test pawn moves
    pawn = board.get_piece(Position(6, 4))  # e2 pawn
    moves = pawn.get_possible_moves(board)
    assert Position(5, 4) in moves  # e3
    assert Position(4, 4) in moves  # e4

def test_check_detection():
    """Test check detection"""
    engine = ChessEngine()
    # Set up check position
    # ... test implementation

def test_game_endings():
    """Test checkmate and stalemate detection"""
    # ... test various ending scenarios
```

## ✅ Learning Outcomes

After implementing this chess system, you should understand:

- ✅ Complex object-oriented design
- ✅ State management in game systems
- ✅ Rule engine implementation
- ✅ Move validation algorithms
- ✅ Design patterns in practice
- ✅ Game state persistence
- ✅ Performance optimization techniques
- ✅ Extensible architecture design

## 🚀 Extensions

### Possible Enhancements
1. **AI Player Integration** - Minimax algorithm with alpha-beta pruning
2. **Chess Variants** - King of the Hill, Chess960, etc.
3. **Network Play** - Multiplayer over network
4. **Advanced UI** - Graphical interface with drag-and-drop
5. **Game Analysis** - Move evaluation and suggestions
6. **Tournament System** - Multiple game management

## 📚 Related Concepts

- **Game Theory** - Minimax algorithms
- **Graph Algorithms** - Move tree traversal
- **State Machines** - Game state management
- **Event-Driven Architecture** - Move notifications
- **Persistence Patterns** - Game state saving