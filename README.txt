Tetris Game Web Application
A modern, fully-featured Tetris game built with Flask and JavaScript. 


Installation & Setup
Prerequisites
Python 3.11 or higher
pip (Python package manager)

Install dependencies:
bash   pip install -r requirements.txt

Run the application:
bash   python app.py

Build the Docker image:
bash   docker build -t tetris-game .

Run the container:
bash   docker run -p 5000:5000 tetris-game


Testing
Run the unit tests with:
bashpython -m pytest test_app.py -v
Or using Python's built-in unittest:
bashpython test_app.py


How to play:
← Move left
→ Move right
↓ Soft drop (faster fall)
↑ Rotate piece
Spacebar  Hard drop (instant fall)
P Pause/Resume game


Technologies Used

Backend: Python 3.11, Flask, SQLAlchemy
Frontend: HTML5 Canvas, JavaScript ES6, CSS3
Database: SQLite
Styling: Modern CSS with gradients and backdrop filters
Deployment: Docker support included