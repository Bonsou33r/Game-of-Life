import numpy as np
import pygame
import sys
import time
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class GameOfLife:
    def __init__(self, initial_size=50, headless=False):
        self.headless = headless

        if not self.headless:
            try:
                pygame.init()
                if not pygame.get_init():
                    raise RuntimeError("Pygame failed to initialize")
                logging.info("Pygame initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize Pygame: {e}")
                raise
        else:
            logging.info("Running in headless mode - Pygame skipped")

        # Game settings
        self.grid_size = initial_size
        self.cell_size = 10
        self.generation = 0
        self.running = True
        self.paused = False
        self.fps_target = 30
        self.fps_actual = 0

        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GRAY = (128, 128, 128)

        # Initialize grids
        self.reset_grid()

        # Setup windows (skip in headless mode)
        if not self.headless:
            self.setup_windows()

        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps_counter = 0
        self.fps_timer = time.time()

    def setup_windows(self):
        if self.headless:
            logging.info("Skipping window setup in headless mode")
            return

        try:
            # Main game window
            self.game_width = max(400, self.grid_size * self.cell_size)
            self.game_height = max(300, self.grid_size * self.cell_size + 100)  # Extra space for info

            # Limit window size to reasonable bounds
            max_width, max_height = 1800, 1200
            if self.game_width > max_width or self.game_height > max_height:
                scale_factor = min(max_width / self.game_width, max_height / self.game_height)
                self.cell_size = max(1, int(self.cell_size * scale_factor))
                self.game_width = self.grid_size * self.cell_size
                self.game_height = self.grid_size * self.cell_size + 100

            self.game_screen = pygame.display.set_mode((self.game_width, self.game_height))
            pygame.display.set_caption("Conway's Game of Life")

            # Control panel window (smaller)
            self.control_width = 400
            self.control_height = 300
            self.control_screen = pygame.Surface((self.control_width, self.control_height))

            # Font for text with error handling
            try:
                self.font_large = pygame.font.Font(None, 24)
                self.font_medium = pygame.font.Font(None, 18)
                self.font_small = pygame.font.Font(None, 16)
            except pygame.error:
                # Fallback to default font
                default_font_name = pygame.font.get_default_font()
                self.font_large = pygame.font.Font(default_font_name, 24)
                self.font_medium = pygame.font.Font(default_font_name, 18)
                self.font_small = pygame.font.Font(default_font_name, 16)
                logging.warning("Using default font due to font loading error")

            logging.info(f"Window setup complete: {self.game_width}x{self.game_height}")

        except pygame.error as e:
            logging.error(f"Failed to setup display: {e}")
            raise RuntimeError(f"Could not create game window: {e}")
        except Exception as e:
            logging.error(f"Unexpected error in window setup: {e}")
            raise

    def reset_grid(self):
        """Initialize or reset the game grid"""
        try:
            # Validate grid size
            if not (10 <= self.grid_size <= 200):
                logging.warning(f"Invalid grid size {self.grid_size}, clamping to valid range")
                self.grid_size = max(10, min(200, self.grid_size))

            self.grid_current = np.random.randint(0, 2, size=(self.grid_size, self.grid_size), dtype=np.uint8)
            self.grid_next = np.zeros((self.grid_size, self.grid_size), dtype=np.uint8)
            self.generation = 0
            logging.info(f"Grid reset: {self.grid_size}x{self.grid_size}")
        except MemoryError:
            logging.error(f"Not enough memory for grid size {self.grid_size}")
            self.grid_size = 50  # Fallback to smaller size
            self.reset_grid()
        except Exception as e:
            logging.error(f"Error resetting grid: {e}")
            raise

    def neighbours(self, grid):
        """Calculate neighbor counts efficiently using NumPy"""
        counter = np.zeros_like(grid, dtype=int)

        counter[1:, 1:] += grid[:-1, :-1]
        counter[1:, :-1] += grid[:-1, 1:]
        counter[:-1, 1:] += grid[1:, :-1]
        counter[:-1, :-1] += grid[1:, 1:]
        counter[1:, :] += grid[:-1, :]
        counter[:-1, :] += grid[1:, :]
        counter[:, 1:] += grid[:, :-1]
        counter[:, :-1] += grid[:, 1:]

        return counter

    def rules(self, current_grid, next_grid, counter):
        """Apply Conway's Game of Life rules"""
        next_grid.fill(0)
        next_grid[(current_grid == 1) & ((counter == 2) | (counter == 3))] = 1
        next_grid[(current_grid == 0) & (counter == 3)] = 1

    def handle_input(self, event):
        """Handle keyboard input for game controls"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.paused = not self.paused
            elif event.key == pygame.K_r:
                self.reset_grid()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                self.running = False
            elif event.key == pygame.K_UP:
                self.change_grid_size(min(200, self.grid_size + 10))
            elif event.key == pygame.K_DOWN:
                self.change_grid_size(max(10, self.grid_size - 10))
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                self.fps_target = min(120, self.fps_target + 5)
            elif event.key == pygame.K_MINUS:
                self.fps_target = max(1, self.fps_target - 5)
            elif event.key == pygame.K_c:
                self.grid_current.fill(0)
                self.generation = 0

    def change_grid_size(self, new_size):
        """Change the grid size and resize window accordingly"""
        try:
            if not (10 <= new_size <= 200):
                logging.warning(f"Grid size {new_size} out of range, clamping to 10-200")
                new_size = max(10, min(200, new_size))

            old_size = self.grid_size
            self.grid_size = new_size
            self.cell_size = max(2, min(15, 800 // self.grid_size))  # Adaptive cell size

            self.reset_grid()
            if not self.headless:
                self.setup_windows()
            logging.info(f"Grid size changed from {old_size} to {new_size}")
        except Exception as e:
            logging.error(f"Failed to change grid size: {e}")
            # Revert to previous size on error
            self.grid_size = getattr(self, 'grid_size', 50)
            raise

    def update_fps(self):
        """Calculate actual FPS"""
        self.fps_counter += 1
        current_time = time.time()
        if current_time - self.fps_timer >= 1.0:
            self.fps_actual = self.fps_counter
            self.fps_counter = 0
            self.fps_timer = current_time

    def draw_game(self):
        """Draw the main game screen with optimized rendering"""
        if self.headless:
            return  # Skip drawing in headless mode

        try:
            self.game_screen.fill(self.BLACK)

            # Optimized grid drawing using batch operations
            if self.cell_size >= 4:  # Only draw grid lines for larger cells
                # Draw all living cells at once using numpy indexing
                living_cells = np.where(self.grid_current == 1)
                for y, x in zip(living_cells[0], living_cells[1]):
                    rect = pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    pygame.draw.rect(self.game_screen, self.WHITE, rect)

                # Draw grid lines (optional for performance)
                if self.cell_size > 8 and self.grid_size < 100:
                    for i in range(self.grid_size + 1):
                        # Vertical lines
                        pygame.draw.line(self.game_screen, self.GRAY,
                                       (i * self.cell_size, 0),
                                       (i * self.cell_size, self.grid_size * self.cell_size))
                        # Horizontal lines
                        pygame.draw.line(self.game_screen, self.GRAY,
                                       (0, i * self.cell_size),
                                       (self.grid_size * self.cell_size, i * self.cell_size))
            else:
                # For very small cells, just draw pixels
                for y in range(self.grid_size):
                    for x in range(self.grid_size):
                        if self.grid_current[y, x] == 1:
                            rect = pygame.Rect(x * self.cell_size, y * self.cell_size,
                                             self.cell_size, self.cell_size)
                            pygame.draw.rect(self.game_screen, self.WHITE, rect)

            # Draw info panel
            info_y = self.grid_size * self.cell_size + 10

            # Title
            title_text = self.font_large.render("Conway's Game of Life", True, self.WHITE)
            self.game_screen.blit(title_text, (10, info_y))

            # Generation counter
            gen_text = self.font_medium.render(f"Generation: {self.generation}", True, self.GREEN)
            self.game_screen.blit(gen_text, (10, info_y + 30))

            # FPS info
            fps_text = self.font_medium.render(f"FPS: {self.fps_actual} / {self.fps_target}", True, self.BLUE)
            self.game_screen.blit(fps_text, (200, info_y + 30))

            # Status
            status_color = self.RED if self.paused else self.GREEN
            status_text = "PAUSED" if self.paused else "RUNNING"
            status_render = self.font_medium.render(f"Status: {status_text}", True, status_color)
            self.game_screen.blit(status_render, (10, info_y + 55))

            # Grid size and living cells count
            living_cells = int(self.grid_current.sum())
            size_text = self.font_medium.render(f"Grid: {self.grid_size}x{self.grid_size} | Cells: {living_cells}", True, self.WHITE)
            self.game_screen.blit(size_text, (200, info_y + 55))

            pygame.display.flip()

        except pygame.error as e:
            logging.error(f"Display error: {e}")
            # Don't crash the game, just skip this frame
        except Exception as e:
            logging.error(f"Unexpected error in draw_game: {e}")
            raise

    def print_controls(self):
        """Print controls to terminal"""
        controls = """
