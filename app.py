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

# Import models after db initialization
from models.database import Score, Player


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
    data = request.json
    
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


@app.route('/api/top-scores')
def get_top_scores():
    """Get top 10 scores as JSON."""
    top_scores = Score.query.order_by(Score.score.desc()).limit(10).all()
    scores_data = [{
        'username': score.player.username,
        'score': score.score,
        'lines_cleared': score.lines_cleared,
        'level': score.level,
        'timestamp': score.timestamp.isoformat()
    } for score in top_scores]
    
    return jsonify(scores_data)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)