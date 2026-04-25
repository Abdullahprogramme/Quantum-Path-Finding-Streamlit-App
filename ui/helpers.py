import html
import streamlit as st

from grid.grid_manager import GridManager
from visualization.grid_renderer import CELL_STYLES, CELL_LABELS, compute_cell_size


def init_state() -> None:
    defaults = {
        'grid_manager': None,
        'encoder': None,
        'results_ready': False,
        'bfs_result': None,
        'astar_result': None,
        'grover_result': None,
        'n': 8,
        'obstacle_pct': 0.2,
        'seed': 42,
        'show_circuit': True,
        'show_histogram': True,
        'show_convergence': True,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_theme_table(title: str, columns: list[str], rows: list[list[object]], note: str | None = None) -> None:
    table_html = [
        '<div class="surface-card">',
        f'<div class="section-label">{html.escape(title)}</div>',
        '<div class="theme-table-wrapper">',
        '<table class="theme-table">',
        '<thead><tr>',
    ]

    for column in columns:
        table_html.append(f'<th>{html.escape(str(column))}</th>')

    table_html.append('</tr></thead><tbody>')

    for row in rows:
        table_html.append('<tr>')
        for cell in row:
            table_html.append(f'<td>{html.escape(str(cell))}</td>')
        table_html.append('</tr>')

    table_html.extend(['</tbody></table>', '</div>'])

    if note:
        table_html.append(f'<div class="theme-table-note">{html.escape(note)}</div>')

    table_html.append('</div>')
    st.markdown(''.join(table_html), unsafe_allow_html = True)


def reset_results() -> None:
    st.session_state['results_ready'] = False
    st.session_state['bfs_result'] = None
    st.session_state['astar_result'] = None
    st.session_state['grover_result'] = None


def apply_grid_edit(cell: tuple[int, int]) -> None:
    gm = st.session_state['grid_manager']
    if gm is None:
        return

    tool = st.session_state.get('placement_tool', 'Obstacle')
    changed = False
    message = None

    if tool == 'Start':
        changed = gm.set_start(cell)
        message = 'Start node moved.' if changed else 'Start and end cannot occupy the same cell.'
    elif tool == 'End':
        changed = gm.set_end(cell)
        message = 'End node moved.' if changed else 'Start and end cannot occupy the same cell.'
    elif tool == 'Obstacle':
        changed = gm.set_obstacle(cell)
        if not changed and cell not in (gm.start, gm.end):
            message = 'Obstacle limit reached for the current density.'
    elif tool == 'Erase':
        if cell == gm.start:
            message = 'Move the start node with the Start tool.'
        elif cell == gm.end:
            message = 'Move the end node with the End tool.'
        else:
            changed = gm.remove_obstacle(cell)
            if not changed:
                gm.set_cell_value(cell, 'empty')
                changed = True
            message = 'Cell cleared.'

    if changed:
        reset_results()
        st.session_state['grid_manager'] = gm
        st.session_state['editor_status'] = message or 'Grid updated.'
    elif message:
        st.session_state['editor_status'] = message


def render_grid_editor(gm: GridManager) -> None:
    cell_size = compute_cell_size(gm.n)
    font_size = max(10, cell_size // 3)
    target_cell_width = cell_size + 12
    target_grid_width = gm.n * target_cell_width + (gm.n - 1)
    assumed_page_width = 1200
    side_weight = max(1.0, (assumed_page_width - target_grid_width) / 2)
    center_weight = max(320.0, target_grid_width)

    st.markdown('<div class="section-label">Grid Editor</div>', unsafe_allow_html = True)
    css_chunks = [
        f"""
<style>
div[data-testid="stHorizontalBlock"] div.stButton > button {{
    width: 100%;
    height: {cell_size}px;
    min-height: {cell_size}px;
    max-height: {cell_size}px;
    padding: 0;
    margin-top: 0 !important;
    border-radius: 10px;
    border: none;
    background: #2a3142;
    color: #e2e8f0;
    font-size: {font_size}px;
    font-weight: 800;
    letter-spacing: 0.02em;
    line-height: 1;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 8px 16px rgba(0,0,0,0.18);
    transition: transform 0.16s ease, box-shadow 0.16s ease, filter 0.16s ease;
}}
div[data-testid="stHorizontalBlock"] div.stButton > button:hover {{
    transform: translateY(-1px) scale(1.01);
    filter: brightness(1.05);
}}

div[data-testid="stHorizontalBlock"] div[data-testid="column"] {{
    padding-left: 0.5px !important;
    padding-right: 0.5px !important;
}}

div[data-testid="stHorizontalBlock"] {{
    gap: 1px !important;
    margin-bottom: 1px !important;
}}

div[data-testid="stVerticalBlock"] > div.element-container:has(> div[data-testid="stHorizontalBlock"]) {{
    margin-bottom: 1px !important;
    padding-top: 0 !important;
    padding-bottom: 0 !important;
}}

div[data-testid="stHorizontalBlock"] div.stButton {{
    margin: 0 !important;
    padding: 0 !important;
}}

div[data-testid="stHorizontalBlock"] div.element-container {{
    margin: 0 !important;
    padding: 0 !important;
}}
</style>
        """
    ]

    st.markdown(
        f"""
<div class="surface-card" style="margin-bottom: 1rem;">
  <div style="display:flex; flex-wrap:wrap; gap:0.7rem; justify-content:space-between; align-items:center;">
    <div>
      <div style="font-weight:800; font-size:1rem;">Click a cell to place the selected tool</div>
      <div style="color: var(--muted); font-size:0.9rem; margin-top:0.2rem;">
        Start and end are free to move. Obstacles are capped at {gm.max_obstacles()} cells for the current density.
      </div>
    </div>
    <div class="hero-pill"><strong>i</strong> Current tool: {st.session_state.get('placement_tool', 'Obstacle')}</div>
  </div>
</div>
""",
        unsafe_allow_html = True,
    )

    outer_cols = st.columns([side_weight, center_weight, side_weight], gap = "small")
    with outer_cols[1]:
        for row_index in range(gm.n):
            row_columns = st.columns(gm.n, gap = "small")
            for col_index in range(gm.n):
                cell = (row_index, col_index)
                cell_type = gm.get_cell_value(cell)
                bg, border = CELL_STYLES.get(cell_type, ('#2a3142', '#46516a'))
                text_color = '#ffffff' if cell_type in ('obstacle', 'end', 'start') else '#e2e8f0'
                label = CELL_LABELS.get(cell_type, '')

                css_chunks.append(
                    f"""
<style>
div[data-testid="stHorizontalBlock"]:nth-last-of-type({gm.n - row_index}) div[data-testid="column"]:nth-of-type({col_index + 1}) div.stButton > button {{
    background: {bg} !important;
    border-color: {border} !important;
    color: {text_color} !important;
}}
</style>
                    """
                )

                with row_columns[col_index]:
                    if st.button(
                        label,
                        key = f'grid_cell_{row_index}_{col_index}',
                        use_container_width = True,
                    ):
                        apply_grid_edit(cell)
                        st.rerun()

    st.markdown(''.join(css_chunks), unsafe_allow_html = True)

    status = st.session_state.get('editor_status')
    if status:
        st.markdown(f'<div class="warn-box">{status}</div>', unsafe_allow_html = True)
