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
Grid2D = List[List[str]] # A grid is a 2D list of strings representing the cell types

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
        self.grid: Grid2D = self._create_grid(n)

        # Place the start and end points
        self.start: Cell = (0, 0)
        self.end: Cell = (n - 1, n - 1)
        self.set_start(self.start)
        self.set_end(self.end)

        # Place the obstacles
        self._place_obstacles(obstacle_percentage, random_seed)

    @staticmethod
    def _create_grid(n: int) -> Grid2D:
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

            if self.set_obstacle(cell, max_obstacles = num_obstacles):
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
            (row, col + 1) # Right
        ]

        valid_neighbors = []
        for r, c in potential_neighbors:
            if 0 <= r < self.n and 0 <= c < self.n and self.grid[r][c] != OBSTACLE:
                valid_neighbors.append((r, c))

        return valid_neighbors

    def neighbors_with_order(self, cell: Cell, order: Tuple[str, str, str, str]) -> List[Cell]:
        """Returns valid neighbors using a caller-provided direction order."""

        row, col = cell
        deltas = {
            'U': (-1, 0),
            'D': (1, 0),
            'L': (0, -1),
            'R': (0, 1),
        }

        valid_neighbors: List[Cell] = []
        for direction in order:
            if direction not in deltas:
                continue

            dr, dc = deltas[direction]
            nr, nc = row + dr, col + dc
            if 0 <= nr < self.n and 0 <= nc < self.n and self.grid[nr][nc] != OBSTACLE:
                valid_neighbors.append((nr, nc))

        return valid_neighbors

    def apply_diverse_pattern(self) -> None:
        """Builds a structured obstacle pattern that encourages multiple valid routes."""

        # Reset to a clean board except start/end.
        for row in range(self.n):
            for col in range(self.n):
                cell = (row, col)
                if cell not in (self.start, self.end):
                    self.set_cell_value(cell, EMPTY)

        cap = self.max_obstacles()
        if cap <= 0:
            return

        pattern_cells: List[Cell] = []

        # Symmetric center block creates alternative shortest detours around it.
        mid = self.n // 2
        center_cells = {
            (mid - 1, mid - 1),
            (mid - 1, mid),
            (mid, mid - 1),
            (mid, mid),
        }
        
        for cell in center_cells:
            r, c = cell
            if 0 <= r < self.n and 0 <= c < self.n and cell not in (self.start, self.end):
                pattern_cells.append(cell)

        # Add two symmetric side pillars with two gates to preserve multiple route choices.
        left_col = max(1, self.n // 3)
        right_col = min(self.n - 2, (2 * self.n) // 3)
        gate_rows = {max(1, self.n // 3), min(self.n - 2, (2 * self.n) // 3)}

        for row in range(1, self.n - 1):
            if row not in gate_rows:
                for col in (left_col, right_col):
                    cell = (row, col)
                    if cell not in (self.start, self.end):
                        pattern_cells.append(cell)

        # Keep order stable while deduplicating.
        seen: Set[Cell] = set()
        unique_cells: List[Cell] = []
        for cell in pattern_cells:
            if cell not in seen:
                seen.add(cell)
                unique_cells.append(cell)

        placed = 0
        for cell in unique_cells:
            if placed >= cap:
                break
            if self.set_obstacle(cell, max_obstacles = cap):
                placed += 1
    
    def is_not_obstacle(self, cell: Cell) -> bool:
        """Checks if a given cell is not an obstacle."""
        
        row, col = cell
        return self.grid[row][col] != OBSTACLE

    def get_cell_value(self, cell: Cell) -> str:
        """Returns the raw cell value for a given cell."""

        row, col = cell
        return self.grid[row][col]

    def set_cell_value(self, cell: Cell, value: str) -> None:
        """Sets the raw cell value for a given cell."""

        row, col = cell
        self.grid[row][col] = value

    def clear_cell(self, cell: Cell) -> None:
        """Clears a cell unless it is the current start or end."""

        if cell == self.start:
            self.start = (-1, -1)
        if cell == self.end:
            self.end = (-1, -1)
        self.set_cell_value(cell, EMPTY)

    def set_start(self, cell: Cell) -> bool:
        """Moves the start cell to a new position."""

        if cell == self.end:
            return False

        if hasattr(self, 'start') and self.start != (-1, -1):
            self.set_cell_value(self.start, EMPTY)

        self.start = cell
        self.set_cell_value(cell, START)
        return True

    def set_end(self, cell: Cell) -> bool:
        """Moves the end cell to a new position."""

        if cell == self.start:
            return False

        if hasattr(self, 'end') and self.end != (-1, -1):
            self.set_cell_value(self.end, EMPTY)

        self.end = cell
        self.set_cell_value(cell, END)
        return True

    def obstacle_count(self) -> int:
        """Returns the number of obstacle cells."""

        return len(self.get_all_obstacle_cells())

    def max_obstacles(self) -> int:
        """Returns the obstacle cap implied by the configured density."""

        return int(self.total_cells() * self.obstacle_percentage)

    def can_add_obstacle(self, cell: Cell, max_obstacles: int | None = None) -> bool:
        """Checks whether an obstacle can be placed at the specified cell."""

        if cell in (self.start, self.end):
            return False

        if self.grid[cell[0]][cell[1]] == OBSTACLE:
            return True

        limit = self.max_obstacles() if max_obstacles is None else max_obstacles
        return self.obstacle_count() < limit

    def set_obstacle(self, cell: Cell, max_obstacles: int | None = None) -> bool:
        """Places an obstacle if allowed by the obstacle cap."""

        if cell in (self.start, self.end):
            return False

        if self.grid[cell[0]][cell[1]] == OBSTACLE:
            return True

        if not self.can_add_obstacle(cell, max_obstacles = max_obstacles):
            return False

        self.set_cell_value(cell, OBSTACLE)
        return True

    def remove_obstacle(self, cell: Cell) -> bool:
        """Removes an obstacle from a cell."""

        if self.grid[cell[0]][cell[1]] != OBSTACLE:
            return False

        self.set_cell_value(cell, EMPTY)
        return True
    
    def get_all_non_obstacle_cells(self) -> List[Cell]:
        """Returns a set of all cells that are not obstacles."""

        non_obstacle_cells = []
        for row in range(self.n):
            for col in range(self.n):
                if self.grid[row][col] != OBSTACLE:
                    non_obstacle_cells.append((row, col))

        return non_obstacle_cells

    def get_obstacle_cells(self) -> Set[Cell]:
        """Compatibility alias for obstacle cell retrieval."""

        return self.get_all_obstacle_cells()
    
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
    
    def path_highlight(self, path: List[Cell], label: str) -> Grid2D:
        """Highlights the cells in the given path by marking them as 'label'."""

        # Make a new copy of the original grid to avoid modifying it
        highlighted_grid: Grid2D = [row.copy() for row in self.grid]

        for cell in path:
            row, col = cell
            if highlighted_grid[row][col] not in (START, END): # Don't overwrite start and end points
                highlighted_grid[row][col] = label

        return highlighted_grid
    
    def merge_paths(self, paths: dict) -> Grid2D:
        """
        Merges multiple paths into a single grid, highlighting each path with its respective label.

        Parameters:
        paths: dict - A dictionary where keys are labels and values are lists of cells representing the paths to be merged.
        """

        # Start with a copy of the original grid
        merged_grid: Grid2D = [row.copy() for row in self.grid]

        for label, path in paths.items():
            if path is not None:
                
                # if the path is not None, highlight it on the merged grid
                for cell in path:
                    row, col = cell
                    if merged_grid[row][col] in (START, END):
                        continue

                    current = merged_grid[row][col]
                    if current == 'path_overlap':
                        continue

                    if isinstance(current, str) and current.startswith('path_') and current != label:
                        merged_grid[row][col] = 'path_overlap'
                    else:
                        merged_grid[row][col] = label

        return merged_grid
    
    def __repr__(self) -> str:
        """String representation of the grid for easy visualization."""

        rows = []
        for row in self.grid:
            rows.append(' '.join(cell[0].upper() for cell in row))

        return '\n'.join(rows)
