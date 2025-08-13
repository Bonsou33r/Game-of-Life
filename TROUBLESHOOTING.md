# Conway's Game of Life - Troubleshooting Guide

This guide helps resolve common issues when running the containerized Game of Life.

## 🚨 Quick Fixes

### Problem: Stuck on "Customization" Screen
**Symptoms:** Interface shows "watch" option, can't interact properly
**Solution:** Use the simplified direct launch:
```bash
./run.sh direct
```
Or run without launcher:
```bash
./run.sh simple
```

### Problem: "the input device is not a TTY" Error
**Solution:** Make sure you're using the interactive flag:
```bash
docker-compose run --rm -it game-of-life python start_game.py
```

### Problem: Game Window Doesn't Appear
**Solution:** Check X11 forwarding:
```bash
# Test X11 first
./run.sh test

# If test fails, configure X11:
xhost +local:docker
export DISPLAY=:0

# Then try again
./run.sh direct
```

## 🐳 Docker Issues

### Docker Not Running
**Error:** "Docker daemon is not running"
**Solutions:**
- **Linux:** `sudo systemctl start docker`
- **macOS:** Start Docker Desktop application
- **Windows:** Start Docker Desktop application

### Docker Compose Not Found
**Error:** "docker-compose: command not found"
**Solutions:**
- **Ubuntu/Debian:** `sudo apt-get install docker-compose-plugin`
- **macOS:** `brew install docker-compose`
- **Alternative:** Use `docker compose` (newer syntax)

### Permission Denied
**Error:** "permission denied while trying to connect"
**Solution:**
```bash
sudo usermod -aG docker $USER
# Then log out and back in
```

## 🖥️ Display Issues

### Linux X11 Problems
**Issue:** GUI window won't appear
**Solutions:**
1. **Check DISPLAY variable:**
   ```bash
   echo $DISPLAY
   # Should show something like :0 or :1
   ```

2. **Allow Docker access:**
   ```bash
   xhost +local:docker
   ```

3. **Check X11 socket:**
   ```bash
   ls -la /tmp/.X11-unix/
   # Should show X0, X1, etc.
   ```

4. **If still not working:**
   ```bash
   # Try different DISPLAY values
   export DISPLAY=:0
   # or
   export DISPLAY=localhost:10.0
   ```

### macOS XQuartz Issues
**Issue:** Game window doesn't appear on macOS
**Solutions:**
1. **Install XQuartz:**
   ```bash
   brew install --cask xquartz
   ```

2. **Configure XQuartz:**
   - Start XQuartz
   - Go to Preferences → Security
   - Check "Allow connections from network clients"
   - Restart XQuartz

3. **Set DISPLAY:**
   ```bash
   export DISPLAY=host.docker.internal:0
   xhost +localhost
   ```

### Windows X Server Issues
**Issue:** No GUI on Windows
**Solutions:**
1. **Install X Server:**
   - VcXsrv (recommended): Download from GitHub
   - Xming: Download from official site

2. **Configure X Server:**
   - Start X Server
   - Allow connections from Docker
   - Set DISPLAY variable

## 🐛 Interface Problems

### Launcher Interface Hangs
**Issue:** Stuck on input screen, can't proceed
**Workarounds:**
1. **Use direct mode:**
   ```bash
   ./run.sh direct
   ```

2. **Use simple mode:**
   ```bash
   ./run.sh simple
   ```

3. **Run locally (if dependencies installed):**
   ```bash
   python run_local.py
   ```

### Terminal Not Responding
**Issue:** Can't type commands in launcher
**Solutions:**
1. **Force quit:** Ctrl+C
2. **Use direct launch:** `./run.sh direct`
3. **Check TTY allocation:** Make sure `-it` flags are used

## ⚡ Performance Issues

### Game Runs Slowly
**Solutions:**
1. **Reduce grid size:** Use smaller grids (20-50 cells)
2. **Lower FPS:** Set FPS to 15-20
3. **Use game controls:** Press `-` key to reduce FPS target

