import streamlit as st
import matplotlib
matplotlib.use('Agg')
import emoji
import sympy as sp
import math

from grid.grid_manager import GridManager
from algorithms.bfs import bfs
from algorithms.a_star import a_star
from algorithms.grovers_search import grovers_search, convergence
from utils.encoding import Encoder
from utils.benchmarking import (
    metrics_from_bfs,
    metrics_from_astar,
    metrics_from_grover,
    build_comparison_table,
    complexity_note
)

from visualization.grid_renderer  import (
    render_grid,
    render_legend,
    compute_cell_size
)

from visualization.quantum_plots  import (
    plot_circuit,
    plot_probability_histogram,
    plot_grover_convergence,
    plot_comparison_bars
)

from ui.styles import apply_global_styles
from ui.helpers import (
    init_state,
    reset_results,
    render_grid_editor
)


# Page configuration
st.set_page_config(
    page_title = "Quantum Pathfinding Visualiser",
    page_icon = emoji.emojize(":compass:"),
    layout = "wide",
    initial_sidebar_state = "expanded",
)

apply_global_styles()
init_state()

# Sidebar controls
with st.sidebar:
    st.markdown(emoji.emojize(":compass:") + " Quantum Pathfinding Visualiser")
    st.markdown("*Three Minds, One Maze*")
    st.divider()

    st.markdown(f"Grid Settings")

    n_val = st.slider(
        f"Grid Size ({sp.latex(sp.Symbol('N'))} x {sp.latex(sp.Symbol('N'))})",
        min_value = 4,
        max_value = 16,
        value = st.session_state['n'],
        step = 1,
        help = (
            "N controls the maze size. Larger N = more cells.\n\n" +
            f"WARNING: For the quantum simulation: N > 12 may be slow "
            "because qubit count = ceil(log2(N²))."
        ),
    )

    obs_pct = st.slider(
        "Obstacle Density",
        min_value = 0,
        max_value = 40,
        value = int(st.session_state['obstacle_pct'] * 100),
        step = 5,
        format = "%d%%",
        help = "Percentage of grid cells that become impassable obstacles (CSP hard constraints).",
    )

    grid_layout = st.selectbox(
        "Grid Layout",
        ["Random", "Diverse Paths"],
        index = ["Random", "Diverse Paths"].index(st.session_state.get('grid_layout', 'Random')),
        help = "Diverse Paths places a structured pattern that encourages multiple valid routes.",
    )

    seed_val = st.number_input(
        "Random Seed",
        min_value = 0,
        max_value = 9999,
        value = st.session_state['seed'],
        step = 1,
        help = "Same seed = same obstacle layout. Change to explore different mazes.",
    )

    st.divider()
    st.markdown(f"Visualisation Options")

    show_circuit = st.checkbox("Show Quantum Circuit Diagram", value = st.session_state['show_circuit'])
    show_histogram = st.checkbox("Show Probability Histogram", value = st.session_state['show_histogram'])
    show_convergence = st.checkbox("Show Convergence Plot", value = st.session_state['show_convergence'])

    st.divider()
    st.markdown(f"Grid Placement Mode")
    placement_tool = st.selectbox(
        "Tool",
        ["Start", "End", "Obstacle", "Erase"],
        index = ["Start", "End", "Obstacle", "Erase"].index(st.session_state.get('placement_tool', 'Obstacle')),
        help = "Choose what happens when you click a cell in the grid editor.",
    )
    st.session_state['placement_tool'] = placement_tool

    if st.session_state['grid_manager'] is not None:
        gm_preview = st.session_state['grid_manager']
        obstacle_used = gm_preview.obstacle_count()
        obstacle_cap = gm_preview.max_obstacles()
        st.markdown(
            f"""
<div class="surface-card">
  <b>Placement Limits</b><br>
  <span style="color: var(--muted); font-size: 0.9rem;">Obstacles used: {obstacle_used} / {obstacle_cap}</span><br>
  <span style="color: var(--muted); font-size: 0.9rem;">Start: {gm_preview.start} | End: {gm_preview.end}</span>
</div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Apply Settings button
    if st.button(f"Apply Settings & Build Grid"):
        # Persist settings
        st.session_state['n'] = n_val
        st.session_state['obstacle_pct'] = obs_pct / 100.0
        st.session_state['grid_layout'] = grid_layout
        st.session_state['seed'] = seed_val
        st.session_state['show_circuit'] = show_circuit
        st.session_state['show_histogram'] = show_histogram
        st.session_state['show_convergence'] = show_convergence

        # Build a fresh grid
        gm = GridManager(
            n = n_val,
            obstacle_percentage = obs_pct / 100.0,
            random_seed = seed_val,
        )

        if grid_layout == "Diverse Paths":
            gm.apply_diverse_pattern()

        st.session_state['grid_manager'] = gm
        st.session_state['encoder'] = Encoder(gm)
        reset_results()
        st.success("Grid built! Click **Run Algorithms** to start.")

    # Run Algorithms button
    if st.button(f"Run All Algorithms"):
        if st.session_state['grid_manager'] is None:
            st.warning("Build the grid first using **Apply Settings**.")
        else:
            gm = st.session_state['grid_manager']
            encoder = st.session_state['encoder']

            with st.spinner("Running BFS…"):
                bfs_res = bfs(gm)
                st.session_state['bfs_result'] = bfs_res

            with st.spinner("Running A*…"):
                astar_res = a_star(gm)
                st.session_state['astar_result'] = astar_res

            with st.spinner("Running Grover's (Qiskit simulation — may take a moment)…"):
                grover_res = grovers_search(gm, encoder)
                st.session_state['grover_result'] = grover_res

            st.session_state['results_ready'] = True
            st.success(emoji.emojize(":tada:") + " All algorithms complete! Check the results below.")

            # FROM HERE ONWARDS
    st.divider()

    # Encoding info
    if st.session_state['encoder'] is not None:
        enc = st.session_state['encoder']
        st.markdown("### Quantum Encoding Info")
        st.markdown(f"""
<div class="info-box">
  <b>Grid Cells:</b> {enc.grid.total_cells()}<br>
    <b>Qubits needed:</b> {enc.num_qubits}<br>
    <b>Quantum states:</b> {enc.num_states}<br>
    <b>Unused states:</b> {enc.num_states - enc.grid.total_cells()}<br>
    <b>Optimal iterations:</b> ≈ {max(1, int((math.pi/4) * math.sqrt(enc.num_states)))}
</div>
        """, unsafe_allow_html = True)

    st.divider()
    st.markdown("""
<div style="font-size:11px; color:#7986cb; text-align:center;">
  Introduction to AI - Semester Project<br>
  Quantum Navigator v1.0
</div>
    """, unsafe_allow_html = True)


# =============================
# MAIN PANEL
# =============================

# Header
st.markdown(
        f"""
<div class="hero-shell">
    <div class="hero-eyebrow">{emoji.emojize(":compass:")} Quantum Pathfinding Visualiser</div>
    <div class="hero-grid">
        <div>
            <h1 class="hero-title">Quantum Navigator</h1>
            <p class="hero-copy">
                A sleek search laboratory for comparing BFS, A*, and Grover's algorithm on a single interactive grid.
                Build the maze, run the algorithms, and inspect the tradeoffs in time, path quality, and quantum amplification.
            </p>
        </div>
        <div class="hero-pills">
            <div class="hero-pill"><strong>{emoji.emojize(":blue_circle:")}</strong> BFS</div>
            <div class="hero-pill"><strong>{emoji.emojize(":yellow_circle:")}</strong> A*</div>
            <div class="hero-pill"><strong>{emoji.emojize(":purple_circle:")}</strong> Grover's</div>
        </div>
    </div>
</div>
""",
        unsafe_allow_html=True,
)
st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)


# =============================
# GRID SECTION
# =============================

if st.session_state['grid_manager'] is None:
    # Welcome state (no grid built yet)
    st.markdown('<div class="section-label">Start Here</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="surface-card" style="text-align:center; padding:56px 24px; margin-bottom: 1.2rem;">
    <h3 style="margin-top:0;">Configure and Build the Grid</h3>
    <p style="color: var(--muted); font-size:14px; max-width: 720px; margin: 0.6rem auto 0; line-height: 1.7;">
    Use the sidebar to set grid size, obstacle density, and seed.<br>
    Click <b>Apply Settings & Build Grid</b>, then <b>Run All Algorithms</b>.
  </p>
</div>
    """, unsafe_allow_html = True)

    # Quick explainer cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
