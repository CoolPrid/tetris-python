"""
Database models for storing game data.
Uses SQLAlchemy ORM for database operations.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from flask_sqlalchemy import SQLAlchemy

# This would typically be imported from app.py, but we'll define it here for clarity
# In practice, you'd import: from app import db
db = SQLAlchemy()


class Player(db.Model):
    """Player model for storing user information."""
    
    __tablename__ = 'player'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    scores = db.relationship('Score', backref='player', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, username: str) -> None:
        """
        Initialize a new player.
        
        Args:
            username: Unique username for the player
        """
        self.username = username
        self.created_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f'<Player {self.username}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert player to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the player
        """
        return {
            'id': self.id,
            'username': self.username,
            'created_at': self.created_at.isoformat(),
            'total_scores': len(self.scores)
        }
    
    def get_best_score(self) -> int:
        """
        Get the player's highest score.
        
        Returns:
            Highest score value, or 0 if no scores exist
        """
        if not self.scores:
            return 0
        return max(score.score for score in self.scores)
    
    def get_total_games(self) -> int:
        """
        Get the total number of games played by the player.
        
        Returns:
            Number of games (scores) recorded
        """
        return len(self.scores)
    
    def get_average_score(self) -> float:
        """
        Get the player's average score.
        
        Returns:
            Average score, or 0.0 if no scores exist
        """
        if not self.scores:
            return 0.0
        return sum(score.score for score in self.scores) / len(self.scores)
    
    @classmethod
    def get_or_create(cls, username: str) -> 'Player':
        """
        Get an existing player or create a new one.
        
        Args:
            username: Player's username
            
        Returns:
            Player instance (existing or newly created)
        """
        player = cls.query.filter_by(username=username).first()
        if not player:
            player = cls(username=username)
            db.session.add(player)
            db.session.commit()
        return player


class Score(db.Model):
    """Score model for storing game results."""
    
    __tablename__ = 'score'
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False, index=True)
    score = db.Column(db.Integer, nullable=False, index=True)
    lines_cleared = db.Column(db.Integer, default=0, nullable=False)
    level = db.Column(db.Integer, default=1, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __init__(self, player_id: int, score: int, lines_cleared: int = 0, level: int = 1) -> None:
        """
        Initialize a new score record.
        
        Args:
            player_id: ID of the player who achieved this score
            score: The score value
            lines_cleared: Number of lines cleared in the game
            level: Level reached in the game
        """
        self.player_id = player_id
        self.score = score
        self.lines_cleared = lines_cleared
        self.level = level
        self.timestamp = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f'<Score {self.score} by Player {self.player_id}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert score to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the score
        """
        return {
            'id': self.id,
            'player_id': self.player_id,
            'username': self.player.username if self.player else 'Unknown',
            'score': self.score,
            'lines_cleared': self.lines_cleared,
            'level': self.level,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def get_top_scores(cls, limit: int = 10) -> List['Score']:
        """
        Get the top scores from the database.
        
        Args:
            limit: Maximum number of scores to return
            
        Returns:
            List of Score objects ordered by score descending
        """
        return cls.query.order_by(cls.score.desc()).limit(limit).all()
    
    @classmethod
    def get_recent_scores(cls, limit: int = 10) -> List['Score']:
        """
        Get the most recent scores from the database.
        
        Args:
            limit: Maximum number of scores to return
            
        Returns:
            List of Score objects ordered by timestamp descending
        """
        return cls.query.order_by(cls.timestamp.desc()).limit(limit).all()
    
    @classmethod
    def get_player_scores(cls, player_id: int) -> List['Score']:
        """
        Get all scores for a specific player.
        
        Args:
            player_id: ID of the player
            
        Returns:
            List of Score objects for the player, ordered by score descending
        """
        return cls.query.filter_by(player_id=player_id).order_by(cls.score.desc()).all()
    
    @classmethod
    def get_stats(cls) -> Dict[str, Any]:
        """
        Get overall game statistics.
        
        Returns:
            Dictionary with various game statistics
        """
        total_games = cls.query.count()
        if total_games == 0:
            return {
                'total_games': 0,
                'highest_score': 0,
                'average_score': 0.0,
                'total_lines_cleared': 0,
                'highest_level': 1
            }
        
        scores = cls.query.all()
        return {
            'total_games': total_games,
            'highest_score': max(score.score for score in scores),
            'average_score': sum(score.score for score in scores) / total_games,
            'total_lines_cleared': sum(score.lines_cleared for score in scores),
            'highest_level': max(score.level for score in scores)
        }


def init_db(app) -> None:
    """
    Initialize the database with the Flask app.
    
    Args:
        app: Flask application instance
    """
    db.init_app(app)
    with app.app_context():
        db.create_all()


def get_leaderboard(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get leaderboard data with player information.
    
    Args:
        limit: Maximum number of entries to return
        
    Returns:
        List of dictionaries containing leaderboard data
    """
    top_scores = Score.get_top_scores(limit)
    return [score.to_dict() for score in top_scores]


def save_game_result(username: str, score: int, lines_cleared: int = 0, level: int = 1) -> bool:
    """
    Save a game result to the database.
    
    Args:
        username: Player's username
        score: Final score
        lines_cleared: Total lines cleared
        level: Final level reached
        
    Returns:
        True if successful, False otherwise
    """
    try:
        player = Player.get_or_create(username)
        new_score = Score(
            player_id=player.id,
            score=score,
            lines_cleared=lines_cleared,
            level=level
        )
        db.session.add(new_score)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error saving game result: {e}")
        return False