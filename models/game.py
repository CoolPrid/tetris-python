"""
Game logic for Tetris.
Implements the main game board and rules.
"""

from typing import List, Optional, Tuple
from models.tetromino import Tetromino, create_random_piece


class TetrisBoard:
    """Main game board for Tetris."""
    
    def __init__(self, width: int = 10, height: int = 20):
        """
        Initialize the game board.
        
        Args:
            width: Board width in blocks
            height: Board height in blocks
        """
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.current_piece = None
        self.next_piece = create_random_piece()
        self.score = 0
        self.lines_cleared = 0
        self.level = 1
        self.game_over = False
    
    def spawn_piece(self) -> bool:
        """
        Spawn a new piece at the top of the board.
        
        Returns:
            False if game over, True otherwise
        """
        self.current_piece = self.next_piece
        self.next_piece = create_random_piece()
        
        # Check if spawn position is blocked
        if not self.is_valid_position(self.current_piece):
            self.game_over = True
            return False
        return True
    
    def is_valid_position(self, piece: Tetromino, dx: int = 0, dy: int = 0) -> bool:
        """
        Check if a piece position is valid.
        
        Args:
            piece: Tetromino to check
            dx: X offset
            dy: Y offset
        
        Returns:
            True if position is valid
        """
        for y, row in enumerate(piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    new_x = piece.x + x + dx
                    new_y = piece.y + y + dy
                    
                    # Check boundaries
                    if new_x < 0 or new_x >= self.width:
                        return False
                    if new_y >= self.height:
                        return False
                    
                    # Check collision with placed pieces
                    if new_y >= 0 and self.grid[new_y][new_x] is not None:
                        return False
        return True
    
    def move_piece(self, dx: int, dy: int) -> bool:
        """
        Move the current piece.
        
        Args:
            dx: X direction (-1 left, 1 right)
            dy: Y direction (1 down)
        
        Returns:
            True if move was successful
        """
        if not self.current_piece:
            return False
        
        if self.is_valid_position(self.current_piece, dx, dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False
    
    def rotate_piece(self) -> bool:
        """
        Rotate the current piece clockwise.
        
        Returns:
            True if rotation was successful
        """
        if not self.current_piece:
            return False
        
        # Save original state
        original_shape = [row[:] for row in self.current_piece.shape]
        original_rotation = self.current_piece.rotation
        
        # Try rotation
        self.current_piece.rotate()
        
        # Check if valid
        if self.is_valid_position(self.current_piece):
            return True
        
        # Try wall kicks
        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1)]
        for dx, dy in kicks:
            if self.is_valid_position(self.current_piece, dx, dy):
                self.current_piece.x += dx
                self.current_piece.y += dy
                return True
        
        # Revert rotation
        self.current_piece.shape = original_shape
        self.current_piece.rotation = original_rotation
        return False
    
    def drop_piece(self) -> int:
        """
        Drop the current piece instantly.
        
        Returns:
            Number of rows dropped
        """
        if not self.current_piece:
            return 0
        
        rows_dropped = 0
        while self.move_piece(0, 1):
            rows_dropped += 1
        
        return rows_dropped
    
    def lock_piece(self) -> None:
        """Lock the current piece in place."""
        if not self.current_piece:
            return
        
        for y, row in enumerate(self.current_piece.shape):
            for x, cell in enumerate(row):
                if cell:
                    board_x = self.current_piece.x + x
                    board_y = self.current_piece.y + y
                    if board_y >= 0:
                        self.grid[board_y][board_x] = self.current_piece.color
        
        self.current_piece = None
        self.clear_lines()
    
    def clear_lines(self) -> int:
        """
        Clear completed lines.
        
        Returns:
            Number of lines cleared
        """
        lines_to_clear = []
        
        for y in range(self.height):
            if all(self.grid[y][x] is not None for x in range(self.width)):
                lines_to_clear.append(y)
        
        for y in lines_to_clear:
            del self.grid[y]
            self.grid.insert(0, [None for _ in range(self.width)])
        
        # Update score
        lines_count = len(lines_to_clear)
        if lines_count > 0:
            self.lines_cleared += lines_count
            scores = [40, 100, 300, 1200]  # 1, 2, 3, 4 lines
            self.score += scores[min(lines_count - 1, 3)] * self.level
            
            # Level up every 10 lines
            self.level = 1 + self.lines_cleared // 10
        
        return lines_count
    
    def get_board_state(self) -> dict:
        """
        Get the current board state for rendering.
        
        Returns:
            Dictionary with board state
        """
        state = {
            'grid': self.grid,
            'current_piece': None,
            'next_piece': None,
            'score': self.score,
            'lines': self.lines_cleared,
            'level': self.level,
            'game_over': self.game_over
        }
        
        if self.current_piece:
            state['current_piece'] = {
                'blocks': self.current_piece.get_blocks(),
                'color': self.current_piece.color
            }
        
        if self.next_piece:
            state['next_piece'] = {
                'shape': self.next_piece.shape,
                'color': self.next_piece.color
            }
        
        return state