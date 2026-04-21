from dataclasses import dataclass, field
from typing import Optional, List
from grid.grid_manager import Cell

import emoji
import math
import sympy as sp


@dataclass
class AlgorithmMetrics:
    """
    Performance metrics for an algorithm run, used for both reporting and comparison.

    Variables:
    name: str - Name of the algorithm (e.g. 'BFS', 'A*', "Grover's")
    time_ms: float - Execution time in milliseconds
    path_length: int - Number of cells in the solution path (0 if none)
    nodes_explored: int - How many cells/states were examined
    path_found: bool - True if a valid path was returned
    path: List[Cell] - The actual list of cells (for grid rendering)
    extra_info: dict - Algorithm-specific notes (e.g. qubit count for Grover)
    """

    name: str
    time: float = 0.0
    path_length: int = 0
    nodes_explored: int = 0
    path_found: bool = False
    path: Optional[List[Cell]] = field(default = None, repr = False)
    extra_info: dict = field(default_factory = dict)

    # Derived properties for reporting

    @property
    def efficiency_ratio(self) -> Optional[float]:
        """
        Efficiency = path_length / nodes_explored.
        A higher ratio means fewer "wasted" explorations.
        """

        if self.nodes_explored == 0:
            return None
        
        return round(self.path_length / self.nodes_explored, 4)

    @property
    def time_str(self) -> str:
        """
        Format time:
            - <1 ms: show in microseconds (µs)
            - 1 ms to 1000 ms: show in milliseconds (ms)
            - >1000 ms: show in seconds (s)
        """

        if self.time < 1:
            return f"{self.time * 1000:.1f} µs"
        elif self.time < 1000:
            return f"{self.time:.2f} ms"
        else:
            return f"{self.time / 1000:.2f} s"

    @property
    def status_str(self) -> str:
        return emoji.emojize(":check_mark: Found") if self.path_found else emoji.emojize(":cross_mark: No Path")



def metrics_from_bfs(result) -> AlgorithmMetrics:
    """Convert a BFSResult into AlgorithmMetrics."""

    return AlgorithmMetrics(
        name = "BFS",
        time = result.time_taken,
        path_length = result.path_length,
        nodes_explored = result.nodes_explored,
        path_found = result.found_path(),
        path = result.path,
        extra_info = {
            "Type": "Uninformed Search",
            "Frontier": "FIFO Queue",
            "Heuristic": "None",
            "Optimal": "Yes (fewest hops)",
        }
    )


def metrics_from_astar(result) -> AlgorithmMetrics:
    """Convert an AStarResult into AlgorithmMetrics."""

    return AlgorithmMetrics(
        name = "A*",
        time = result.time_taken,
        path_length = result.path_length,
        nodes_explored = result.nodes_explored,
        path_found = result.found_path(),
        path = result.path,
        extra_info = {
            "Type": "Informed Search",
            "Frontier": "Min-Heap (f = g + h)",
            "Heuristic": "Manhattan Distance",
            "Optimal": "Yes (admissible heuristic)",
        }
    )


def metrics_from_grover(result) -> AlgorithmMetrics:
    """Convert a GroverResult into AlgorithmMetrics."""

    return AlgorithmMetrics(
        name = "Grover's",
        time = result.time_taken,
        path_length = result.path_length,
        nodes_explored = result.nodes_explored,
        path_found = result.found(),
        path = result.path,
        extra_info = {
            "Type": "Quantum Search",
            "Qubits": result.num_qubits,
            "Iterations": result.num_iterations,
            "Oracle calls": result.num_iterations,
            "Speedup": "O(√N) vs O(N) classical",
            "Found state": result.found_state or "N/A",
        }
    )

def build_comparison_table(metrics_list: List[AlgorithmMetrics]) -> List[dict]:
    """
    Build a list of dicts suitable for rendering in st.dataframe.

    Each dict represents one row (one algorithm).
    """

    rows = []
    for m in metrics_list:
        rows.append({
            "Algorithm": m.name,
            "Status": m.status_str,
            "Time": m.time_str,
            "Path Length": m.path_length if m.path_found else "-",
            "Nodes Explored": m.nodes_explored,
            "Efficiency": m.efficiency_ratio if m.efficiency_ratio else "-",
        })

    return rows


def complexity_note(n: int) -> dict:
    """
    Return theoretical complexity strings for an N x N grid.
    """

    total = math.pow(n, 2)
    return {
        "Grid size": f"{n} x {n} = {total} cells",
        "BFS (worst case)": f"O({total}) = O(N²)",
        "A* (with heuristic)": f"O({total} x log {total}) typically much less",
        "Grover's": f"O(√{total}) = O(√(N²)) = O(N) oracle calls",
        "Quantum speedup": f"√{total} ≈ {int(math.pow(total, 0.5))} oracle calls vs {total} classical",
    }

    # N = sp.Symbol('N')

    # total = math.pow(n, 2)

    # return {
    #     "Grid size": sp.latex(N**2),
    #     "BFS (worst case)": sp.latex(sp.O(N**2)),
    #     "A* (with heuristic)": sp.latex(sp.O(N**2 * sp.log(N**2))),
    #     "Grover's": sp.latex(sp.O(sp.sqrt(N**2))),
    #     "Quantum speedup": sp.latex(sp.sqrt(N**2))
    # }
    