<div class="feature-card">
  <b style="color:#5bbcff; font-size: 1rem;">{emoji.emojize(":blue_circle:")} BFS</b><br>
  <i>Uninformed Search</i>
  <p>Explores the maze level by level. Always shortest, but often the most exhaustive.</p>
  <div class="section-label" style="margin-top:0.7rem;">Complexity: O(N²)</div>
</div>
        """, unsafe_allow_html = True)
    with col2:
        st.markdown(f"""
<div class="feature-card">
  <b style="color:#f7c948; font-size: 1rem;">{emoji.emojize(":yellow_circle:")} A*</b><br>
  <i>Informed Search</i>
  <p>Uses a Manhattan heuristic to focus attention on promising directions and avoid waste.</p>
  <div class="section-label" style="margin-top:0.7rem;">Complexity: O(N² log N²)</div>
</div>
        """, unsafe_allow_html = True)
    with col3:
        st.markdown(f"""
<div class="feature-card">
  <b style="color:#d8b4fe; font-size: 1rem;">{emoji.emojize(":purple_circle:")} Grover's</b><br>
  <i>Quantum Search</i>
  <p>Amplitude amplification makes the target state dominate, then the classical path is reconstructed afterward.</p>
  <div class="section-label" style="margin-top:0.7rem;">Complexity: O(√N²) = O(N)</div>
