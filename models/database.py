"""
Database models for storing game data.
Uses SQLAlchemy ORM for database operations.
"""

from datetime import datetime
from app import db


class Player(db.Model):
    """Player model for storing user information."""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='player', lazy=True)
    
    def __repr__(self):
        return f'<Player {self.username}>'


class Score(db.Model):
    """Score model for storing game results."""
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    lines_cleared = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Score {self.score} by Player {self.player_id}>'