import streamlit as st


GLOBAL_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

    :root {
        --bg-0: #060814;
        --bg-1: #0b1220;
        --bg-2: #111a2e;
        --surface: rgba(14, 22, 39, 0.78);
        --surface-strong: rgba(17, 26, 46, 0.94);
        --surface-soft: rgba(255, 255, 255, 0.04);
        --border: rgba(148, 163, 184, 0.18);
        --text: #f8fafc;
        --muted: #9aa7bb;
        --accent: #7c9cff;
        --accent-2: #2dd4bf;
        --accent-3: #f59e0b;
        --shadow: 0 24px 80px rgba(0, 0, 0, 0.35);
    }

    html, body, [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top left, rgba(124, 156, 255, 0.18), transparent 26%),
            radial-gradient(circle at 92% 12%, rgba(45, 212, 191, 0.14), transparent 22%),
            radial-gradient(circle at 50% 115%, rgba(245, 158, 11, 0.08), transparent 26%),
            linear-gradient(180deg, var(--bg-0), var(--bg-1) 48%, #08101d 100%);
        color: var(--text);
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        color: var(--text);
    }

    .block-container {
        padding-top: 1.6rem;
        padding-bottom: 2.5rem;
        max-width: 1280px;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(9, 14, 26, 0.98), rgba(10, 16, 29, 0.95));
        border-right: 1px solid var(--border);
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 1.1rem;
    }

    section[data-testid="stSidebar"] * {
        color: var(--text) !important;
    }


    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: var(--text) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSlider"] {
        padding-top: 0.15rem;
        padding-bottom: 0.45rem;
    }

    section[data-testid="stSidebar"] [data-testid="stSlider"] label,
    section[data-testid="stSidebar"] [data-testid="stSlider"] p {
        color: var(--text) !important;
    }

    /* Keep sidebar sliders visually close to Streamlit defaults */
    section[data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
        box-shadow: none !important;
    }

    /* Use a neutral tone for slider help icons instead of white */
    section[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stWidgetLabelHelp"] svg,
    section[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stWidgetLabelHelp"] path {
        color: #94a3b8 !important;
        fill: currentColor !important;
        stroke: currentColor !important;
    }

    section[data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, rgba(124, 156, 255, 1), rgba(45, 212, 191, 1));
    }

    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        background-image:
            linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
        background-size: 72px 72px;
        mask-image: linear-gradient(180deg, rgba(0,0,0,0.65), transparent 90%);
        opacity: 0.18;
    }

    h1, h2, h3, h4, h5 {
        color: var(--text) !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.03em;
    }

    p, li, td, th, label, div {
        font-family: 'Inter', sans-serif;
    }

    hr {
        border-color: rgba(148, 163, 184, 0.14) !important;
        margin: 1rem 0;
    }

    .hero-shell {
        position: relative;
        border: 1px solid var(--border);
        border-radius: 28px;
        padding: 1.6rem 1.8rem;
        margin: 0 0 1.4rem 0;
        background:
            linear-gradient(135deg, rgba(124, 156, 255, 0.14), rgba(17, 26, 46, 0.92) 34%, rgba(45, 212, 191, 0.06));
        box-shadow: var(--shadow);
        overflow: hidden;
    }
    .hero-shell::after {
        content: "";
        position: absolute;
        inset: auto -12% -56% auto;
        width: 220px;
        height: 220px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(124, 156, 255, 0.22), transparent 70%);
        filter: blur(10px);
    }

    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.45rem 0.8rem;
        border: 1px solid rgba(124, 156, 255, 0.25);
        background: rgba(255, 255, 255, 0.04);
        border-radius: 999px;
        color: var(--muted);
        font-size: 0.8rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.4fr) minmax(320px, 0.8fr);
        gap: 1.2rem;
        align-items: end;
        margin-top: 1rem;
    }

    .hero-title {
        font-size: clamp(2.4rem, 5vw, 4.8rem);
        font-weight: 900;
        line-height: 0.96;
        margin: 0.35rem 0 0.8rem 0;
    }

    .hero-copy {
        color: var(--muted);
        font-size: 1rem;
        line-height: 1.7;
        max-width: 62ch;
        margin: 0;
    }

    .hero-pills {
        display: flex;
        flex-wrap: wrap;
        gap: 0.7rem;
        justify-content: flex-end;
    }

    .hero-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        border-radius: 999px;
        padding: 0.65rem 0.9rem;
        border: 1px solid var(--border);
        background: rgba(255, 255, 255, 0.04);
        color: var(--text);
        font-size: 0.86rem;
        box-shadow: 0 14px 30px rgba(0, 0, 0, 0.12);
    }

    .hero-pill strong {
        color: var(--accent);
    }

    .theme-table-wrapper {
        border: 1px solid var(--border);
        border-radius: 20px;
        overflow: hidden;
        background: rgba(255,255,255,0.03);
        box-shadow: var(--shadow);
        margin: 0.8rem 0 1.2rem;
    }

    table.theme-table {
        width: 100%;
        border-collapse: collapse;
        color: var(--text);
        font-size: 0.95rem;
    }

    table.theme-table thead th {
        background: rgba(124, 156, 255, 0.14);
        color: var(--text);
        text-align: left;
        padding: 0.95rem 1rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.18);
        font-size: 0.82rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    table.theme-table tbody td {
        background: rgba(255,255,255,0.02);
        color: var(--text);
        padding: 0.88rem 1rem;
        border-bottom: 1px solid rgba(148, 163, 184, 0.10);
        vertical-align: top;
    }

    table.theme-table tbody tr:nth-child(even) td {
        background: rgba(255,255,255,0.045);
    }
    
    table.theme-table tbody tr:hover td {
        background: rgba(124, 156, 255, 0.10);
    }

    .theme-table-note {
        color: var(--muted);
        font-size: 0.82rem;
        margin-top: 0.5rem;
        text-align: right;
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 1rem 1rem 0.9rem;
        box-shadow: 0 12px 30px rgba(0,0,0,0.16);
    }

    div[data-testid="metric-container"] label,
    div[data-testid="metric-container"] div {
        color: var(--text) !important;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.7rem;
        font-weight: 800;
        letter-spacing: -0.03em;
    }

    [data-testid="stMetricLabel"] {
        color: var(--muted) !important;
        font-size: 0.84rem !important;
    }

    .surface-card,
    .info-box,
    .warn-box {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 1rem 1.05rem;
        margin: 0.8rem 0;
        box-shadow: 0 14px 36px rgba(0,0,0,0.18);
        backdrop-filter: blur(14px);
    }

    .info-box {
        border-left: 4px solid var(--accent);
    }

    .warn-box {
        border-left: 4px solid var(--accent-3);
    }

    .surface-card h3,
    .info-box h3,
    .warn-box h3 {
        margin-top: 0;
    }

    .surface-card p,
    .info-box p,
    .warn-box p {
        color: var(--muted);
    }

    .feature-card {
        border: 1px solid var(--border);
        border-radius: 20px;
        padding: 1rem 1.05rem;
        background: rgba(255, 255, 255, 0.04);
        box-shadow: 0 14px 28px rgba(0, 0, 0, 0.16);
        height: 100%;
    }

    .feature-card b,
    .feature-card i,
    .feature-card p {
        color: var(--text);
    }

    .feature-card p {
        color: var(--muted);
    }

    .grid-section {
        text-align: center;
    }

    .panel-shell {
        border: 1px solid var(--border);
        border-radius: 24px;
        background: rgba(255, 255, 255, 0.03);
        padding: 1.25rem;
        box-shadow: var(--shadow);
    }

    .soft-divider {
        height: 1px;
        margin: 1rem 0 1.25rem;
        background: linear-gradient(90deg, transparent, rgba(148, 163, 184, 0.22), transparent);
    }

    .section-label {
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.45rem 0.75rem;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: rgba(255,255,255,0.04);
        color: var(--muted);
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }

    div.stButton > button {
        background: linear-gradient(135deg, rgba(124, 156, 255, 1), rgba(45, 212, 191, 1));
        color: #08111f;
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 14px;
        font-weight: 800;
        width: 100%;
        padding: 0.9rem 0;
        margin-top: 0.6rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
        box-shadow: 0 12px 24px rgba(124, 156, 255, 0.22);
    }
    div.stButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.04);
        box-shadow: 0 18px 34px rgba(124, 156, 255, 0.28);
    }

    button[kind="primary"] {
        background: linear-gradient(135deg, rgba(124, 156, 255, 1), rgba(45, 212, 191, 1)) !important;
        color: #08111f !important;
    }

    div[data-testid="stNumberInput"] input,
    div[data-baseweb="input"] input {
        background: rgba(7, 12, 22, 0.9) !important;
        color: var(--text) !important;
        border: 1px solid rgba(148, 163, 184, 0.22) !important;
        border-radius: 14px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }

    div[data-testid="stNumberInput"] input::placeholder,
    div[data-baseweb="input"] input::placeholder {
        color: rgba(154, 167, 187, 0.7) !important;
    }

    div[data-testid="stNumberInput"] button {
        color: var(--text) !important;
        opacity: 0.9;
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        border-radius: 10px !important;
        min-width: 2rem !important;
        min-height: 2rem !important;
    }

    div[data-testid="stNumberInput"] button:hover {
        opacity: 1;
        background: rgba(124, 156, 255, 0.18) !important;
    }

    div[data-baseweb="checkbox"] {
        color: var(--text) !important;
    }

    div[data-baseweb="select"] > div {
        background: rgba(7, 12, 22, 0.92) !important;
        color: var(--text) !important;
        border: 1px solid rgba(148, 163, 184, 0.22) !important;
        border-radius: 14px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.03);
    }

    div[data-baseweb="select"] svg {
        fill: var(--muted) !important;
    }

</style>
"""


def apply_global_styles() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html = True)
