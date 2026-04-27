import time
import math
from typing import Optional, Tuple, List, Dict
from collections import deque
import numpy as np

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.circuit.library import GroverOperator

from grid.grid_manager import GridManager, Cell
from utils.encoding import Encoder

class GroversSearch:
    def __init__(self, path: Optional[List[Cell]], nodes_explored: int, time_taken: float, num_qubits: int, num_iterations: int, probabilities: Dict[str, float], found_state: Optional[str], circuit_diagram: Optional[object]):
        
        self.path = path # The path found by Grover's algorithm, represented as a list of cells (row, column)
        self.path_length = len(path) if path else 0 # Keep parity with BFS/A* result objects
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
    
    def _oracle_builder(num_qubits: int, target_state: str) -> QuantumCircuit:
        """
        Builds the oracle for Grover's algorithm that marks the target state.

        How it works:
        1. Apply X gates to the qubits corresponding to '0' bits in the target state to flip them (X gate).
        2. Apply a multi-controlled Z (phase flip) gate.
        3. Apply X gates again to revert the qubits back to their original state.

        Parameters:
        num_qubits: int - The total number of qubits in the circuit
        target_state: str - The binary string representation of the target state (cell) to be marked by the oracle

        Returns:
        QuantumCircuit - The constructed oracle as a quantum circuit
        """
        
        oracle = QuantumCircuit(num_qubits, name='Oracle')

        for i, bit in enumerate(reversed(target_state)):
            if bit == '0':
                oracle.x(i) # Flip qubits corresponding to '0' bits in the target state

        # Apply multi-controlled Z gate to all qubits to mark the target state
        if num_qubits == 1:
            oracle.z(0) # For 1 qubit, just apply Z gate to the single qubit
        else:
            oracle.h(num_qubits - 1) # Prepare the last qubit for multi-controlled Z
            oracle.mcx( list( range(num_qubits - 1) ), num_qubits - 1 ) # Multi-controlled (Z) gate
            oracle.h(num_qubits - 1) # Revert the last qubit back

        for i, bit in enumerate(reversed(target_state)):
            if bit == '0':
                oracle.x(i) # Revert the qubits back to their original state

        return oracle

    def _diffusion_operator(num_qubits: int) -> QuantumCircuit:
        """
        The diffusion operator reflects the state about the average amplitude, amplifying the probability of the marked state.

        Parameters:
        num_qubits: int - The total number of qubits in the circuit

        Returns:
        QuantumCircuit - The constructed diffusion operator as a quantum circuit
        """

        diffusion = QuantumCircuit(num_qubits, name='Diffusion')

        # Apply Hadamard gates to all qubits
        diffusion.h(range(num_qubits))

        # Apply X gates to all qubits
        diffusion.x(range(num_qubits))

        # Apply multi-controlled Z gate to all qubits to reflect about the average
        if num_qubits == 1:
            diffusion.z(0) # For 1 qubit, just apply Z gate to the single qubit
        else:
            diffusion.h(num_qubits - 1) # Prepare the last qubit for multi-controlled Z
            diffusion.mcx( list( range(num_qubits - 1) ), num_qubits - 1 ) # Multi-controlled (Z) gate
            diffusion.h(num_qubits - 1) # Revert the last qubit back

        # Apply X gates to all qubits again
        diffusion.x(range(num_qubits))

        # Apply Hadamard gates to all qubits again
        diffusion.h(range(num_qubits))

        return diffusion
    
    def _bfs_path(grid_manager: GridManager, start: Cell, target: Cell) -> Optional[List[Cell]]:
        """
        A mimimal implementation of a breadth-first search (BFS) for path reconstruction.
        This is used after grover's algorithm finds the target state to reconstruct the path from start to target.

        Parameters:
        grid_manager: GridManager - The grid manager that provides access to the grid and its properties
        start: Cell - The starting cell (row, column) in the grid
        target: Cell - The target cell (row, column) in the grid

        Returns:
        Optional[List[Cell]] - The path from start to target as a list of cells, or None if no path exists
        """

        queue = deque([start]) # Initialize the queue with the starting cell
        parent_map = {start: None} # Map to keep track of the parent of each cell for path reconstruction

        while queue:
            current = queue.popleft() # Get the next cell from the queue

            if current == target:

                # If we have reached the target, reconstruct the path
                path = []
                while current is not None:
                    path.append(current) # Add the current cell to the path
                    current = parent_map[current] # Move to the parent cell

                path.reverse() # Reverse the path to get it from start to target
                return path

            for neighbor in grid_manager.neighbors_with_order(current, ('U', 'L', 'D', 'R')):
                if neighbor not in parent_map: # If the neighbor has not been visited
                    parent_map[neighbor] = current # Set the parent of the neighbor to the current cell
                    queue.append(neighbor) # Add the neighbor to the queue for further exploration

        return None # Return None if no path exists from start to target
    
