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
            if (this.gameOver) return;
            
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
        const randomType = pieceTypes[Math.floor(Math.random() * pieceTypes.length)];
        
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