### High CPU Usage
**Solutions:**
1. **Limit FPS:** Press `-` in game to reduce target FPS
2. **Smaller grid:** Press `↓` arrow to reduce grid size
3. **Pause when not watching:** Press `SPACE` to pause

### Memory Issues
**Error:** "Not enough memory for grid"
**Solutions:**
1. **Use smaller grids:** Maximum safe size is usually 100x100
2. **Close other applications**
3. **Increase Docker memory limit** (in Docker Desktop settings)

## 🔧 Build Problems

### Docker Build Fails
**Common causes and solutions:**

1. **Network issues:**
   ```bash
   # Check internet connection
   curl -I https://pypi.org
   ```

2. **Disk space:**
   ```bash
   # Check available space
   df -h
   # Clean Docker if needed
   ./run.sh clean
   ```

3. **Corrupted cache:**
   ```bash
   ./run.sh clean
   docker system prune -a
   ./run.sh build
   ```

### Missing Files Error
**Error:** "COPY failed: file not found"
**Solution:**
```bash
# Make sure all files exist
ls -la *.py *.txt *.yml
# If missing, re-download or check file names
```

## 🔍 Debugging

### Enable Verbose Logging
```bash
# Run with debug output
PYTHONUNBUFFERED=1 ./run.sh direct

# Or check container logs
docker-compose logs -f
```

### Test Components Individually

1. **Test Python dependencies:**
   ```bash
   python -c "import numpy, pygame; print('Dependencies OK')"
   ```

2. **Test game logic without display:**
   ```bash
   python -c "
   from game_of_life_pygame import GameOfLife
   game = GameOfLife(10, headless=True)
   print('Game logic OK')
   "
   ```

3. **Test X11 forwarding:**
   ```bash
   ./run.sh test
   ```

## 📱 Platform-Specific Solutions

### Ubuntu/Debian
```bash
# Install required packages
sudo apt-get update
sudo apt-get install docker.io docker-compose x11-xserver-utils

# Enable Docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

### CentOS/RHEL
```bash
# Install Docker
sudo yum install docker docker-compose xorg-x11-server-utils

# Start Docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker $USER
```

### Arch Linux
```bash
# Install packages
sudo pacman -S docker docker-compose xorg-xhost

# Enable Docker
sudo systemctl enable docker.service
sudo systemctl start docker.service
sudo usermod -aG docker $USER
```

## 🆘 Still Not Working?

### Last Resort Options

1. **Run without Docker:**
   ```bash
   # Install dependencies locally
   pip install numpy pygame
   
   # Run directly
   python start_game.py
   ```

2. **Use local test runner:**
   ```bash
   python run_local.py
   ```

3. **Check system compatibility:**
   ```bash
   # Check Python version (needs 3.8+)
   python --version
   
   # Check available memory
   free -h
   
   # Check graphics support
   glxinfo | grep OpenGL
   ```

### Get Help
If none of these solutions work:

1. **Check the logs:**
   ```bash
   docker-compose logs > game_logs.txt
   ```

2. **Collect system info:**
   ```bash
   uname -a > system_info.txt
   docker version >> system_info.txt
   echo $DISPLAY >> system_info.txt
   ```

3. **Try the absolute simplest version:**
   ```bash
   python -c "
   import pygame
   pygame.init()
   screen = pygame.display.set_mode((400, 300))
   pygame.display.set_caption('Test')
   print('Basic pygame works!')
   pygame.time.wait(2000)
   pygame.quit()
   "
   ```

## ✅ Working Configuration Examples

### Linux (Ubuntu 20.04+)
```bash
export DISPLAY=:0
xhost +local:docker
./run.sh direct
```

### macOS (with XQuartz)
```bash
export DISPLAY=host.docker.internal:0
xhost +localhost
./run.sh direct
```

### Windows (with VcXsrv)
```bash
export DISPLAY=localhost:0.0
./run.sh direct
```