def grovers_search(grid_manager: GridManager, encoder: Encoder) -> GroversSearch:
    """
    Executes Grover's search algorithm to find a path from the start cell to the target cell in the grid.

    The steps are as follows:
    1. Determine the number of qubits needed to represent all cells in the grid.
    2. Encode the target cell as a binary string to be used in the oracle.
    3. Build the oracle that marks the target state.
    The oracle is |0> -> Hadamard -> [oracle + diffusion] x K -> Measure
    4. Simulate the quantum circuit and measure the output to find the most likely state (cell).
    5. Extract the probabilities of each state from the simulation results.
    6. Decode the highest probability state back to a cell.
    7. Reconstruct the path from the start cell to the target cell using a breadth-first search (BFS) for path reconstruction.
    

    Parameters:
    grid_manager: GridManager - The grid manager that provides access to the grid and its properties
    encoder: Encoder - The encoder that converts cells to binary strings and vice versa

    Returns:
    GroversSearch - An object containing the results of the search, including the path found, nodes explored, time taken, and other relevant information
    """

    start = grid_manager.start
    target = grid_manager.end

    time_start = time.time() # Start the timer to measure execution time

    # Step 1: Determine the number of qubits needed to represent all cells in the grid
    num_cells = grid_manager.total_cells()
    num_qubits = max( 1, math.ceil(math.log2(num_cells)) ) # Calculate the number of qubits needed, ensuring at least 1 qubit
    num_states = 2 ** num_qubits # Total number of states that can be represented with the given number of qubits

    # Step 2: Encode the target cell as a binary string to be used in the oracle
    target_index = grid_manager.cell_index(target) # Get the index of the target cell in the grid
    target_state = format(target_index, f'0{num_qubits}b') # Convert the target index to a binary string with leading zeros

    # Step 3: Build the oracle that marks the target state
    number_of_iterations = max( 1, math.ceil(math.pi / 4 * math.sqrt(num_states)) )# Calculate the optimal number of iterations for Grover's algorithm

    # Build the quantum circuit for Grover's algorithm
    qr = QuantumRegister(num_qubits, name='q') # Create a quantum register with the required number of qubits
    cr = ClassicalRegister(num_qubits, name='c') # Create a classical register for measurement
    circuit = QuantumCircuit(qr, cr) # Create a quantum circuit with the quantum and

    circuit.h(range(num_qubits)) # Apply Hadamard gates to all qubits to create a superposition of all states
    circuit.barrier() # Add a barrier for better visualization  

    # Build the oracle and diffusion operator
    oracle = GroversSearch._oracle_builder(num_qubits, target_state) # Build the oracle to mark the target state
    diffusion = GroversSearch._diffusion_operator(num_qubits) # Build the diffusion operator to amplify the marked state

    for iter in range(number_of_iterations):
        circuit.compose(oracle, qubits = range(num_qubits), inplace = True) # Inline oracle instructions for Aer compatibility
        circuit.compose(diffusion, qubits = range(num_qubits), inplace = True) # Inline diffusion instructions for Aer compatibility

        if iter < number_of_iterations - 1:
            circuit.barrier() # Add a barrier between iterations for better visualization
    
    circuit.barrier() # Add a barrier before measurement
    circuit.measure(qr, cr) # Measure the quantum register into the classical register

    circuit_diagram = circuit.copy() # Copy the circuit for visualization purposes

    # Step 5: Simulate the quantum circuit and measure the output to find the most likely state (cell)
    
    qc_no_measure = QuantumCircuit(num_qubits) # Create a copy of the circuit without measurement for statevector simulation
    qc_no_measure.h(range(num_qubits)) # Apply Hadamard gates to all qubits
    for iter in range(number_of_iterations):
        qc_no_measure.compose(oracle, qubits = range(num_qubits), inplace = True) # Inline oracle instructions for Aer compatibility
        qc_no_measure.compose(diffusion, qubits = range(num_qubits), inplace = True) # Inline diffusion instructions for Aer compatibility

    simulator = AerSimulator(method='statevector') # Use the statevector simulator to get the final state of the quantum circuit
    qc_simulator = qc_no_measure.copy() # Copy the circuit without measurement for simulation
    qc_simulator.save_statevector() # Save the statevector at the end of the circuit

    sv_job = simulator.run(qc_simulator)
    sv_result = sv_job.result()
    state_vector = np.asarray(sv_result.get_statevector(qc_simulator)) # Get the final statevector from the simulation

    # Compute probabilities for all basis states
    probabilities: Dict[str, float] = {}
    for idx in range(num_states):
        basis_string = format(idx, f'0{num_qubits}b')
        probabilities[basis_string] = float(abs(state_vector[idx]) ** 2) # Calculate the probability of each basis state from the statevector
 
    # Run measurement circuit to get the most likely outcome
    shot_simulator = AerSimulator().run(circuit, shots = 1024)
    counts = shot_simulator.result().get_counts(circuit)

    found_state = max(counts, key = counts.get) # Get the state with the highest count (most likely state)
    found_index = int(found_state, 2) # Convert the found state from binary string to integer index

    # Step 6: Decode the highest probability state back to a cell

    if found_index < num_cells:
        decoded_cell = grid_manager.index_to_cell(found_index)

        if grid_manager.is_not_obstacle(decoded_cell):
            quantum_goal = decoded_cell
        else:
            quantum_goal = target # fallback to actual target if decode lands on obstacle
    else:
        quantum_goal = target # fallback if index out of range

    # Step 7: Reconstruct the path from the start cell to the target cell using a breadth-first search (BFS) for path reconstruction

    path = GroversSearch._bfs_path(grid_manager, start, quantum_goal)
    nodes_explored = number_of_iterations

    time_end = time.time() # End the timer
    time_taken = time_end - time_start # Calculate the total time taken for the search

    return GroversSearch(
        path = path,
        nodes_explored = nodes_explored,
        time_taken = time_taken,
        num_qubits = num_qubits,
        num_iterations = number_of_iterations,
        probabilities = probabilities,
        found_state = found_state,
        circuit_diagram = circuit_diagram
    )

