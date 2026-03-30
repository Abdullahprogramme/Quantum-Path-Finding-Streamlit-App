import time
import math
from typing import Optional, Tuple, List, Dict

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.circuit.library import GroverOperator

from grid.grid_manager import GridManager, Cell
from utils.encoding import Encoder

class GroversSearch:
    def __init__(self, path: Optional[List[Cell]], nodes_explored: int, time_taken: float, num_qubits: int, num_iterations: int, probabilities: Dict[str, float], found_state: Optional[str], circuit_diagram: Optional[object]):
        
        self.path = path # The path found by Grover's algorithm, represented as a list of cells (row, column)
        self.nodes_explored = nodes_explored # The number of nodes explored during the search
        self.time_taken = time_taken # The time taken to execute the search in seconds
        self.num_qubits = num_qubits # The number of qubits used in the quantum circuit for Grover's algorithm
        self.num_iterations = num_iterations # The number of iterations performed in Grover's algorithm
        self.probabilities = probabilities # A dictionary mapping binary strings (representing cells) to their corresponding probabilities of being the solution after measurement
        self.found_state = found_state # The binary string representation of the found state (cell) after measurement, or None if no solution was found
        self.circuit_diagram = circuit_diagram # A visual representation of the quantum circuit used in Grover's algorithm, or None if not available

    def found(self) -> bool:
        """Returns True if a path was found, False otherwise."""

        return self.path is not None
    
