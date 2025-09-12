"""
Main Flask application for Tetris game.
Handles web routes and API endpoints.
"""

from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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


@app.route('/')
def index():
    """Render the main game page."""
    return render_template('game.html')


@app.route('/leaderboard')
def leaderboard():
    """Display the top 10 scores."""
    top_scores = Score.query.order_by(Score.score.desc()).limit(10).all()
    return render_template('leaderboard.html', scores=top_scores)


@app.route('/api/score', methods=['POST'])
def save_score():
    """Save a new score to the database."""
    try:
        data = request.json
        
        if not data or 'username' not in data or 'score' not in data:
            return jsonify({'success': False, 'message': 'Missing required data'}), 400
        
        # Get or create player
        player = Player.query.filter_by(username=data['username']).first()
        if not player:
            player = Player(username=data['username'])
            db.session.add(player)
            db.session.commit()
        
        # Save score
        new_score = Score(
            player_id=player.id,
            score=data['score'],
            lines_cleared=data.get('lines', 0),
            level=data.get('level', 1)
        )
        db.session.add(new_score)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Score saved successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/top-scores')
def get_top_scores():
    """Get top 10 scores as JSON."""
    try:
        top_scores = Score.query.order_by(Score.score.desc()).limit(10).all()
        scores_data = [{
            'username': score.player.username,
            'score': score.score,
            'lines_cleared': score.lines_cleared,
            'level': score.level,
            'timestamp': score.timestamp.isoformat()
        } for score in top_scores]
        
        return jsonify(scores_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)