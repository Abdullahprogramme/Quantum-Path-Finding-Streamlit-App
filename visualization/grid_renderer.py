from typing import List, Optional
from grid.grid_manager import Grid2D, Cell

# Colours for each cell type
CELL_STYLES = {
    'empty': ('white','#e8eaf6'), # background, border
    'obstacle': ('#1a1a2e', '#1a1a2e'),
    'start': ('#00c853', '#00a844'),
    'end': ('#ff1744', '#d50032'),
    'path_bfs': ('#29b6f6', '#039be5'),
    'path_astar': ('#ffca28', '#f9a825'),
    'path_quantum': ('#ce93d8', '#ab47bc')
}

# Labels for each cell type (can be empty for no text)
CELL_LABELS = {
    'start': 'S',
    'end': 'E'
}

LEGEND = {
    'Start': '#00c853',
    'End': '#ff1744',
    'Obstacle': '#1a1a2e',
    'BFS Path': '#29b6f6',
    'A* Path': '#ffca28',
    "Grover's Path": '#ce93d8'
}

def render_grid(grid: Grid2D, cell_size: int = 32) -> str:
    """
    Convert a Grid2D to an HTML table string.

    Parameters:
    grid: 2D list of cell types (e.g. 'empty', 'obstacle', 'start', 'end', 'path_bfs', etc.)
    cell_size: int - pixel size per cell (auto-scaled based on N in app.py)

    Returns:
    str — full HTML string ready for st.markdown(html, unsafe_allow_html = True)
    """

    n = len(grid)

    # CSS
    css = f"""
    <style>
      .qnav-grid {{
        border-collapse: collapse;
        margin: 0 auto;
        font-family: 'Courier New', monospace;
      }}
      .qnav-grid td {{
        width:  {cell_size}px;
        height: {cell_size}px;
        text-align: center;
        vertical-align: middle;
        font-size: {max(8, cell_size // 3)}px;
        font-weight: bold;
        border: 1px solid #c5cae9;
        transition: background-color 0.3s ease;
      }}
    </style>
    """

    # Table rows
    rows_html = []
    for row in grid:
        cells_html = []

        for cell_type in row:
            bg, border = CELL_STYLES.get(cell_type, ('#ffffff', '#e8eaf6'))
            label = CELL_LABELS.get(cell_type, '')
            text_color = '#ffffff' if cell_type in ('obstacle', 'end', 'start') else '#1a1a2e'
            cells_html.append(
                f'<td style="background:{bg}; border-color:{border}; color:{text_color};">'
                f'{label}</td>'
            )

        rows_html.append('<tr>' + ''.join(cells_html) + '</tr>')

    table_html = (
        f'<table class="qnav-grid">'
        + ''.join(rows_html)
        + '</table>'
    )

    return css + table_html


def render_legend() -> str:
    """
    Return a small horizontal legend showing what each colour means.
    Rendered below the grid in the main panel.
    """

    items = []
    for label, color in LEGEND.items():
        text_col = '#ffffff' if label in ('End', 'Obstacle') else '#1a1a2e'

        items.append(
            f'<span style="'
            f'background:{color}; color:{text_col}; '
            f'padding:3px 10px; border-radius:4px; '
            f'margin:3px; font-size:12px; font-weight:bold; '
            f'display:inline-block;">'
            f'{label}</span>'
        )

    return '<div style="text-align:center; margin:8px 0;">' + ''.join(items) + '</div>'

def compute_cell_size(n: int, max_width: int = 680) -> int:
    """
    Compute the per-cell pixel size so the grid fits within max_width.
    Clamps between 14px (very small for large grids) and 48px.

    Parameters:
    n: int - grid dimension (N x N)
    max_width: int - maximum pixel width for the entire grid (default 680px)
    """
    
    size = max_width // n
    return max(14, min(48, size))
