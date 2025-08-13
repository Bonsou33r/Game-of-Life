# Conway's Game of Life - Docker Edition

A containerized implementation of Conway's Game of Life using Python, NumPy, and Pygame. This optimized version features a dual-window interface with real-time controls and runs efficiently in a Docker container.

## Features

- 🎮 **Optimized Pygame Interface**: Smooth, responsive game visualization
- 🖥️ **Dual Window System**:
  - Main game window with visual simulation
  - Terminal interface for controls and status
- ⚡ **High Performance**: NumPy-optimized neighbor calculations
- 🎛️ **Real-time Controls**: Adjust settings without restarting
- 🐳 **Containerized**: Easy deployment with Docker
- 📊 **Live Statistics**: Generation counter, FPS monitor, cell count
- 🔧 **Configurable**: Adjustable grid size, FPS, and patterns

## Prerequisites

### For Docker (Recommended)
- Docker and Docker Compose installed
- X11 forwarding support (Linux/macOS) or X server (Windows)
- GPU support recommended for smooth graphics

### For Local Development

- Python 3.8+
- NumPy and Pygame
- GUI environment

## Quick Start with Docker

### 1. Clone the Repository
```bash
git clone https://github.com/Bonsou33r/Game-of-Life.git
cd Game-of-Life
```

### 2. Build and Run with Docker Compose
```bash
# Allow X11 forwarding (Linux/macOS)
xhost +local:docker

# Build and run with terminal interface
docker-compose up --build

# OR run simple version without terminal interface
docker-compose --profile simple up game-only --build
```

### 3. Alternative: Manual Docker Build
```bash
# Build the image
docker build -t game-of-life .

# Run the container
docker run -it \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  --network host \
  game-of-life
```

## Game Controls

### In-Game Keyboard Controls
| Key | Action |
|-----|--------|
| `SPACE` | Pause/Resume simulation |
| `R` | Reset with new random pattern |
| `C` | Clear the grid (kill all cells) |
| `Q` / `ESC` | Quit the application |
| `↑` / `↓` | Increase/Decrease grid size (+/- 10) |
| `+` / `-` | Increase/Decrease FPS target (+/- 5) |

### Terminal Commands (when using launcher)
| Command | Description |
|---------|-------------|
| `status` | Show current game status |
| `help` | Show help message |
| `quit` | Exit the application |
| `reset` | Reset the game |
| `pause` | Toggle pause state |
| `size X` | Change grid size to X (e.g., `size 100`) |
| `fps X` | Change FPS target to X (e.g., `fps 60`) |

## Architecture

### Files Structure
```
Game-of-Life/
├── Dockerfile                 # Container definition
├── docker-compose.yml         # Multi-service configuration
├── game_of_life_pygame.py     # Main game implementation
├── launcher.py                # Terminal interface launcher
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

### Game Components
- **GameOfLife Class**: Core game logic with NumPy optimization
- **Pygame Renderer**: Efficient graphics rendering
- **Terminal Interface**: Command-line controls and status
- **FPS Controller**: Smooth animation timing

## Configuration Options

### Environment Variables
- `DISPLAY`: X11 display for GUI forwarding
- `SDL_VIDEODRIVER`: Video driver for Pygame (default: x11)

### Runtime Settings
- **Grid Size**: 10-200 cells (adjustable)
- **FPS Target**: 1-120 FPS (adjustable)
- **Cell Size**: Auto-adaptive based on grid size
- **Colors**: Customizable color scheme

## Performance Optimization

- **NumPy Vectorization**: Efficient neighbor counting
- **Memory Management**: In-place grid operations
- **Adaptive Rendering**: Cell size adjusts to grid size
- **Frame Rate Control**: Configurable FPS limiting

## Platform Support

### Linux (Native)
```bash
# Install X11 forwarding support
sudo apt-get install x11-apps

# Allow Docker X11 access
xhost +local:docker
```

### macOS
```bash
# Install XQuartz for X11 support
brew install --cask xquartz

# Configure XQuartz and restart
# Then allow connections: xhost +localhost
```

### Windows
```bash
# Install VcXsrv or Xming
# Configure X server to allow connections
# Set DISPLAY environment variable
```

## Troubleshooting

### Common Issues

**Display Issues**
```bash
# If GUI doesn't appear, check X11 forwarding
echo $DISPLAY
xhost +local:docker

# Test X11 with simple app
docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix:rw alpine:latest sh -c "apk add --no-cache xeyes && xeyes"
```

**Permission Errors**
```bash
# Fix X11 permissions
sudo chown $USER:$USER /tmp/.X11-unix/X*
chmod 755 /tmp/.X11-unix/X*
```

**Performance Issues**
- Reduce grid size for better FPS
- Lower FPS target for smoother animation
- Ensure GPU acceleration is available

### Debug Mode
```bash
# Run with verbose output
docker-compose up --build --verbose

# Check container logs
docker logs conways-game-of-life
```

## Development

### Local Development Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python launcher.py
# or
python game_of_life_pygame.py
```

### Building Custom Images
```bash
# Build with custom tag
docker build -t my-game-of-life:latest .

# Build for different architecture
docker buildx build --platform linux/amd64,linux/arm64 -t game-of-life .
```

## Conway's Game of Life Rules

1. **Birth**: A dead cell with exactly 3 neighbors becomes alive
2. **Survival**: A living cell with 2 or 3 neighbors stays alive
3. **Death**: A living cell with fewer than 2 or more than 3 neighbors dies

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker
5. Submit a pull request

## License

This project is open source. Feel free to use, modify, and distribute.

## Acknowledgments

- John Conway for the original Game of Life
- NumPy community for optimization techniques
- Pygame developers for the graphics framework
