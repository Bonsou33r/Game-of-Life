#!/usr/bin/env python3

import threading
import time
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    from game_of_life_pygame import GameOfLife
except ImportError as e:
    logging.error(f"Failed to import GameOfLife: {e}")
    print("Error: Could not import game_of_life_pygame module.")
    print("Make sure game_of_life_pygame.py is in the same directory.")
    sys.exit(1)

class GameLauncher:
    def __init__(self):
        self.game = None
        self.game_thread = None
        self.running = True
        self.logger = logging.getLogger(__name__)

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self):
        """Print the application header"""
        print("=" * 60)
        print("            CONWAY'S GAME OF LIFE - DOCKER EDITION")
        print("=" * 60)

    def print_controls(self):
        """Print available controls"""
        print("\nGAME CONTROLS (in the game window):")
        print("-" * 40)
        print("SPACE     - Pause/Resume simulation")
        print("R         - Reset with new random pattern")
        print("C         - Clear the grid (kill all cells)")
        print("Q/ESC     - Quit the application")
        print("↑/↓       - Increase/Decrease grid size (+/- 10)")
        print("+/-       - Increase/Decrease FPS target (+/- 5)")
        print("-" * 40)

    def get_initial_settings(self):
        """Get initial settings from user with simplified input"""
        self.clear_screen()
        self.print_header()

        print("\nWelcome! Setting up your Game of Life simulation...")
        print("\nGame controls will be available in the game window once it opens.")

        # Simple grid size input with timeout
        print("\nPress ENTER for default settings, or enter a grid size (10-200):")

        try:
            # Set a reasonable timeout for input
            import signal

            def timeout_handler(signum, frame):
                raise TimeoutError("Input timeout")

            # Only set timeout on Unix systems
            if hasattr(signal, 'SIGALRM'):
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(10)  # 10 second timeout

            try:
                size_input = input("Grid size (default 50): ").strip()
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)  # Cancel timeout

                if not size_input:
                    grid_size = 50
                else:
                    grid_size = int(size_input)
                    grid_size = max(10, min(200, grid_size))

            except TimeoutError:
                print("\nTimeout reached, using default settings...")
                grid_size = 50
            except ValueError:
                print("Invalid input, using default size...")
                grid_size = 50

        except Exception:
            # Fallback for any other issues
            grid_size = 50

        print(f"\nInitializing {grid_size}x{grid_size} grid...")
        return grid_size

    def start_game(self, grid_size):
        """Start the game in a separate thread"""
        try:
            self.game = GameOfLife(grid_size)
            self.logger.info(f"Game initialized with grid size {grid_size}")
        except Exception as e:
            self.logger.error(f"Failed to initialize game: {e}")
            print(f"\nError initializing game: {e}")
            print("Make sure you have proper display/X11 forwarding setup")
            print("For Docker: ensure 'xhost +local:docker' has been run")
            self.running = False
            return False

        def run_game():
            try:
                if self.game:
                    self.game.run()
            except KeyboardInterrupt:
                self.logger.info("Game interrupted by user")
            except Exception as e:
                self.logger.error(f"Game error: {e}")
                print(f"Game error: {e}")
            finally:
                self.running = False

        self.game_thread = threading.Thread(target=run_game, daemon=True)
        self.game_thread.start()
        return True

    def wait_for_game(self):
        """Simple wait loop for game completion"""
        print("\n" + "=" * 60)
        print("GAME IS STARTING...")
        print("=" * 60)
        print("\nThe game window should appear shortly.")
        self.print_controls()
        print("\nWaiting for game to finish...")
        print("Press Ctrl+C to force quit if needed.\n")

        # Simple status updates every 10 seconds
        last_status = time.time()

        try:
            while self.running and (not self.game_thread or self.game_thread.is_alive()):
                time.sleep(1)

                # Show periodic status
                current_time = time.time()
                if current_time - last_status > 10:  # Every 10 seconds
                    if self.game and not self.game.paused:
                        print(f"Game running - Generation: {self.game.generation} | "
                              f"Living cells: {int(self.game.grid_current.sum())} | "
                              f"FPS: {self.game.fps_actual}")
                    last_status = current_time

        except KeyboardInterrupt:
            print("\nShutting down game...")
            if self.game:
                self.game.running = False
            self.running = False

    def cleanup(self):
        """Clean up resources"""
        self.logger.info("Cleaning up...")
        if self.game:
            self.game.running = False
        if self.game_thread and self.game_thread.is_alive():
            self.game_thread.join(timeout=3)
            if self.game_thread.is_alive():
                self.logger.warning("Game thread did not terminate gracefully")

    def run(self):
        """Main launcher function - simplified version"""
        try:
            # Get initial settings
            grid_size = self.get_initial_settings()

            # Start the game
            if not self.start_game(grid_size):
                return

            # Wait for game to complete
            self.wait_for_game()

        except KeyboardInterrupt:
            print("\nApplication terminated by user")
            self.logger.info("Application terminated by user interrupt")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            self.logger.error(f"Unexpected error in launcher: {e}")
        finally:
            self.cleanup()
            print("\nThank you for playing Conway's Game of Life!")

def main():
    """Main entry point"""
    print("Initializing Game of Life launcher...")
    logging.info("Starting Game of Life launcher")

    try:
        launcher = GameLauncher()
        launcher.run()
    except Exception as e:
        logging.error(f"Fatal error in main: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
