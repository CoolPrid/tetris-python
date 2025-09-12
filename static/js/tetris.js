/**
 * Tetris game implementation in JavaScript
 * Handles game rendering and user input
 */

class TetrisGame {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.blockSize = 30;
        this.boardWidth = 10;
        this.boardHeight = 20;
        
        // Set canvas size
        this.canvas.width = this.boardWidth * this.blockSize;
        this.canvas.height = this.boardHeight * this.blockSize;
        
        // Game state
        this.board = [];
        this.currentPiece = null;
        this.nextPiece = null;
        this.score = 0;
        this.lines = 0;
        this.level = 1;
        this.gameOver = false;
        this.isPaused = false;
        
        // Timing
        this.dropTime = 1000;
        this.lastDrop = 0;
        
        // Initialize board
        this.initBoard();
        
        // Piece definitions
        this.pieces = {
            I: { shape: [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]], color: '#00F0F0' },
            O: { shape: [[1,1], [1,1]], color: '#F0F000' },
            T: { shape: [[0,1,0], [1,1,1], [0,0,0]], color: '#A000F0' },
            S: { shape: [[0,1,1], [1,1,0], [0,0,0]], color: '#00F000' },
            Z: { shape: [[1,1,0], [0,1,1], [0,0,0]], color: '#F00000' },
            J: { shape: [[1,0,0], [1,1,1], [0,0,0]], color: '#0000F0' },
            L: { shape: [[0,0,1], [1,1,1], [0,0,0]], color: '#F0A000' }
        };
        
        // Bind keyboard events
        this.bindEvents();
        
        // Start game
        this.spawnPiece();
        this.gameLoop();
    }
    
    initBoard() {
        this.board = Array(this.boardHeight).fill().map(() => 
            Array(this.boardWidth).fill(null)
        );
    }
    
    bindEvents() {
        document.addEventListener('keydown', (e) => {
            if (this.gameOver || this.isPaused) return;
            
            switch(e.key) {
                case 'ArrowLeft':
                    this.movePiece(-1, 0);
                    break;
                case 'ArrowRight':
                    this.movePiece(1, 0);
                    break;
                case 'ArrowDown':
                    this.movePiece(0, 1);
                    break;
                case 'ArrowUp':
                    this.rotatePiece();
                    break;
                case ' ':
                    e.preventDefault();
                    this.dropPiece();
                    break;
                case 'p':
                case 'P':
                    this.togglePause();
                    break;
            }
        });
    }
    
    spawnPiece() {
        const pieceTypes = Object.keys(this.pieces);
        
        if (!this.nextPiece) {
            const nextType = pieceTypes[Math.floor(Math.random() * pieceTypes.length)];
            this.nextPiece = {
                type: nextType,
                shape: JSON.parse(JSON.stringify(this.pieces[nextType].shape)),
                color: this.pieces[nextType].color,
                x: 0,
                y: 0
            };
        }
        
        this.currentPiece = this.nextPiece;
        this.currentPiece.x = Math.floor((this.boardWidth - this.currentPiece.shape[0].length) / 2);
        this.currentPiece.y = 0;
        
        // Generate next piece
        const nextType = pieceTypes[Math.floor(Math.random() * pieceTypes.length)];
        this.nextPiece = {
            type: nextType,
            shape: JSON.parse(JSON.stringify(this.pieces[nextType].shape)),
            color: this.pieces[nextType].color,
            x: 0,
            y: 0
        };
        
        // Update next piece preview
        this.drawNextPiece();
        
        // Check game over
        if (!this.isValidPosition(this.currentPiece.shape, this.currentPiece.x, this.currentPiece.y)) {
            this.endGame();
        }
    }
    
    isValidPosition(shape, x, y) {
        for (let row = 0; row < shape.length; row++) {
            for (let col = 0; col < shape[row].length; col++) {
                if (shape[row][col]) {
                    const newX = x + col;
                    const newY = y + row;
                    
                    if (newX < 0 || newX >= this.boardWidth || 
                        newY >= this.boardHeight ||
                        (newY >= 0 && this.board[newY][newX])) {
                        return false;
                    }
                }
            }
        }
        return true;
    }
    
    movePiece(dx, dy) {
        if (!this.currentPiece) return;
        
        const newX = this.currentPiece.x + dx;
        const newY = this.currentPiece.y + dy;
        
        if (this.isValidPosition(this.currentPiece.shape, newX, newY)) {
            this.currentPiece.x = newX;
            this.currentPiece.y = newY;
            return true;
        }
        
        // If can't move down, lock piece
        if (dy > 0) {
            this.lockPiece();
        }
        
        return false;
    }
    
    rotatePiece() {
        if (!this.currentPiece) return;
        
        const rotated = this.currentPiece.shape[0].map((_, i) =>
            this.currentPiece.shape.map(row => row[i]).reverse()
        );
        
        if (this.isValidPosition(rotated, this.currentPiece.x, this.currentPiece.y)) {
            this.currentPiece.shape = rotated;
        }
    }
    
    dropPiece() {
        if (!this.currentPiece) return;
        
        while (this.movePiece(0, 1)) {
            this.score += 2;
        }
        this.updateScore();
    }
    
    lockPiece() {
        if (!this.currentPiece) return;
        
        // Add piece to board
        for (let row = 0; row < this.currentPiece.shape.length; row++) {
            for (let col = 0; col < this.currentPiece.shape[row].length; col++) {
                if (this.currentPiece.shape[row][col]) {
                    const boardY = this.currentPiece.y + row;
                    const boardX = this.currentPiece.x + col;
                    if (boardY >= 0) {
                        this.board[boardY][boardX] = this.currentPiece.color;
                    }
                }
            }
        }
        
        // Clear completed lines
        this.clearLines();
        
        // Spawn next piece
        this.spawnPiece();
    }
    
    clearLines() {
        let linesCleared = 0;
        
        for (let row = this.boardHeight - 1; row >= 0; row--) {
            if (this.board[row].every(cell => cell !== null)) {
                this.board.splice(row, 1);
                this.board.unshift(Array(this.boardWidth).fill(null));
                linesCleared++;
                row++; // Check the same row again
            }
        }
        
        if (linesCleared > 0) {
            this.lines += linesCleared;
            
            // Calculate score based on lines cleared
            const lineScores = [0, 40, 100, 300, 1200];
            this.score += lineScores[Math.min(linesCleared, 4)] * this.level;
            
            // Level up every 10 lines
            this.level = Math.floor(this.lines / 10) + 1;
            
            // Increase drop speed
            this.dropTime = Math.max(50, 1000 - (this.level - 1) * 50);
            
            this.updateScore();
        }
    }
    
    togglePause() {
        this.isPaused = !this.isPaused;
    }
    
    gameLoop() {
        if (!this.gameOver && !this.isPaused) {
            const currentTime = Date.now();
            
            if (currentTime - this.lastDrop > this.dropTime) {
                this.movePiece(0, 1);
                this.lastDrop = currentTime;
            }
        }
        
        this.draw();
        requestAnimationFrame(() => this.gameLoop());
    }
    
    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw board
        for (let row = 0; row < this.boardHeight; row++) {
            for (let col = 0; col < this.boardWidth; col++) {
                if (this.board[row][col]) {
                    this.drawBlock(col, row, this.board[row][col]);
                }
            }
        }
        
        // Draw current piece
        if (this.currentPiece) {
            for (let row = 0; row < this.currentPiece.shape.length; row++) {
                for (let col = 0; col < this.currentPiece.shape[row].length; col++) {
                    if (this.currentPiece.shape[row][col]) {
                        this.drawBlock(
                            this.currentPiece.x + col,
                            this.currentPiece.y + row,
                            this.currentPiece.color
                        );
                    }
                }
            }
        }
        
        // Draw grid lines
        this.drawGrid();
    }
    
    drawBlock(x, y, color) {
        const pixelX = x * this.blockSize;
        const pixelY = y * this.blockSize;
        
        this.ctx.fillStyle = color;
        this.ctx.fillRect(pixelX, pixelY, this.blockSize, this.blockSize);
        
        // Draw border
        this.ctx.strokeStyle = '#333';
        this.ctx.lineWidth = 1;
        this.ctx.strokeRect(pixelX, pixelY, this.blockSize, this.blockSize);
    }
    
    drawGrid() {
        this.ctx.strokeStyle = '#222';
        this.ctx.lineWidth = 1;
        
        for (let col = 0; col <= this.boardWidth; col++) {
            this.ctx.beginPath();
            this.ctx.moveTo(col * this.blockSize, 0);
            this.ctx.lineTo(col * this.blockSize, this.canvas.height);
            this.ctx.stroke();
        }
        
        for (let row = 0; row <= this.boardHeight; row++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, row * this.blockSize);
            this.ctx.lineTo(this.canvas.width, row * this.blockSize);
            this.ctx.stroke();
        }
    }
    
    drawNextPiece() {
        const nextCanvas = document.getElementById('next-piece-canvas');
        if (!nextCanvas) return;
        
        const nextCtx = nextCanvas.getContext('2d');
        const nextBlockSize = 20;
        
        // Clear canvas
        nextCtx.fillStyle = '#000';
        nextCtx.fillRect(0, 0, nextCanvas.width, nextCanvas.height);
        
        if (this.nextPiece) {
            const shape = this.nextPiece.shape;
            const startX = (nextCanvas.width - shape[0].length * nextBlockSize) / 2;
            const startY = (nextCanvas.height - shape.length * nextBlockSize) / 2;
            
            for (let row = 0; row < shape.length; row++) {
                for (let col = 0; col < shape[row].length; col++) {
                    if (shape[row][col]) {
                        const x = startX + col * nextBlockSize;
                        const y = startY + row * nextBlockSize;
                        
                        nextCtx.fillStyle = this.nextPiece.color;
                        nextCtx.fillRect(x, y, nextBlockSize, nextBlockSize);
                        
                        nextCtx.strokeStyle = '#333';
                        nextCtx.lineWidth = 1;
                        nextCtx.strokeRect(x, y, nextBlockSize, nextBlockSize);
                    }
                }
            }
        }
    }
    
    updateScore() {
        document.getElementById('score').textContent = this.score;
        document.getElementById('lines').textContent = this.lines;
        document.getElementById('level').textContent = this.level;
    }
    
    endGame() {
        this.gameOver = true;
        document.getElementById('final-score').textContent = this.score;
        document.getElementById('game-over-overlay').style.display = 'flex';
    }
    
    restart() {
        this.board = [];
        this.currentPiece = null;
        this.nextPiece = null;
        this.score = 0;
        this.lines = 0;
        this.level = 1;
        this.gameOver = false;
        this.isPaused = false;
        this.dropTime = 1000;
        this.lastDrop = 0;
        
        this.initBoard();
        this.spawnPiece();
        this.updateScore();
        
        document.getElementById('game-over-overlay').style.display = 'none';
    }
}

// Game management functions
let game;

function startGame() {
    game = new TetrisGame('tetris-canvas');
}

function saveScore() {
    const username = document.getElementById('username-input').value.trim();
    
    if (!username) {
        alert('Please enter a username!');
        return;
    }
    
    const scoreData = {
        username: username,
        score: game.score,
        lines: game.lines,
        level: game.level
    };
    
    fetch('/api/score', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(scoreData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Score saved successfully!');
            document.getElementById('username-input').value = '';
        } else {
            alert('Error saving score: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error saving score!');
    });
}

function restartGame() {
    game.restart();
}

// Initialize game when page loads
document.addEventListener('DOMContentLoaded', function() {
    startGame();
});