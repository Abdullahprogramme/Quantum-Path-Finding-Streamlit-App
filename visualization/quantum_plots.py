import math
from typing import Dict, List, Tuple, Optional
 
import numpy as np
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure


# Colour variants defined here
COLORS = {
    'bfs':     '#29b6f6',
    'astar':   '#ffca28',
    'quantum': '#ce93d8',
    'target':  '#ff1744',
    'bg':      '#0f0e17',
    'panel':   '#1a1a2e',
    'text':    '#fffffe',
    'grid':    '#2d2d44',
}

def _dark_theme(ax, fig):
    """Apply a dark theme to the given Matplotlib axis and figure."""

    fig.patch.set_facecolor(COLORS['bg'])
    ax.set_facecolor(COLORS['panel'])
    ax.tick_params(colors = COLORS['text'], labelsize = 9)
    ax.xaxis.label.set_color(COLORS['text'])
    ax.yaxis.label.set_color(COLORS['text'])
    ax.title.set_color(COLORS['text'])

    for spine in ax.spines.values():
        spine.set_edgecolor(COLORS['grid'])


def plot_circuit(Circuit) -> Optional[Figure]:
    """
    Draw the Grover quantum circuit using Qiskit's built-in Matplotlib drawer.
 
    Returns the Matplotlib Figure object (for st.pyplot).
    """

    try:
        figure = Circuit.draw(
            output = 'mpl',
            style = {
                'backgroundcolor': COLORS['bg'],
                'textcolor':       COLORS['text'],
                'gatetextcolor':   '#ffffff',
                'subtextcolor':    '#aaaaaa',
                'linecolor':       '#7986cb',
                'creglinecolor':   '#ce93d8',
                'gatefacecolor':   '#3949ab',
                'barrierfacecolor':'#4a4a6a',
                'fold': 25,
            },
            fold = 25,
        )

        figure.suptitle(
            "Grover's Algorithm — Quantum Circuit",
            color = COLORS['text'],
            fontsize = 12,
            fontweight = 'bold',
        )

        return figure
    
    except Exception as e:
        # If circuit drawing fails, return a fallback text figure

        fig, ax = plt.subplots(figsize = (8, 2))
        ax.text(
            0.5, 0.5,
            f"Circuit diagram unavailable\n({e})",
            ha = 'center', va = 'center',
            transform = ax.transAxes,
            color = COLORS['text'],
        )

        _dark_theme(ax, fig)

        return fig
    
    
def plot_probability_histogram(probabilities: Dict[str, float], target_state:  str, num_qubits: int, n: int) -> Figure:
    """
    Bar chart of probability for each quantum basis state.
 
    The target state (goal cell) should appear as a towering bar after Grover's iterations. 
    This visualises PROBABILISTIC REASONING - the quantum computer is not certain, but heavily biased towards the correct answer.
 
    Parameters:
    probabilities: Dict[str, float] - Mapping of binary basis states to their probabilities.
    target_state: str - The binary string of the target state (goal cell).
    num_qubits: int - The total number of qubits used in the circuit.
    n: int - The grid size (n x n).

    Returns:
    Figure - A Matplotlib Figure object containing the histogram.
    """

    total_cells = n * n
    states = sorted(probabilities.keys())
    probs = [probabilities[s] for s in states]
 
    # Colour mapping: target = red, valid cells = violet, out-of-range = dark grey
    bar_colors = []
    for s in states:
        if s == target_state:
            bar_colors.append(COLORS['target'])
        elif int(s, 2) < total_cells:
            bar_colors.append(COLORS['quantum'])
        else:
            bar_colors.append('#444466')  # unused quantum states (out of grid range)
 
    # Limit display to 64 states max for readability
    max_display = min(len(states), 64)
    states_display = states[:max_display]
    probs_display  = probs[:max_display]
    colors_display = bar_colors[:max_display]
 
    fig, ax = plt.subplots(figsize = (12, 4))
    _dark_theme(ax, fig)
 
    x = np.arange(len(states_display))
    bars = ax.bar(x, probs_display, color=colors_display, edgecolor='none', width=0.8)
 
    # Highlight the target bar with a border
    target_idx_in_display = states_display.index(target_state) if target_state in states_display else None
    if target_idx_in_display is not None:
        bars[target_idx_in_display].set_edgecolor('white')
        bars[target_idx_in_display].set_linewidth(1.5)
 
    ax.set_xticks(x)
    ax.set_xticklabels(states_display, rotation = 90, fontsize = max(5, 9 - num_qubits), color = COLORS['text'])
    ax.set_ylabel('Probability', color = COLORS['text'])
    ax.set_xlabel('Basis State (binary)', color = COLORS['text'])
    ax.set_title(
        f"Quantum State Probabilities After Grover's Search  |  "
        f"Target: |{target_state}⟩  |  {num_qubits} qubits",
        color = COLORS['text'],
        fontsize = 11
    )
 
    # Legend
    legend_patches = [
        mpatches.Patch(color = COLORS['target'], label = f'Target |{target_state}⟩ (Goal Cell)'),
        mpatches.Patch(color = COLORS['quantum'], label = 'Valid Grid Cells'),
        mpatches.Patch(color = '#444466', label = 'Out-of-range States (unused qubits)'),
    ]
    ax.legend(handles = legend_patches, facecolor = COLORS['panel'], labelcolor = COLORS['text'], fontsize = 8, loc = 'upper right')
 
    # Annotate target probability
    if target_idx_in_display is not None:
        p = probs_display[target_idx_in_display]
        ax.annotate(
            f'{p:.3f}',
            xy = (target_idx_in_display, p),
            xytext = (target_idx_in_display, p + 0.02),
            ha = 'center',
            fontsize = 8,
            color = 'white',
            fontweight = 'bold'
        )
 
    fig.tight_layout()
    
    return fig


