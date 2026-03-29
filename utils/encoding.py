# Grid which is N x N can be represented by N qubits as they produce 2^N states. 
# For example, a 2x2 grid can be represented by 2 qubits as they produce 4 states: |00>, |01>, |10>, |11>.

# Each cell is represented by a binary string such as:
# 4 x 4 grid: 
# (0, 0) -> index 0 -> |0000>
# (0, 1) -> index 1 -> |0001>   
# (3, 3) -> index 15 -> |1111>

import math
from typing import List, Optional
from grid.grid_manager import GridManager, Cell

class Encoder:
    def __init__(self, grid_manager: GridManager):
        self.grid = grid_manager
        self.n = grid_manager.size

        total_cells = grid_manager.total_cells()

        self.num_qubits = max( 1, math.ceil(math.log2(total_cells)) ) # Number of qubits needed to represent all cells
        self.num_states = 2 ** self.num_qubits # Total states that can be represented by the qubits

    def cell_to_binary(self, cell: Cell) -> str:
        """
        Encodes a cell (row, column) into its corresponding binary string representation.

        Parameters:
        cell: Cell - The cell to be encoded (row, column)

        Returns:
        str - The binary string representation of the cell
        """
        
        index = self.grid.cell_index(cell) # Get the index of the cell in row-major order
        binary_str = format(index, f'0{self.num_qubits}b') # Convert index to binary with leading zeros

        return binary_str
    
    def binary_to_cell(self, binary_str: str) -> Optional[Cell]:
        """
        Decodes a binary string back to its corresponding cell (row, column).

        Parameters:
        binary_str: str - The binary string representation of the cell

        Returns:
        Optional[Cell] - The decoded cell (row, column) or None if the binary string is invalid
        """

        try:
            index = int(binary_str, 2) # Convert binary string to integer index

            if index >= self.grid.total_cells():
                return None # Invalid index, out of bounds
            
            return self.grid.index_to_cell(index) # Convert index back to cell (row, column)
        
        except ValueError:
            return None

    def index_to_binary(self, index: int) -> Optional[str]:
        """
        Encodes an index into its corresponding binary string representation.

        Parameters:
        index: int - The index to be encoded

        Returns:
        Optional[str] - The binary string representation of the index or None if the index is invalid
        """

        if index < 0 or index >= self.grid.total_cells():
            return None # Invalid index, out of bounds
        
        binary_str = format(index, f'0{self.num_qubits}b') # Convert index to binary with leading zeros

        return binary_str
    
    def get_num_qubits(self) -> int:
        """
        Returns the number of qubits needed to represent all cells in the grid.

        Returns:
        int - The number of qubits
        """

        return self.num_qubits
    

    def get_num_states(self) -> int:
        """
        Returns the total number of states that can be represented by the qubits.

        Returns:
        int - The total number of states
        """

        return self.num_states
    
    def get_valid_states(self) -> List[str]:
        """
        Returns a list of valid binary string representations for all cells in the grid.

        Returns:
        List[str] - A list of valid binary string representations for all cells
        """

        valid_states = self.grid.get_all_non_obstacle_cells() # Get all non-obstacle cells

        return [self.cell_to_binary(cell) for cell in valid_states] # Convert each cell to its binary representation and return the list
    
    def description(self) -> str:
        """
        Returns a string description of the encoder, including the number of qubits and states.

        Returns:
        str - A description of the encoder
        """

        return (
            f"Grid {self.n}x{self.n} = {self.grid.total_cells()} cells -> "
            f"{self.num_qubits} qubits -> {self.num_states} quantum states "
            f"({self.num_states - self.grid.total_cells()} states unused)"
        )
