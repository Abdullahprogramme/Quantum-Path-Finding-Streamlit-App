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
