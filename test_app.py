"""
Unit tests for the Tetris game application.
Run with: python -m pytest tests/
"""

import unittest
import json
import os
import tempfile
from app import app, db, Player, Score


class TetrisTestCase(unittest.TestCase):
    """Test case for Tetris game functionality."""
    
    def setUp(self):
        """Set up test database and client."""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after tests."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
    
    def test_index_page(self):
        """Test that the main game page loads."""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'tetris-canvas', response.data)
    
    def test_leaderboard_page(self):
        """Test that the leaderboard page loads."""
        response = self.app.get('/leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Leaderboard', response.data)
    
    def test_save_score_success(self):
        """Test successful score saving."""
        score_data = {
            'username': 'TestPlayer',
            'score': 1000,
            'lines': 10,
            'level': 2
        }
        
        response = self.app.post('/api/score',
                               data=json.dumps(score_data),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify score was saved to database
        with app.app_context():
            player = Player.query.filter_by(username='TestPlayer').first()
            self.assertIsNotNone(player)
            self.assertEqual(len(player.scores), 1)
            self.assertEqual(player.scores[0].score, 1000)
    
    def test_save_score_invalid_data(self):
        """Test score saving with invalid data."""
        response = self.app.post('/api/score',
                               data=json.dumps({}),
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
    
    def test_get_top_scores(self):
        """Test retrieving top scores."""
        # Add some test scores
        with app.app_context():
            player1 = Player(username='Player1')
            player2 = Player(username='Player2')
            db.session.add_all([player1, player2])
            db.session.commit()
            
            score1 = Score(player_id=player1.id, score=2000, lines_cleared=20, level=3)
            score2 = Score(player_id=player2.id, score=1500, lines_cleared=15, level=2)
            db.session.add_all([score1, score2])
            db.session.commit()
        
        response = self.app.get('/api/top-scores')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['score'], 2000)  # Should be sorted by score desc
        self.assertEqual(data[1]['score'], 1500)
    
    def test_player_creation(self):
        """Test player model creation."""
        with app.app_context():
            player = Player(username='TestUser')
            db.session.add(player)
            db.session.commit()
            
            retrieved_player = Player.query.filter_by(username='TestUser').first()
            self.assertIsNotNone(retrieved_player)
            self.assertEqual(retrieved_player.username, 'TestUser')
    
    def test_score_creation(self):
        """Test score model creation."""
        with app.app_context():
            player = Player(username='ScoreTest')
            db.session.add(player)
            db.session.commit()
            
            score = Score(
                player_id=player.id,
                score=5000,
                lines_cleared=50,
                level=5
            )
            db.session.add(score)
            db.session.commit()
            
            retrieved_score = Score.query.filter_by(player_id=player.id).first()
            self.assertIsNotNone(retrieved_score)
            self.assertEqual(retrieved_score.score, 5000)
            self.assertEqual(retrieved_score.lines_cleared, 50)


if __name__ == '__main__':
    unittest.main()