</div>
        """, unsafe_allow_html = True)

else:
    # Grid is ready
    gm = st.session_state['grid_manager']
    n = gm.n
    cell_px = compute_cell_size(n)

    # Determine which grid to render
    if st.session_state['results_ready']:
        bfs_r = st.session_state['bfs_result']
        astar_r = st.session_state['astar_result']
        grover_r = st.session_state['grover_result']

        # Overlay all three paths onto the same grid
        paths = {
            'path_bfs': bfs_r.path if bfs_r and bfs_r.found_path() else None,
            'path_astar': astar_r.path if astar_r and astar_r.found_path() else None,
            'path_quantum': grover_r.path if grover_r and grover_r.found() else None,
        }

        display_grid = gm.merge_paths(paths)

        status_msg = ""
        if bfs_r and not bfs_r.found_path():
            status_msg += f"WARNING -> BFS: No path found.  "
        if astar_r and not astar_r.found_path():
            status_msg += f"WARNING -> A*: No path found.  "
        if grover_r and not grover_r.found():
            status_msg += f"WARNING -> Grover's: No path found."
        if status_msg:
            st.warning(status_msg)
    else:
        render_grid_editor(gm)
        st.divider()
        display_grid = gm.grid

    # Render grid 
    st.markdown('<div class="section-label">Path Map</div>', unsafe_allow_html = True)
    grid_html = render_grid(display_grid, cell_size = cell_px)
    st.markdown(grid_html, unsafe_allow_html = True)

    # Legend
    st.markdown(render_legend(), unsafe_allow_html = True)

    # Grid info line
    enc = st.session_state['encoder']
    st.markdown(
        f"<p style='text-align:center; font-size:12px; color:var(--muted); margin-top: 0.7rem;'>"
        f"Grid: {n}x{n} = {gm.total_cells()} cells &nbsp;|&nbsp; "
        f"Start: {gm.start} &nbsp;|&nbsp; End: {gm.end} &nbsp;|&nbsp; "
        f"Obstacles: {len(gm.get_all_obstacle_cells())} cells &nbsp;|&nbsp; "
        f"Qubits: {enc.num_qubits} -> {enc.num_states} quantum states"
        f"</p>",
        unsafe_allow_html = True,
    )

    st.divider()


# =============================
# RESULTS SECTION
# =============================

if st.session_state['results_ready']:
    bfs_r = st.session_state['bfs_result']
    astar_r = st.session_state['astar_result']
    grover_r = st.session_state['grover_result']
    gm = st.session_state['grid_manager']
    enc = st.session_state['encoder']

    bfs_metrics = metrics_from_bfs(bfs_r)
    astar_metrics = metrics_from_astar(astar_r)
    grover_metrics = metrics_from_grover(grover_r)
    all_metrics = [bfs_metrics, astar_metrics, grover_metrics]

    # Top-level metric cards 
    st.markdown("## Benchmark Results")
    mc1, mc2, mc3 = st.columns(3)
    for col, m, color in zip(
        [mc1, mc2, mc3],
        all_metrics,
        ['#29b6f6', '#ffca28', '#ce93d8'],
    ):
        with col:
            st.markdown(f"<h4 style='color:{color};'>{m.name}</h4>", unsafe_allow_html = True)
            st.metric("Time", m.time_str)
            st.metric("Path Length", m.path_length if m.path_found else "No path")
            st.metric("Nodes Explored", m.nodes_explored)
            st.metric("Status", m.status_str)

    st.divider()

    # Detailed comparison table 
    st.markdown("### Detailed Comparison Table")
    import pandas as pd
    comparison_rows = build_comparison_table(all_metrics)
    df = pd.DataFrame(comparison_rows)
    st.dataframe(df, use_container_width = True, hide_index = True)

    # Theoretical complexity note
    with st.expander(f"Theoretical Complexity Notes"):
        notes = complexity_note(gm.n)
        for k, v in notes.items():
            st.markdown(f"**{k}:** {v}")

        st.markdown("""
---
**Why does Grover's time appear HIGH despite fewer oracle calls?**

The simulation runs on a *classical computer emulating quantum hardware*.
Qiskit's Aer simulator has to compute a full 2^n statevector, which takes
exponential classical time — the opposite of what real quantum hardware does.

