"""
Tetromino classes for Tetris game pieces.
Implements all seven standard Tetris pieces using OOP.
"""

from enum import Enum
from typing import List, Tuple


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
    
    def __init__(self, x: int = 0, y: int = 0):
        """
        Initialize a tetromino piece.
        
        Args:
            x: Initial x position
            y: Initial y position
        """
        self.x = x
        self.y = y
        self.rotation = 0
        self.shape = self.get_shape()
        self.color = self.get_color()
    
    def get_shape(self) -> List[List[int]]:
        """Get the shape matrix for the piece."""
        raise NotImplementedError
    
    def get_color(self) -> str:
        """Get the color of the piece."""
        raise NotImplementedError
    
    def rotate(self, clockwise: bool = True) -> None:
        """
        Rotate the piece 90 degrees.
        
        Args:
            clockwise: Direction of rotation
        """
        if clockwise:
            self.shape = [list(row) for row in zip(*self.shape[::-1])]
        else:
            self.shape = [list(row) for row in zip(*self.shape)][::-1]
        
        self.rotation = (self.rotation + (1 if clockwise else -1)) % 4
    
    def get_blocks(self) -> List[Tuple[int, int]]:
        """
        Get the positions of all blocks in the piece.
        
        Returns:
            List of (x, y) tuples for each block
        """
        blocks = []
        for row_idx, row in enumerate(self.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    blocks.append((self.x + col_idx, self.y + row_idx))
        return blocks


class I_Piece(Tetromino):
    """I-shaped tetromino (straight piece)."""
    
    def get_shape(self):
        return [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]
    
    def get_color(self):
        return '#00F0F0'  # Cyan


class O_Piece(Tetromino):
    """O-shaped tetromino (square piece)."""
    
    def get_shape(self):
        return [
            [1, 1],
            [1, 1]
        ]
    
    def get_color(self):
        return '#F0F000'  # Yellow
    
    def rotate(self, clockwise=True):
        """O piece doesn't rotate."""
        pass


class T_Piece(Tetromino):
    """T-shaped tetromino."""
    
    def get_shape(self):
        return [
            [0, 1, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
    
    def get_color(self):
        return '#A000F0'  # Purple


class S_Piece(Tetromino):
    """S-shaped tetromino."""
    
    def get_shape(self):
        return [
            [0, 1, 1],
            [1, 1, 0],
            [0, 0, 0]
        ]
    
    def get_color(self):
        return '#00F000'  # Green


class Z_Piece(Tetromino):
    """Z-shaped tetromino."""
    
    def get_shape(self):
        return [
            [1, 1, 0],
            [0, 1, 1],
            [0, 0, 0]
        ]
    
    def get_color(self):
        return '#F00000'  # Red


class J_Piece(Tetromino):
    """J-shaped tetromino."""
    
    def get_shape(self):
        return [
            [1, 0, 0],
            [1, 1, 1],
            [0, 0, 0]
        ]
    
    def get_color(self):
        return '#0000F0'  # Blue


class L_Piece(Tetromino):
    """L-shaped tetromino."""
    
    def get_shape(self):
        return [
            [0, 0, 1],
            [1, 1, 1],
            [0, 0, 0]
        ]
    
    def get_color(self):
        return '#F0A000'  # Orange


def create_random_piece(x: int = 4, y: int = 0) -> Tetromino:
    """
    Create a random tetromino piece.
    
    Args:
        x: Initial x position
        y: Initial y position
    
    Returns:
        Random Tetromino instance
    """
    import random
    pieces = [I_Piece, O_Piece, T_Piece, S_Piece, Z_Piece, J_Piece, L_Piece]
    return random.choice(pieces)(x, y)