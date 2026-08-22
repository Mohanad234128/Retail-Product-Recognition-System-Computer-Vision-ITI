"""
views/insights.py
-------------------
Architecture pipeline, real training metrics (Plotly curve), and the
honest roadmap callouts, pulled from the graduation project README.
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

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=epochs, y=train_acc, mode="lines+markers", name="Train Accuracy",
    line=dict(color=ui.TEXT_DIM, width=2), marker=dict(size=7),
))
fig.add_trace(go.Scatter(
    x=epochs, y=val_acc, mode="lines+markers", name="Val Accuracy",
    line=dict(color=ui.CYAN, width=3), marker=dict(size=9, color=ui.CYAN),
    fill="tozeroy", fillcolor="rgba(0,240,192,0.08)",
))
fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=ui.TEXT_DIM, family="Inter"),
    xaxis=dict(title="Epoch", gridcolor=ui.BORDER, zeroline=False, dtick=1),
    yaxis=dict(title="Accuracy (%)", gridcolor=ui.BORDER, zeroline=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=10, r=10, t=40, b=10),
    height=380,
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
ui.insight_callouts()
st.markdown('</div>', unsafe_allow_html=True)

ui.footer_section()