On **real quantum hardware**, Grover's √N speedup would be physically realised.
This is just a simulation.
        """)

    # Extra info per algorithm 
    with st.expander(f"Algorithm Details"):
        d1, d2, d3 = st.columns(3)
        for col, m in zip([d1, d2, d3], all_metrics):
            with col:
                st.markdown(f"**{m.name}**")
                for k, v in m.extra_info.items():
                    st.markdown(f"- **{k}:** {v}")

    st.divider()

    # =============================
    # MATPLOTLIB VISUALISATIONS
    # =============================

    st.markdown("## Quantum Visualisations")

    # Comparison bars 
    st.markdown("### Performance Comparison")
    fig_bars = plot_comparison_bars(all_metrics)
    st.pyplot(fig_bars, use_container_width = True)

    # Probability histogram
    if st.session_state['show_histogram']:
        st.markdown("### Quantum State Probability Histogram")
        st.markdown(
            "<div class='info-box'>"
            "<b>Probabilistic Reasoning:</b> After Grover's amplitude amplification, "
            "the target state's probability is dramatically higher than all others. "
            "This is why quantum measurement gives the correct answer with high probability. "
            "Note that the result is <i>probabilistic, not certain</i> — this is fundamental "
            "to quantum computing."
            "</div>",
            unsafe_allow_html = True,
        )
        target_state = format(gm.cell_index(gm.end), f'0{enc.num_qubits}b')
        fig_hist = plot_probability_histogram(
            probabilities = grover_r.probabilities,
            target_state = target_state,
            num_qubits = enc.num_qubits,
            n = gm.n,
        )
        st.pyplot(fig_hist, use_container_width = True)

    # Convergence plot
    if st.session_state['show_convergence']:
        st.markdown("### Grover's Convergence (Amplitude Amplification)")
        st.markdown(
            "<div class='info-box'>"
            "<b>Local Search Analogy:</b> Just like simulated annealing or hill climbing "
            "improves a solution iteratively, Grover's algorithm amplifies the correct "
            "answer's probability with each iteration. The key quantum difference: "
            "it <i>peaks</i> and then <i>decreases</i> — over-iterating hurts performance."
            "</div>",
            unsafe_allow_html = True,
        )

        with st.spinner("Computing convergence curve…"):
            target_state = format(gm.cell_index(gm.end), f'0{enc.num_qubits}b')
            optimal_k = max(1, int((math.pi / 4) * math.sqrt(enc.num_states)))
            convergence_data = convergence(enc.num_qubits, target_state)

        fig_conv = plot_grover_convergence(convergence_data, optimal_k)
        st.pyplot(fig_conv, use_container_width = True)

    # Quantum circuit diagram
    if st.session_state['show_circuit']:
        st.markdown("### Quantum Circuit Diagram")
        st.markdown(
            "<div class='info-box'>"
            "<b>Reading the circuit:</b> Time flows left to right. "
            "Each horizontal line is a qubit. "
            "<code>H</code> = Hadamard (creates superposition). "
            "<code>Oracle</code> = phase-flips the goal state (constraint encoding). "
            "<code>Diffusion</code> = amplifies the goal state amplitude. "
            "The measurement (meter symbol) collapses the quantum state to a classical answer."
            "</div>",
            unsafe_allow_html = True,
        )
        fig_circuit = plot_circuit(grover_r.circuit_diagram)
        if fig_circuit:
            st.pyplot(fig_circuit, use_container_width = True)

    st.divider()

    # AI Topics summary table
    st.markdown("## AI Course Topics Addressed")
    topics_data = {
        "Course Topic": [
            "Introduction & Search Problem",
            "Uninformed Search",
            "Informed Search",
            "Local Search",
            "Adversarial Search",
            "Constraint Satisfaction",
            "Probabilistic Reasoning",
            "Knowledge Representation",
            "Performance Measures",
        ],
        "Implementation": [
            "The entire project is a live search problem on an NxN grid",
            "BFS — explores level-by-level with no heuristic",
            "A* — uses Manhattan distance heuristic",
            "Grover's iterative amplitude amplification (convergence plot)",
            "Obstacles simulate an adversarial environment blocking paths",
            "Obstacles = hard constraints; Oracle encodes them in the quantum circuit",
            "Quantum measurement is probabilistic; histogram visualizes uncertainty",
            "Grid as explicit graph; cells as nodes; edges as valid moves",
            "Time, path length, nodes explored, efficiency ratio compared side-by-side",
        ],
        "Module": [
            "app.py", 
            "algorithms/bfs.py", 
            "algorithms/a_star.py",
            "algorithms/grovers_search.py", 
            "grid/grid_manager.py",
            "algorithms/grovers_search.py + grid/grid_manager.py",
            "visualization/quantum_plots.py", 
            "grid/grid_manager.py",
            "utils/benchmarking.py",
        ]
    }

    st.dataframe(pd.DataFrame(topics_data), use_container_width = True, hide_index = True)