def convergence(num_qubits: int, target_state: str) -> List[Tuple[int, float]]:
    """
    Analyzes the convergence of Grover's algorithm by calculating the probability of finding the target state after each iteration.

    Parameters:
    num_qubits: int - The total number of qubits in the circuit
    target_state: str - The binary string representation of the target state (cell) to be marked by the oracle

    Returns:
    List[Tuple[int, float]] - A list of tuples where each tuple contains the iteration number and the corresponding probability of finding the target state
    """

    num_states = 2 ** num_qubits # Total number of states that can be represented with the given number of qubits
    max_iter = max( 1, math.floor(math.pi / 4 * math.sqrt(num_states)) ) + 3 # Calculate the optimal number of iterations for Grover's algorithm

    oracle = GroversSearch._oracle_builder(num_qubits, target_state) # Build the oracle to mark the target state
    diffusion = GroversSearch._diffusion_operator(num_qubits) # Build the diffusion operator to amplify the marked state
    simulator = AerSimulator(method ='statevector') # Use the statevector simulator to get the final state of the quantum circuit

    convergence = [] # List to store the convergence data (iteration number and probability)

    for iter in range(0, max_iter + 1):
        circuit = QuantumCircuit(num_qubits) # Create a new quantum circuit for each iteration
        circuit.h(range(num_qubits)) # Apply Hadamard gates to all qubits to create a superposition of all states

        for _ in range(iter):
            circuit.compose(oracle, qubits = range(num_qubits), inplace = True) # Inline oracle instructions for Aer compatibility
            circuit.compose(diffusion, qubits = range(num_qubits), inplace = True) # Inline diffusion instructions for Aer compatibility
        circuit.save_statevector() # Save the statevector at the end of the circuit

        sv_job = simulator.run(circuit)
        sv = np.asarray(sv_job.result().get_statevector(circuit)) # Get the final statevector from the simulation
        target_index = int(target_state, 2) # Convert the target state from binary string to integer index
        probability = float(abs(sv[target_index]) ** 2) # Calculate the probability of finding the target state from the statevector

        convergence.append((iter, probability)) # Append the iteration number and probability to the convergence list

    return convergence
