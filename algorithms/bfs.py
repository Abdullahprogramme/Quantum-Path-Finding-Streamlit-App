import time 
from collections import deque
from typing import List, Optional

from grid.grid_manager import GridManager, Cell

class BFS_Result:
    def __init__(self, path: Optional[List[Cell]], time_taken: float, nodes_explored: int, visited_orders: List[Cell]):
        self.path = path
        self.time_taken = time_taken
        self.nodes_explored = nodes_explored
        self.visited_orders = visited_orders
        self.path_length = len(path) if path else 0

    def found_path(self) -> bool:
        return self.path is not None
    

def bfs(grid_manager: GridManager) -> BFS_Result:
    """
    Performs Breadth-First Search (BFS) on the grid to find the shortest path from start to goal.

    Parameters:
    grid_manager: GridManager - An instance of the GridManager class containing the grid and start/end points.

    Returns:    
    BFS_Result - An object containing the path found, time taken, nodes explored, and visited order.
    """

    # Initialize BFS variables
    start_node = grid_manager.start
    end_node = grid_manager.end

    time_start = time.perf_counter()

    queue: deque[Cell] = deque([start_node])
    visited: List[Cell] = [start_node]
    parent_map: dict[Cell, Optional[Cell]] = {start_node: None}
    nodes_explored = 0

    while queue:
        current_node = queue.popleft()
        nodes_explored += 1

        if current_node == end_node:
            time_end = time.perf_counter()
            path = _reconstruct_path(parent_map, start_node, end_node)
            time_taken = (time_end - time_start) * 1000 # Calculate time taken for BFS in seconds

            return BFS_Result(path, time_taken, nodes_explored, visited)
        
        for neighbor in grid_manager.neighbors_with_order(current_node, ('D', 'R', 'U', 'L')):
            if neighbor not in parent_map: # Not visited
                visited.append(neighbor)
                parent_map[neighbor] = current_node
                queue.append(neighbor)

    # No path found
    time_end = time.perf_counter()
    time_taken = (time_end - time_start) * 1000 # Calculate time taken for BFS in seconds

    return BFS_Result(None, time_taken, nodes_explored, visited)

def _reconstruct_path(parent_map: dict[Cell, Optional[Cell]], start_node: Cell, end_node: Cell) -> List[Cell]:
    """
    Reconstructs the path from start to end using the parent map.

    Parameters:
    parent_map: dict[Cell, Optional[Cell]] - A mapping of each cell to its parent cell in the search tree.

    Returns:
    List[Cell] - The reconstructed path from start to end.
    """

    path = []
    current_node = end_node
    while current_node is not None:
        path.append(current_node)
        current_node = parent_map[current_node]

    path.reverse() # Reverse the path to get it from start to end
    return path