def plot_grover_convergence(convergence: List[Tuple[int, float]], optimal_k: int) -> Figure:
    """
    Line plot of target-state probability vs. Grover iteration count.

 
    Parameters:
    convergence: List[Tuple[int, float]] - A list of (iteration k, probability) pairs showing how the probability of measuring the target state evolves with each Grover iteration.
    optimal_k: int - The iteration count at which the probability peaks (the optimal number of Grover iterations to maximize success probability).

    Returns:
    Figure - A Matplotlib Figure object containing the convergence plot.
    """

    iterations = [c[0] for c in convergence]
    probabilities = [c[1] for c in convergence]
 
    fig, ax = plt.subplots(figsize = (10, 4))
    _dark_theme(ax, fig)
 
    # Main probability curve
    ax.plot(iterations, probabilities, color = COLORS['quantum'], linewidth = 2.5, marker = 'o', markersize = 5, label = 'P(target state)')
 
    # Shade the "amplification" region
    ax.fill_between(iterations, probabilities, alpha = 0.15, color = COLORS['quantum'])
 
    # Mark the optimal iteration with a vertical dashed line
    ax.axvline(x = optimal_k, color = COLORS['target'], linestyle = '--', linewidth = 1.5, label = f'Optimal k = {optimal_k}')
 
    # Mark peak probability
    peak_index = np.argmax(probabilities)
    ax.annotate(
        f'  Peak: {probabilities[peak_index]:.3f}\n  (k={iterations[peak_index]})',
        xy = (iterations[peak_index], probabilities[peak_index]),
        color = 'white', fontsize = 9,
        arrowprops = dict(arrowstyle = '->', color = COLORS['target']),
        xytext = (iterations[peak_index] + 0.5, probabilities[peak_index] - 0.15),
    )
 
    # Reference line: classical probability = 1/N
    if len(probabilities) > 0:
        num_states = 2 ** math.ceil(math.log2(max(1, len(probabilities))))
        classical_probability = 1.0 / num_states if num_states > 0 else 0
        ax.axhline(y = classical_probability, color = '#aaaaaa', linestyle = ':', linewidth = 1, label = f'Classical baseline (1/N = {classical_probability:.4f})')
 
    ax.set_xlabel('Grover Iteration (k)', color  =COLORS['text'])
    ax.set_ylabel('P(target) - Probability of Finding Goal', color = COLORS['text'])
    ax.set_title(
        "Grover's Algorithm - Amplitude Amplification Convergence\n"
        "(Probability rises then falls — quantum periodicity)",
        color = COLORS['text'], fontsize = 11
    )
    ax.set_ylim(-0.05, 1.05)
    ax.set_xticks(iterations)
    ax.legend(facecolor = COLORS['panel'], labelcolor = COLORS['text'], fontsize = 9)
    ax.grid(True, alpha = 0.15, color = COLORS['grid'])
 
    fig.tight_layout()

    return fig
 
def plot_comparison_bars(metrics_list) -> Figure:
    """
    Side-by-side grouped bar charts comparing:
    1. Left panel: Path Length per algorithm
    2. Right panel: Time (ms) per algorithm
 
    Parameters:
    metrics_list : list of Algorithm Metrics
    """
    names = [metric.name for metric in metrics_list]
    path_lengths = [metric.path_length if metric.path_found else 0 for metric in metrics_list]
    times_ms = [metric.time_ms for metric in metrics_list]
    nodes_exp = [metric.nodes_explored for metric in metrics_list]
    colors = [COLORS['bfs'], COLORS['astar'], COLORS['quantum']]
 
    fig, axes = plt.subplots(1, 3, figsize = (13, 4))
    fig.patch.set_facecolor(COLORS['bg'])
 
    datasets = [
        (axes[0], path_lengths, 'Path Length (cells)', 'Path Length'),
        (axes[1], times_ms, 'Time (ms)', 'Execution Time'),
        (axes[2], nodes_exp, 'Nodes/Oracle Calls', 'Search Effort'),
    ]
 
    for ax, values, ylabel, title in datasets:
        _dark_theme(ax, fig)
        bars = ax.bar(names, values, color = colors, edgecolor = 'none', width = 0.5)
 
        # Value labels on top of each bar
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(values) * 0.02,
                f'{val:.2f}' if isinstance(val, float) else str(val),
                ha = 'center', va = 'bottom',
                color = COLORS['text'], fontsize = 9, fontweight = 'bold'
            )
 
        ax.set_ylabel(ylabel, color = COLORS['text'])
        ax.set_title(title, color = COLORS['text'], fontsize = 11)
        ax.set_ylim(0, max(values) * 1.2 if max(values) > 0 else 1)
        ax.grid(True, axis = 'y', alpha = 0.15, color = COLORS['grid'])
 
    fig.suptitle(
        'Algorithm Benchmark Comparison',
        color = COLORS['text'], fontsize = 13, fontweight = 'bold', y = 1.02,
    )

    fig.tight_layout()

    return fig
