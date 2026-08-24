"""
views/insights.py
-------------------
Architecture pipeline, real training metrics (Plotly curve), and the
honest roadmap callouts, pulled from the graduation project README.

Hover deltas and the extrapolation toggle both use Plotly's own
interactivity/rerun path — no custom JS needed, since Plotly ships its
own event handling independent of Streamlit's markdown limitations, and
the toggle is just a native st.checkbox triggering an ordinary rerun.
"""

import streamlit as st
import plotly.graph_objects as go

import ui_components as ui

ui.inject_global_css()
ui.top_nav(active="insights.py")

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-label">How It Works</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">From pixels to prediction</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">A from-scratch CNN — no pretrained backbone — trained with '
    'categorical crossentropy and SGD, batch size 64, with early stopping on val_accuracy.</div>',
    unsafe_allow_html=True,
)
ui.pipeline_steps()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Model performance</div>', unsafe_allow_html=True)
ui.metric_counters()
st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)

epochs = [1, 2, 3, 4, 5]
train_acc = [58.64, 80.45, 88.08, 91.34, 93.38]
val_acc = [79.57, 87.13, 91.12, 91.16, 94.18]

# Per-point hover deltas: how much each epoch gained over the previous one.
train_deltas = ["first epoch"] + [f"+{train_acc[i] - train_acc[i-1]:.2f}pp vs epoch {i}" for i in range(1, len(train_acc))]
val_deltas = ["first epoch"] + [f"+{val_acc[i] - val_acc[i-1]:.2f}pp vs epoch {i}" for i in range(1, len(val_acc))]

show_extrapolation = st.checkbox(
    "Show illustrative extrapolation — what if training continued?",
    value=False,
    help="A simple diminishing-returns projection, not a real forecast — shown to make the "
         "\"the curve hadn't plateaued yet\" claim easier to see, not to predict an exact number.",
)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=epochs, y=train_acc, mode="lines+markers", name="Train Accuracy",
    line=dict(color=ui.ACCENT_BLUE, width=2, dash="dot"), marker=dict(size=7, color=ui.ACCENT_BLUE),
    customdata=train_deltas,
    hovertemplate="Epoch %{x}<br>Train Accuracy: %{y:.2f}%<br>Change: %{customdata}<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=epochs, y=val_acc, mode="lines+markers", name="Val Accuracy",
    line=dict(color=ui.ACCENT, width=3), marker=dict(size=9, color=ui.ACCENT_YELLOW),
    fill="tozeroy", fillcolor="rgba(45,212,167,0.14)",
    customdata=val_deltas,
    hovertemplate="Epoch %{x}<br>Val Accuracy: %{y:.2f}%<br>Change: %{customdata}<extra></extra>",
))

if show_extrapolation:
    # Simple diminishing-returns heuristic: each hypothetical future epoch
    # closes a fixed fraction of the remaining gap to 100%. This is purely
    # illustrative — it's not a trained forecast — which is why it's
    # opt-in, dashed, and labeled as such in both the legend and hover text.
    future_epochs = list(range(5, 11))
    projected = [val_acc[-1]]
    current, gap_close_rate = val_acc[-1], 0.35
    for _ in range(5):
        remaining = 100 - current
        current = current + remaining * gap_close_rate
        projected.append(round(current, 2))
    fig.add_trace(go.Scatter(
        x=future_epochs, y=projected, mode="lines+markers", name="Hypothetical (illustrative)",
        line=dict(color=ui.ACCENT_PURPLE, width=2, dash="dash"),
        marker=dict(size=6, color=ui.ACCENT_PURPLE, symbol="diamond"),
        hovertemplate="Epoch %{x} (hypothetical)<br>Projected: %{y:.2f}%<extra></extra>",
    ))

fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=ui.TEXT_DIM, family="Inter"),
    xaxis=dict(title="Epoch", gridcolor=ui.BORDER, zeroline=False, dtick=1),
    yaxis=dict(title="Accuracy (%)", gridcolor=ui.BORDER, zeroline=False, range=[50, 102]),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=10, r=10, t=40, b=10),
    height=380,
    hoverlabel=dict(bgcolor=ui.BG_ELEV, bordercolor=ui.BORDER, font=dict(color=ui.TEXT, family="Inter")),
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
if show_extrapolation:
    st.markdown(
        f'<div style="color:{ui.TEXT_FAINT}; font-size:.72rem; margin-top:-1rem;">'
        f'The dashed line is a simple diminishing-returns heuristic, not a trained prediction — '
        f'it illustrates that the curve had room to keep climbing, not what it would have hit exactly.</div>',
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
ui.insight_callouts()
st.markdown('</div>', unsafe_allow_html=True)

ui.footer_section()