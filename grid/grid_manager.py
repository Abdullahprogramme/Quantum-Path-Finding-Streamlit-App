# This is the main grid file #
"""
Grid is 2D
Each cell is one of the following:
- "empty" with colour white
- "obstacle" with colour black
- "start" with colour green
- "end" with colour red
"""

from typing import List, Tuple, Set
import random as r

# Defining the constant variables to be used in the grid
Cell = Tuple[int, int] # A cell is represented as a tuple of (row, column)
Grid = List[List[str]] # A grid is a 2D list of strings representing the cell types

EMPTY = "empty"
OBSTACLE = "obstacle"   
START = "start"
END = "end"


# Grid Manager class to handle the grid operations
class GridManager:
    """
    A class to manage the grid and its operations such as creating the grid, adding obstacles, and finding paths.
    
    Parameters:
    n: int - The size of the grid (n x n)
    obstacle_percentage: float - The percentage of cells that will be obstacles
    random_seed: int - A random seed for reproducibility
    """

    def __init__(self, n: int, obstacle_percentage: float = 0.4, random_seed: int = 42):
        self.n = n
        self.obstacle_percentage = obstacle_percentage
        self.random_seed = random_seed
        
        # Create the empty grid
        self.grid: Grid = self._create_grid(n)

        # Place the start and end points
        self.start: Cell = (0, 0)
        self.end: Cell = (n - 1, n - 1)
        self.grid[self.start[0]][self.start[1]] = START
        self.grid[self.end[0]][self.end[1]] = END

        # Place the obstacles
        self._place_obstacles(obstacle_percentage, random_seed)

    @staticmethod
    def _create_grid(n: int) -> Grid:
        """Creates an n x n grid filled with empty cells."""
        return [[EMPTY for _ in range(n)] for _ in range(n)]
    
    def _place_obstacles(self, obstacle_percentage: float, random_seed: int):
        """Places obstacles randomly in the grid based on the given percentage."""

        random = r.Random(random_seed) # Create a random generator with the given seed

        # Calculate the total number of cells and the number of obstacles to place
        total_cells = self.total_cells()
        num_obstacles = int(total_cells * obstacle_percentage)

        # Building a list of all possible cells excluding the start and end points
        possible_cells: List[Cell] = [(row, col) for row in range(self.n) for col in range(self.n) if (row, col) != self.start and (row, col) != self.end]

        random.shuffle(possible_cells) # Shuffle the list of possible cells to randomize obstacle placement

        placed = 0
        for cell in possible_cells:
            if placed >= num_obstacles:
                break

            row, col = cell
            self.grid[row][col] = OBSTACLE
            placed += 1

    def total_cells(self) -> int:
        """Total number of cells in the grid."""
        return self.n * self.n
    
    def neighbors(self, cell: Cell) -> List[Cell]:
        """
        Returns the valid neighboring cells (up, down, left, right) that are not obstacles.
        """

        row, col = cell
        potential_neighbors = [
            (row - 1, col), # Up
            (row + 1, col), # Down
            (row, col - 1), # Left
            (row, col + 1)  # Right
        ]

        valid_neighbors = []
        for r, c in potential_neighbors:
            if 0 <= r < self.n and 0 <= c < self.n and self.grid[r][c] != OBSTACLE:
                valid_neighbors.append((r, c))

        return valid_neighbors
    
    def is_not_obstacle(self, cell: Cell) -> bool:
        """Checks if a given cell is not an obstacle."""
        row, col = cell
        return self.grid[row][col] != OBSTACLE
    
    def get_all_non_obstacle_cells(self) -> List[Cell]:
        """Returns a set of all cells that are not obstacles."""

        non_obstacle_cells = []
        for row in range(self.n):
            for col in range(self.n):
                if self.grid[row][col] != OBSTACLE:
                    non_obstacle_cells.append((row, col))

        return non_obstacle_cells
    
    def get_all_obstacle_cells(self) -> Set[Cell]:
        """Returns a set of all cells that are obstacles."""

        return {(row, col) for row in range(self.n) for col in range(self.n) if self.grid[row][col] == OBSTACLE}
    
    def cell_index(self, cell: Cell) -> int:
        """
        Returns the index of a cell in a flattened grid.
        Formula for row-major order: index = row * n + col
        """

        row, col = cell
        return row * self.n + col
    
    def index_to_cell(self, index: int) -> Cell:
        """
        Converts a flattened grid index back to a cell (row, col).
        Formula for row-major order: row = index // n, col = index % n
        """

        row = index // self.n
        col = index % self.n
        return (row, col)
    
    def path_highlight(self, path: List[Cell], label: str) -> Grid:
        """Highlights the cells in the given path by marking them as 'label'."""

        # Make a new copy of the original grid to avoid modifying it
        highlighted_grid: Grid = [row.copy() for row in self.grid]

        for cell in path:
            row, col = cell
            if highlighted_grid[row][col] not in (START, END): # Don't overwrite start and end points
                highlighted_grid[row][col] = label

        return highlighted_grid
    
    def merge_paths(self, paths: dict) -> Grid:
        """
        Merges multiple paths into a single grid, highlighting each path with its respective label.

        Parameters:
        paths: dict - A dictionary where keys are labels and values are lists of cells representing the paths to be merged.
        """

        # Start with a copy of the original grid
        merged_grid: Grid = [row.copy() for row in self.grid]

        for label, path in paths.items():
            if path is not None:
                
                # if the path is not None, highlight it on the merged grid
                for cell in path:
                    row, col = cell
                    if merged_grid[row][col] not in (START, END): # Don't overwrite start and end points
                        merged_grid[row][col] = label

        return merged_grid
    
    def __repr__(self) -> str:
        """String representation of the grid for easy visualization."""

        rows = []
        for row in self.grid:
            rows.append(' '.join(cell[0].upper() for cell in row))

        return '\n'.join(rows)
