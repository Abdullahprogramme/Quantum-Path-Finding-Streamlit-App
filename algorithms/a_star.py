import time
import heapq
from typing import List, Optional, Dict, Set, Tuple
 
from grid.grid_manager import GridManager, Cell

class AStar_Result:
    def __init__(self, path: Optional[List[Cell]], time_taken: float, nodes_explored: int, visited_orders: List[Cell]):
        self.path = path
        self.time_taken = time_taken
        self.nodes_explored = nodes_explored
        self.visited_orders = visited_orders
        self.path_length = len(path) if path else 0

    def found_path(self) -> bool:
        return self.path is not None
    
def heuristic(a: Cell, b: Cell) -> float:
    """
    Calculates the Manhattan distance heuristic between two cells.

    Parameters:
    a: Cell - The first cell (row, column)
    b: Cell - The second cell (row, column)

    Returns:
    float - The Manhattan distance between the two cells
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star(grid_manager: GridManager) -> AStar_Result:
    """
    Performs A* Search on the grid to find the shortest path from start to goal.

    Parameters:
    grid_manager: GridManager - An instance of the GridManager class containing the grid and start/end points.

    Returns:
    AStar_Result - An object containing the path found, time taken, nodes explored, and visited order.
    """

    # Initialize A* variables
    start = grid_manager.start
    end = grid_manager.end

    time_start = time.perf_counter()

    best_cost: Dict[Cell, float] = {start: 0}
    parent_map: Dict[Cell, Optional[Cell]] = {start: None}
    visited: List[Cell] = []
    closed_set: Set[Cell] = set()

    counter: int = 0 # Counter to break ties in the heap
    h_start = heuristic(start, end)
    heap = List[Tuple] = []
    heapq.heappush(heap, (h_start, counter, start)) # (f_cost, counter, cell) 
    nodes_explored = 0

    while heap:
        f_current, _, current = heapq.heappop(heap)

        # Skip if the current node is in the closed set
        if current in closed_set:
            continue

        visited.append(current)
        nodes_explored += 1
        closed_set.add(current)

        if current == end:
            time_end = time.perf_counter()
            path = _reconstruct_path(parent_map, start, end)
            time_taken = (time_end - time_start) * 1000 # Calculate time taken for A* in seconds

            return AStar_Result(path, time_taken, nodes_explored, visited)
        
        for neighbor in grid_manager.neighbors(current):
            if neighbor in closed_set:
                continue

            tentative_g_cost = best_cost[current] + 1 # Assuming uniform cost for moving to a neighbor

            if neighbor not in best_cost or tentative_g_cost < best_cost[neighbor]:
                best_cost[neighbor] = tentative_g_cost
                parent_map[neighbor] = current

                h_neighbor = heuristic(neighbor, end)
                counter += 1
                heapq.heappush(heap, (tentative_g_cost + h_neighbor, counter, neighbor))

    # No path found
    time_end = time.perf_counter()
    time_taken = (time_end - time_start) * 1000 # Calculate time taken for A* in seconds

    return AStar_Result(None, time_taken, nodes_explored, visited)

def _reconstruct_path(parent_map: Dict[Cell, Optional[Cell]], start: Cell, end: Cell) -> List[Cell]:
    """
    Reconstructs the path from start to end using the parent map.

    Parameters:
    parent_map: Dict[Cell, Optional[Cell]] - A mapping of each cell to its parent cell in the search tree.

    Returns:
    List[Cell] - The reconstructed path from start to end.
    """

    path = []
    current = end
    while current is not None:
        path.append(current)
        current = parent_map[current]

    path.reverse() # Reverse the path to get it from start to end
    return path
