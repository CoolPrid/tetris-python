"""
Main Flask application for Tetris game.
Handles web routes and API endpoints.
"""

from flask import Flask, render_template, request, jsonify, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import os

app = Flask(__name__)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "tetris.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'

db = SQLAlchemy(app)


# Database models (moved here to fix import issues)
class Player(db.Model):
    """Player model for storing user information."""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    scores = db.relationship('Score', backref='player', lazy=True)
    
    def __repr__(self) -> str:
        return f'<Player {self.username}>'


class Score(db.Model):
    """Score model for storing game results."""
    
    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    lines_cleared = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<Score {self.score} by Player {self.player_id}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert score to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'username': self.player.username,
            'score': self.score,
            'lines_cleared': self.lines_cleared,
            'level': self.level,
            'timestamp': self.timestamp.isoformat()
        }


@app.route('/')
def index() -> str:
    """Render the main game page."""
    return render_template('game.html')


@app.route('/leaderboard')
def leaderboard() -> str:
    """Display the top 10 scores."""
    top_scores: List[Score] = Score.query.order_by(Score.score.desc()).limit(10).all()
    return render_template('leaderboard.html', scores=top_scores)


@app.route('/api/score', methods=['POST'])
def save_score() -> Tuple[Response, int]:
    """
    Save a new score to the database.
    
    Returns:
        JSON response with success status and message
    """
    try:
        data: Optional[Dict[str, Any]] = request.json
        
        if not data or 'username' not in data or 'score' not in data:
            return jsonify({'success': False, 'message': 'Missing required data'}), 400
        
        username: str = data['username']
        score: int = data['score']
        lines: int = data.get('lines', 0)
        level: int = data.get('level', 1)
        
        # Validate input data
        if not isinstance(username, str) or not username.strip():
            return jsonify({'success': False, 'message': 'Invalid username'}), 400
        
        if not isinstance(score, int) or score < 0:
            return jsonify({'success': False, 'message': 'Invalid score'}), 400
        
        if not isinstance(lines, int) or lines < 0:
            return jsonify({'success': False, 'message': 'Invalid lines count'}), 400
        
        if not isinstance(level, int) or level < 1:
            return jsonify({'success': False, 'message': 'Invalid level'}), 400
        
        # Get or create player
        player: Optional[Player] = Player.query.filter_by(username=username.strip()).first()
        if not player:
            player = Player(username=username.strip())
            db.session.add(player)
            db.session.commit()
        
        # Save score
        new_score = Score(
            player_id=player.id,
            score=score,
            lines_cleared=lines,
            level=level
        )
        db.session.add(new_score)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Score saved successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/top-scores')
def get_top_scores() -> Tuple[Response, int]:
    """
    Get top 10 scores as JSON.
    
    Returns:
        JSON array of top scores with player information
    """
    try:
        top_scores: List[Score] = Score.query.order_by(Score.score.desc()).limit(10).all()
        scores_data: List[Dict[str, Any]] = [score.to_dict() for score in top_scores]
        
        return jsonify(scores_data), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/player/<string:username>/stats')
def get_player_stats(username: str) -> Tuple[Response, int]:
    """
    Get statistics for a specific player.
    
    Args:
        username: Player's username
        
    Returns:
        JSON object with player statistics
    """
    try:
        player: Optional[Player] = Player.query.filter_by(username=username).first()
        
        if not player:
            return jsonify({'error': 'Player not found'}), 404
        
        scores: List[Score] = Score.query.filter_by(player_id=player.id).all()
        
        if not scores:
            stats = {
                'username': player.username,
                'games_played': 0,
                'best_score': 0,
                'total_lines': 0,
                'max_level': 1,
                'average_score': 0
            }
        else:
            stats = {
                'username': player.username,
                'games_played': len(scores),
                'best_score': max(score.score for score in scores),
                'total_lines': sum(score.lines_cleared for score in scores),
                'max_level': max(score.level for score in scores),
                'average_score': sum(score.score for score in scores) // len(scores)
            }
        
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error: Any) -> Tuple[str, int]:
    """Handle 404 errors."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error: Any) -> Tuple[str, int]:
    """Handle 500 errors."""
    db.session.rollback()
    return render_template('500.html'), 500


def create_app() -> Flask:
    """
    Application factory function.
    
    Returns:
        Configured Flask application instance
    """
    with app.app_context():
        db.create_all()
    
    return app


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)