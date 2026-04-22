import html
import streamlit as st

from grid.grid_manager import GridManager


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
    st.markdown('<div class="section-label">Grid Editor</div>', unsafe_allow_html = True)
    st.markdown(
        """
<style>
div[data-testid="stButton"] button {
    width: 100%;
    min-height: 30px;
    padding: 0.1rem 0.15rem;
    border-radius: 10px;
    border: 1px solid rgba(148,163,184,0.12);
    background: rgba(42,49,66,0.94);
    color: #e2e8f0;
    font-weight: 800;
    line-height: 1;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 6px 12px rgba(0,0,0,0.14);
}
div[data-testid="stButton"] button:hover {
    border-color: rgba(125,211,252,0.28);
    transform: translateY(-1px);
}

div[data-testid="column"] {
    padding-left: 1px !important;
    padding-right: 1px !important;
}
</style>
        """,
        unsafe_allow_html = True,
    )

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

    for row_index in range(gm.n):
        row_columns = st.columns(gm.n, gap = "small")
        for col_index in range(gm.n):
            cell = (row_index, col_index)
            value = gm.get_cell_value(cell)

            # Map cell types to button labels
            label_map = {
                'empty': '',
                'obstacle': 'O',
                'start': 'S',
                'end': 'E',
            }

            button_label = label_map.get(value, '')
            with row_columns[col_index]:
                if st.button(button_label, key = f'grid_cell_{row_index}_{col_index}', use_container_width = True):
                    apply_grid_edit(cell)
                    st.rerun()

    status = st.session_state.get('editor_status')
    if status:
        st.markdown(f'<div class="warn-box">{status}</div>', unsafe_allow_html = True)