=== GAME OF LIFE CONTROLS ===

SPACE       - Pause/Resume
R           - Reset with random pattern
C           - Clear grid
Q/ESC       - Quit
↑/↓         - Change grid size (+/- 10)
+/-         - Change FPS target (+/- 5)

=== CURRENT STATUS ===
Grid Size:  {grid_size}x{grid_size}
FPS Target: {fps_target}
Generation: {generation}
Status:     {status}

Press Ctrl+C to exit
========================
        """.format(
            grid_size=self.grid_size,
            fps_target=self.fps_target,
            generation=self.generation,
            status="PAUSED" if self.paused else "RUNNING"
        )

        # Clear terminal and print controls
        os.system('clear' if os.name == 'posix' else 'cls')
        print(controls)

    def run(self):
        """Main game loop with better error handling"""
        try:
            if not self.headless:
                self.print_controls()
            logging.info("Starting game loop")

            while self.running:
                try:
                    # Handle events (skip in headless mode)
                    if not self.headless:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                self.running = False
                            else:
                                self.handle_input(event)

                    # Update game state
                    if not self.paused:
                        counter = self.neighbours(self.grid_current)
                        self.rules(self.grid_current, self.grid_next, counter)
                        self.grid_current, self.grid_next = self.grid_next, self.grid_current
                        self.generation += 1

                    # Update FPS counter
                    self.update_fps()

                    # Draw everything
                    self.draw_game()

                    # Control frame rate (skip in headless mode for faster testing)
                    if not self.headless:
                        self.clock.tick(self.fps_target)

                except pygame.error as e:
                    logging.error(f"Pygame error in main loop: {e}")
                    # Try to continue running
                    continue
                except KeyboardInterrupt:
                    logging.info("Game interrupted by user")
                    break
                except Exception as e:
                    logging.error(f"Unexpected error in game loop: {e}")
                    break

        except Exception as e:
            logging.error(f"Fatal error in game loop: {e}")
            raise
        finally:
            logging.info("Cleaning up and exiting")
            if not self.headless:
                try:
                    pygame.quit()
                except:
                    pass  # Ignore cleanup errors
            if not self.headless:
                sys.exit(0)

def main():
    """Main function to start the game with comprehensive error handling"""
    print("Starting Conway's Game of Life...")
    logging.info("Application starting")

    # Initialize game variable to avoid unbound variable error
    game = None

    # Get initial grid size from user
    size = 50  # Default size
    try:
        size_input = input("Enter initial grid size (10-200, default 50): ").strip()
        if size_input:
            size = int(size_input)
            if not (10 <= size <= 200):
                print(f"Size {size} out of range, using default 50")
                size = 50
    except (ValueError, EOFError, KeyboardInterrupt):
        print("Using default size: 50")
        size = 50

    print(f"Initializing {size}x{size} grid...")
    logging.info(f"Grid size: {size}")

    # Create and run game with error handling
    try:
        game = GameOfLife(size)
        game.run()
    except KeyboardInterrupt:
        print("\nGame terminated by user")
        logging.info("Game terminated by user interrupt")
    except pygame.error as e:
        print(f"\nPygame error: {e}")
        logging.error(f"Pygame error: {e}")
        print("Make sure you have proper display/X11 forwarding setup")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        logging.error(f"Unexpected error: {e}")
        raise
    finally:
        try:
            if not getattr(game, 'headless', False):
                pygame.quit()
        except:
            pass  # Ignore cleanup errors
        logging.info("Application finished")

if __name__ == "__main__":
    main()
