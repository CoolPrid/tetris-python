"""
Tetromino classes for Tetris game pieces.
Implements all seven standard Tetris pieces using OOP.
"""

from enum import Enum
from typing import List, Tuple, Type, Union
import random


class TetrominoType(Enum):
    """Enumeration of Tetris piece types."""
    I = 'I'
    O = 'O'
    T = 'T'
    S = 'S'
    Z = 'Z'
    J = 'J'
    L = 'L'


class Tetromino:
    """Base class for all Tetris pieces."""
    
    def __init__(self, x: int = 0, y: int = 0) -> None:
        """
        Initialize a tetromino piece.
        
        Args:
            x: Initial x position
            y: Initial y position
        """
        self.x: int = x
        self.y: int = y
        self.rotation: int = 0
        self.shape: List[List[int]] = self.get_shape()
        self.color: str = self.get_color()
    
    def get_shape(self) -> List[List[int]]:
        """
        Get the shape matrix for the piece.
        
        Returns:
            2D list representing the piece shape (1 for filled, 0 for empty)
        """
        raise NotImplementedError("Subclasses must implement get_shape method")
    
    def get_color(self) -> str:
        """
        Get the color of the piece.
        
        Returns:
            Hex color string for the piece
        """
        raise NotImplementedError("Subclasses must implement get_color method")
    
    def rotate(self, clockwise: bool = True) -> None:
        """
        Rotate the piece 90 degrees.
        
        Args:
            clockwise: Direction of rotation (True for clockwise, False for counter-clockwise)
        """
        if clockwise:
            # Rotate clockwise: transpose then reverse each row
            self.shape = [list(row) for row in zip(*self.shape[::-1])]
        else:
            # Rotate counter-clockwise: reverse each row then transpose
            self.shape = [list(row) for row in zip(*self.shape)][::-1]
        
        self.rotation = (self.rotation + (1 if clockwise else -1)) % 4
    
    def get_blocks(self) -> List[Tuple[int, int]]:
        """
        Get the positions of all blocks in the piece.
        
        Returns:
            List of (x, y) tuples for each filled block in the piece
        """
        blocks: List[Tuple[int, int]] = []
        for row_idx, row in enumerate(self.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    blocks.append((self.x + col_idx, self.y + row_idx))
        return blocks
    
    def get_width(self) -> int:
        """
        Get the width of the piece's bounding box.
        
        Returns:
            Width in blocks
        """
        return len(self.shape[0]) if self.shape else 0
    
    def get_height(self) -> int:
        """
        Get the height of the piece's bounding box.
        
        Returns:
            Height in blocks
        """
        return len(self.shape)
    
    def copy(self) -> 'Tetromino':
        """
        Create a deep copy of the piece.
        
        Returns:
            New Tetromino instance with the same properties
        """
        new_piece = self.__class__(self.x, self.y)
        new_piece.rotation = self.rotation
        new_piece.shape = [row[:] for row in self.shape]  # Deep copy of shape
        return new_piece
    
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__} at ({self.x}, {self.y}) rotation={self.rotation}>'


class I_Piece(Tetromino):
    """I-shaped tetromino (straight piece)."""
    
    def get_shape(self) -> List[List[int]]:
        return [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
    
    def get_color(self) -> str:
        return '#00F0F0'  # Cyan


class O_Piece(Tetromino):
    """O-shaped tetromino (square piece)."""
    
    def get_shape(self) -> List[List[int]]:
        return [
            [1, 1],
            [1, 1]
        ]
    
    def get_color(self) -> str:
        return '#F0F000'  # Yellow
    
    def rotate(self, clockwise: bool = True) -> None:
        """O piece doesn't rotate - override to prevent rotation."""
        pass


class T_Piece(Tetromino):
    """T-shaped tetromino."""
    
    def get_shape(self) -> List[List[int]]:
        return [
            [0, 1, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
    
    def get_color(self) -> str:
        return '#A000F0'  # Purple


class S_Piece(Tetromino):
    """S-shaped tetromino."""
    
    def get_shape(self) -> List[List[int]]:
        return [
            [0, 1, 1],
            [1, 1, 0],
            [0, 0, 0]
        ]
    
    def get_color(self) -> str:
        return '#00F000'  # Green


class Z_Piece(Tetromino):
    """Z-shaped tetromino."""
    
    def get_shape(self) -> List[List[int]]:
        return [
            [1, 1, 0],
            [0, 1, 1],
            [0, 0, 0]
        ]
    
    def get_color(self) -> str:
        return '#F00000'  # Red


class J_Piece(Tetromino):
    """J-shaped tetromino."""
    
    def get_shape(self) -> List[List[int]]:
        return [
            [1, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
    
    def get_color(self) -> str:
        return '#0000F0'  # Blue


class L_Piece(Tetromino):
    """L-shaped tetromino."""
    
    def get_shape(self) -> List[List[int]]:
        return [
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 0]
        ]
    
    def get_color(self) -> str:
        return '#F0A000'  # Orange


# Type alias for piece classes
PieceClass = Type[Tetromino]

# All available piece classes
PIECE_CLASSES: List[PieceClass] = [
    I_Piece, O_Piece, T_Piece, S_Piece, Z_Piece, J_Piece, L_Piece
]


def create_random_piece(x: int = 4, y: int = 0) -> Tetromino:
    """
    Create a random tetromino piece.
    
    Args:
        x: Initial x position (default: 4, center of a 10-wide board)
        y: Initial y position (default: 0, top of board)
    
    Returns:
        Random Tetromino instance of one of the seven piece types
    """
    piece_class: PieceClass = random.choice(PIECE_CLASSES)
    return piece_class(x, y)


def create_piece_by_type(piece_type: Union[TetrominoType, str], x: int = 4, y: int = 0) -> Tetromino:
    """
    Create a specific tetromino piece by type.
    
    Args:
        piece_type: Type of piece to create (TetrominoType enum or string)
        x: Initial x position
        y: Initial y position
    
    Returns:
        Tetromino instance of the specified type
        
    Raises:
        ValueError: If piece_type is not valid
    """
    if isinstance(piece_type, str):
        try:
            piece_type = TetrominoType(piece_type.upper())
        except ValueError:
            raise ValueError(f"Invalid piece type: {piece_type}")
    
    piece_map = {
        TetrominoType.I: I_Piece,
        TetrominoType.O: O_Piece,
        TetrominoType.T: T_Piece,
        TetrominoType.S: S_Piece,
        TetrominoType.Z: Z_Piece,
        TetrominoType.J: J_Piece,
        TetrominoType.L: L_Piece,
    }
    
    piece_class = piece_map.get(piece_type)
    if not piece_class:
        raise ValueError(f"Unknown piece type: {piece_type}")
    
    return piece_class(x, y)


def get_all_piece_types() -> List[TetrominoType]:
    """
    Get all available piece types.
    
    Returns:
        List of all TetrominoType enum values
    """
    return list(TetrominoType)