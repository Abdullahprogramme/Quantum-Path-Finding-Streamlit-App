from typing import List, Optional
from grid.grid_manager import Grid2D, Cell

# Colours for each cell type
CELL_STYLES = {
    'empty': ('#2a3142', '#46516a'),
    'obstacle': ('#141927', '#0f172a'),
    'start': ('#60a5fa', '#3b82f6'),
    'end': ('#fb7185', '#e11d48'),
    'path_bfs': ('#7dd3fc', '#0ea5e9'),
    'path_astar': ('#fde68a', '#f59e0b'),
    'path_quantum': ('#d8b4fe', '#a855f7'),
    'path_overlap': ('#fbcfe8', '#ec4899')
}

# Labels for each cell type (can be empty for no text)
CELL_LABELS = {
    'start': 'S',
    'end': 'E'
}

LEGEND = {
    'Start': '#60a5fa',
    'End': '#fb7185',
    'Obstacle': '#141927',
    'BFS Path': '#7dd3fc',
    'A* Path': '#fde68a',
    "Grover's Path": '#d8b4fe',
    'Path Overlap': '#fbcfe8'
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
            border-collapse: separate;
            border-spacing: 1px;
            margin: 0 auto;
            font-family: 'Inter', sans-serif;
        }}
        .qnav-grid td {{
            width: {cell_size}px;
            height: {cell_size}px;
            text-align: center;
            vertical-align: middle;
            font-size: {max(10, cell_size // 3)}px;
            font-weight: 800;
            letter-spacing: 0.02em;
            border: none;
            border-radius: 10px;
            transition: transform 0.16s ease, box-shadow 0.16s ease, filter 0.16s ease;
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 8px 16px rgba(0,0,0,0.18);
        }}
        .qnav-grid td:hover {{
            transform: translateY(-1px) scale(1.01);
            filter: brightness(1.05);
        }}
    </style>
    """

    # Table rows
    rows_html = []
    for row in grid:
        cells_html = []

        for cell_type in row:
            bg, border = CELL_STYLES.get(cell_type, ('rgba(255,255,255,0.04)', 'rgba(148,163,184,0.16)'))
            label = CELL_LABELS.get(cell_type, '')
            text_color = '#ffffff' if cell_type in ('obstacle', 'end', 'start') else '#e2e8f0'
            extra_style = ''
            if cell_type.startswith('path_'):
                extra_style = 'box-shadow: inset 0 1px 0 rgba(255,255,255,0.18), 0 0 0 2px rgba(255,255,255,0.08), 0 0 18px rgba(124,156,255,0.28); font-weight: 900;'
            cells_html.append(
                f'<td style="background:{bg}; border-color:{border}; color:{text_color}; {extra_style}">'
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
        text_col = '#ffffff' if label in ('End', 'Obstacle') else '#08111f'

        items.append(
            f'<span style="'
            f'background:{color}; color:{text_col}; '
            f'padding:7px 12px; border-radius:999px; '
            f'margin:4px; font-size:12px; font-weight:800; '
            f'border: 1px solid rgba(255,255,255,0.14); '
            f'display:inline-flex; align-items:center; gap:6px; '
            f'box-shadow: 0 10px 20px rgba(0,0,0,0.16);">'
            f'{label}</span>'
        )

    return '<div style="text-align:center; margin:10px 0 4px;">' + ''.join(items) + '</div>'

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
