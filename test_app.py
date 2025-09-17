"""
Unit tests for the Tetris game application.
Run with: python -m pytest test_app.py -v
"""

import unittest
import json
import os
import tempfile
from typing import Dict, Any, List, Optional, Union
from flask.testing import FlaskClient
from flask import Flask, Response

from app import app, db, Player, Score


class TetrisTestCase(unittest.TestCase):
    """Test case for Tetris game functionality."""
    
    def setUp(self) -> None:
        """Set up test database and client."""
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        self.app: FlaskClient = app.test_client()
        
        with app.app_context():
            db.create_all()
    
    def tearDown(self) -> None:
        """Clean up after tests."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
        os.close(self.db_fd)
    
    def test_index_page(self) -> None:
        """Test that the main game page loads."""
        response: Response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'tetris-canvas', response.data)
        self.assertIn(b'Tetris Game', response.data)
    
    def test_leaderboard_page(self) -> None:
        """Test that the leaderboard page loads."""
        response: Response = self.app.get('/leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Leaderboard', response.data)
        self.assertIn(b'Top 10', response.data)
    
    def test_save_score_success(self) -> None:
        """Test successful score saving."""
        score_data: Dict[str, Union[str, int]] = {
            'username': 'TestPlayer',
            'score': 1000,
            'lines': 10,
            'level': 2
        }
        
        response: Response = self.app.post('/api/score',
                                         data=json.dumps(score_data),
                                         content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        data: Dict[str, Any] = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['message'], 'Score saved successfully')
        
        # Verify score was saved to database
        with app.app_context():
            player: Optional[Player] = Player.query.filter_by(username='TestPlayer').first()
            self.assertIsNotNone(player)
            self.assertEqual(len(player.scores), 1)
            self.assertEqual(player.scores[0].score, 1000)
            self.assertEqual(player.scores[0].lines_cleared, 10)
            self.assertEqual(player.scores[0].level, 2)
    
    def test_save_score_invalid_data(self) -> None:
        """Test score saving with invalid data."""
        response: Response = self.app.post('/api/score',
                                         data=json.dumps({}),
                                         content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data: Dict[str, Any] = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Missing required data', data['message'])
    
    def test_save_score_invalid_username(self) -> None:
        """Test score saving with invalid username."""
        score_data: Dict[str, Union[str, int]] = {
            'username': '',
            'score': 1000,
            'lines': 10,
            'level': 2
        }
        
        response: Response = self.app.post('/api/score',
                                         data=json.dumps(score_data),
                                         content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data: Dict[str, Any] = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Invalid username', data['message'])
    
    def test_save_score_negative_score(self) -> None:
        """Test score saving with negative score."""
        score_data: Dict[str, Union[str, int]] = {
            'username': 'TestPlayer',
            'score': -100,
            'lines': 10,
            'level': 2
        }
        
        response: Response = self.app.post('/api/score',
                                         data=json.dumps(score_data),
                                         content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        data: Dict[str, Any] = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('Invalid score', data['message'])
    
    def test_get_top_scores(self) -> None:
        """Test retrieving top scores."""
        # Add some test scores
        with app.app_context():
            player1 = Player(username='Player1')
            player2 = Player(username='Player2')
            db.session.add_all([player1, player2])
            db.session.commit()
            
            score1 = Score(player_id=player1.id, score=2000, lines_cleared=20, level=3)
            score2 = Score(player_id=player2.id, score=1500, lines_cleared=15, level=2)
            score3 = Score(player_id=player1.id, score=1800, lines_cleared=18, level=2)
            db.session.add_all([score1, score2, score3])
            db.session.commit()
        
        response: Response = self.app.get('/api/top-scores')
        self.assertEqual(response.status_code, 200)
        
        data: List[Dict[str, Any]] = json.loads(response.data)
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0]['score'], 2000)  # Should be sorted by score desc
        self.assertEqual(data[1]['score'], 1800)
        self.assertEqual(data[2]['score'], 1500)
        self.assertEqual(data[0]['username'], 'Player1')
    
    def test_get_player_stats(self) -> None:
        """Test retrieving player statistics."""
        # Add test data
        with app.app_context():
            player = Player(username='StatPlayer')
            db.session.add(player)
            db.session.commit()
            
            scores = [
                Score(player_id=player.id, score=1000, lines_cleared=10, level=2),
                Score(player_id=player.id, score=2000, lines_cleared=20, level=3),
                Score(player_id=player.id, score=1500, lines_cleared=15, level=2)
            ]
            db.session.add_all(scores)
            db.session.commit()
        
        response: Response = self.app.get('/api/player/StatPlayer/stats')
        self.assertEqual(response.status_code, 200)
        
        data: Dict[str, Any] = json.loads(response.data)
        self.assertEqual(data['username'], 'StatPlayer')
        self.assertEqual(data['games_played'], 3)
        self.assertEqual(data['best_score'], 2000)
        self.assertEqual(data['total_lines'], 45)
        self.assertEqual(data['max_level'], 3)
        self.assertEqual(data['average_score'], 1500)  # (1000 + 2000 + 1500) // 3
    
    def test_get_player_stats_not_found(self) -> None:
        """Test retrieving stats for non-existent player."""
        response: Response = self.app.get('/api/player/NonexistentPlayer/stats')
        self.assertEqual(response.status_code, 404)
        
        data: Dict[str, str] = json.loads(response.data)
        self.assertIn('Player not found', data['error'])
    
    def test_player_creation(self) -> None:
        """Test player model creation."""
        with app.app_context():
            player = Player(username='TestUser')
            db.session.add(player)
            db.session.commit()
            
            retrieved_player: Optional[Player] = Player.query.filter_by(username='TestUser').first()
            self.assertIsNotNone(retrieved_player)
            self.assertEqual(retrieved_player.username, 'TestUser')
            self.assertIsNotNone(retrieved_player.created_at)
    
    def test_score_creation(self) -> None:
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
            
            retrieved_score: Optional[Score] = Score.query.filter_by(player_id=player.id).first()
            self.assertIsNotNone(retrieved_score)
            self.assertEqual(retrieved_score.score, 5000)
            self.assertEqual(retrieved_score.lines_cleared, 50)
            self.assertEqual(retrieved_score.level, 5)
            self.assertIsNotNone(retrieved_score.timestamp)
    
    def test_player_methods(self) -> None:
        """Test player model methods."""
        with app.app_context():
            player = Player(username='MethodTest')
            db.session.add(player)
            db.session.commit()
            
            # Test with no scores
            self.assertEqual(player.get_best_score(), 0)
            self.assertEqual(player.get_total_games(), 0)
            self.assertEqual(player.get_average_score(), 0.0)
            
            # Add some scores
            scores = [
                Score(player_id=player.id, score=1000, lines_cleared=10, level=2),
                Score(player_id=player.id, score=2000, lines_cleared=20, level=3),
                Score(player_id=player.id, score=1500, lines_cleared=15, level=2)
            ]
            db.session.add_all(scores)
            db.session.commit()
            
            self.assertEqual(player.get_best_score(), 2000)
            self.assertEqual(player.get_total_games(), 3)
            self.assertEqual(player.get_average_score(), 1500.0)
    
    def test_score_to_dict(self) -> None:
        """Test score to_dict method."""
        with app.app_context():
            player = Player(username='DictTest')
            db.session.add(player)
            db.session.commit()
            
            score = Score(player_id=player.id, score=3000, lines_cleared=30, level=4)
            db.session.add(score)
            db.session.commit()
            
            score_dict: Dict[str, Any] = score.to_dict()
            self.assertIsInstance(score_dict, dict)
            self.assertEqual(score_dict['username'], 'DictTest')
            self.assertEqual(score_dict['score'], 3000)
            self.assertEqual(score_dict['lines_cleared'], 30)
            self.assertEqual(score_dict['level'], 4)
            self.assertIn('timestamp', score_dict)
    
    def test_empty_leaderboard(self) -> None:
        """Test leaderboard with no scores."""
        response: Response = self.app.get('/leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No scores yet', response.data)
    
    def test_duplicate_username_handling(self) -> None:
        """Test handling of duplicate usernames."""
        score_data1: Dict[str, Union[str, int]] = {
            'username': 'DuplicateUser',
            'score': 1000,
            'lines': 10,
            'level': 2
        }
        
        score_data2: Dict[str, Union[str, int]] = {
            'username': 'DuplicateUser',
            'score': 2000,
            'lines': 20,
            'level': 3
        }
        
        # Save first score
        response1: Response = self.app.post('/api/score',
                                          data=json.dumps(score_data1),
                                          content_type='application/json')
        self.assertEqual(response1.status_code, 200)
        
        # Save second score with same username
        response2: Response = self.app.post('/api/score',
                                          data=json.dumps(score_data2),
                                          content_type='application/json')
        self.assertEqual(response2.status_code, 200)
        
        # Verify only one player exists with two scores
        with app.app_context():
            player: Optional[Player] = Player.query.filter_by(username='DuplicateUser').first()
            self.assertIsNotNone(player)
            self.assertEqual(len(player.scores), 2)


def run_tests() -> None:
    """Run all tests."""
    unittest.main(verbosity=2)


if __name__ == '__main__':
    run_tests()