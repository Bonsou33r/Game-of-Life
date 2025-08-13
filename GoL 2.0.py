import numpy as np
import matplotlib.pyplot as plt

def neighbours(grid):
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

def rules(current_grid, next_grid, counter):
    next_grid.fill(0)
    next_grid[(current_grid == 1) & ((counter == 2) | (counter == 3))] = 1
    next_grid[(current_grid == 0) & (counter == 3)] = 1

def main():
    global grid_current, grid_next, generation
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 10))
    size = int(input("Taille de la grille: "))
    print("Création des grilles...")
    grid_current = np.random.randint(0, 2, size=(size, size))
    grid_next = np.zeros((size, size), dtype=int)
    im = ax.imshow(grid_current, cmap='binary', interpolation='nearest', origin='lower')
    ax.set_title("Jeu de la Vie")
    generation = 0

    print("Lancement du jeu...")

    try:
        while plt.fignum_exists(fig.number):
            counter = neighbours(grid_current)
            rules(grid_current, grid_next, counter)
            grid_current, grid_next = grid_next, grid_current
            generation += 1
            im.set_data(grid_current)
            ax.set_title(f"Génération n°{generation}")
            fig.canvas.draw()
            fig.canvas.flush_events()
    except KeyboardInterrupt:
        print(f"\nJeu arrêté à la génération n°{generation}")

    finally:
        plt.ioff()
        if plt.fignum_exists(fig.number):
            plt.show()

main()
