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
import metrics as M

ui.inject_global_css()
ui.top_nav(active="insights.py")

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-label">How It Works</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">From pixels to prediction</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="section-sub">An ImageNet-pretrained EfficientNetB0 with a small dense head, trained in two '
    f'phases (frozen backbone, then top-30-layer fine-tuning) with Adam, batch size 128, '
    f'ReduceLROnPlateau and early stopping on val_loss.</div>',
    unsafe_allow_html=True,
)
ui.pipeline_steps()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Results</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Model performance</div>', unsafe_allow_html=True)
ui.metric_counters()
st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)

train_acc = M.P1_TRAIN_ACC + M.P2_TRAIN_ACC
val_acc = M.P1_VAL_ACC + M.P2_VAL_ACC
epochs = list(range(1, len(val_acc) + 1))
split_at = M.P1_EPOCHS + 0.5

# Per-point hover deltas: change versus the previous epoch (signed).
def _deltas(vals):
    return ["first epoch"] + [f"{vals[i] - vals[i-1]:+.2f}pp vs epoch {i}" for i in range(1, len(vals))]
train_deltas, val_deltas = _deltas(train_acc), _deltas(val_acc)
phase = ["Phase 1 · frozen backbone"] * M.P1_EPOCHS + ["Phase 2 · fine-tuning"] * M.P2_EPOCHS

show_test = st.checkbox(
    f"Show held-out test accuracy ({M.TEST_ACC:.2f}%)",
    value=True,
    help="Validation is a random 15% split of the training folders. The test set is a separate "
         "Fruits-360 split, so it is the fairer number — and it sits lower than validation.",
)

fig = go.Figure()
fig.add_vrect(x0=split_at, x1=len(epochs) + 0.5, fillcolor=ui.ACCENT_PURPLE, opacity=0.07, line_width=0,
              annotation_text="Phase 2 · fine-tune", annotation_position="top left",
              annotation_font=dict(color=ui.TEXT_DIM, size=11))
fig.add_trace(go.Scatter(
    x=epochs, y=train_acc, mode="lines+markers", name="Train Accuracy (augmented)",
    line=dict(color=ui.ACCENT_BLUE, width=2, dash="dot"), marker=dict(size=7, color=ui.ACCENT_BLUE),
    customdata=list(zip(train_deltas, phase)),
    hovertemplate="Epoch %{x} · %{customdata[1]}<br>Train: %{y:.2f}%<br>Change: %{customdata[0]}<extra></extra>",
))
fig.add_trace(go.Scatter(
    x=epochs, y=val_acc, mode="lines+markers", name="Val Accuracy",
    line=dict(color=ui.ACCENT, width=3), marker=dict(size=9, color=ui.ACCENT_YELLOW),
    fill="tozeroy", fillcolor="rgba(45,212,167,0.14)",
    customdata=list(zip(val_deltas, phase)),
    hovertemplate="Epoch %{x} · %{customdata[1]}<br>Val: %{y:.2f}%<br>Change: %{customdata[0]}<extra></extra>",
))
if show_test:
    fig.add_hline(y=M.TEST_ACC, line=dict(color=ui.ACCENT_PURPLE, width=2, dash="dash"),
                  annotation_text=f"Test {M.TEST_ACC:.2f}%", annotation_position="bottom right",
                  annotation_font=dict(color=ui.ACCENT_PURPLE, size=12))

fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=ui.TEXT_DIM, family="Inter"),
    xaxis=dict(title="Epoch (15 frozen + 6 fine-tune)", gridcolor=ui.BORDER, zeroline=False, dtick=1),
    yaxis=dict(title="Accuracy (%)", gridcolor=ui.BORDER, zeroline=False, range=[50, 100]),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=10, r=10, t=40, b=10),
    height=380,
    hoverlabel=dict(bgcolor=ui.BG_ELEV, bordercolor=ui.BORDER, font=dict(color=ui.TEXT, family="Inter")),
)
st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
st.markdown(
    f'<div style="color:{ui.TEXT_FAINT}; font-size:.78rem; margin-top:-1rem;">'
    f'Train accuracy sits <i>below</i> validation because it is measured on heavily augmented images '
    f'(background swaps, noise, brightness/contrast jitter) with dropout active, while validation is clean. '
    f'The Phase 2 curve is flat — fine-tuning did not beat the Phase 1 checkpoint.</div>',
    unsafe_allow_html=True,
)

st.markdown("<div style='height:2rem;'></div>", unsafe_allow_html=True)
ui.insight_callouts()
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Where the parameters live — real numbers from model.summary().
# ---------------------------------------------------------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Architecture</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Where the parameters actually live</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Pooling and dropout layers carry no parameters. Almost everything sits in the '
    'pretrained EfficientNetB0 backbone; the trainable head is tiny.</div>',
    unsafe_allow_html=True,
)

layer_names = ["EfficientNetB0 backbone", f"Dense (256)", f"Dense ({M.NUM_CLASSES}) softmax"]
layer_params = [M.BACKBONE_PARAMS, M.HEAD_DENSE_PARAMS, M.HEAD_OUT_PARAMS]
layer_colors = [ui.ACCENT_BLUE, ui.ACCENT, ui.ACCENT_YELLOW]

param_fig = go.Figure(go.Bar(
    x=layer_params, y=layer_names, orientation="h",
    marker=dict(color=layer_colors),
    text=[f"{p:,}" for p in layer_params], textposition="outside",
    hovertemplate="%{y}<br>%{x:,} parameters<extra></extra>",
))
param_fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=ui.TEXT_DIM, family="Inter"),
    xaxis=dict(title="Parameters (log scale)", type="log", gridcolor=ui.BORDER, zeroline=False, range=[4, 7.4]),
    yaxis=dict(gridcolor=ui.BORDER, zeroline=False, autorange="reversed"),
    margin=dict(l=10, r=10, t=20, b=40),
    height=260,
    hoverlabel=dict(bgcolor=ui.BG_ELEV, bordercolor=ui.BORDER, font=dict(color=ui.TEXT, family="Inter")),
)
st.plotly_chart(param_fig, use_container_width=True, config={"displayModeBar": False})
st.markdown(
    f'<div style="color:{ui.TEXT_FAINT}; font-size:.78rem; margin-top:-.5rem;">'
    f'The pretrained backbone holds <b style="color:{ui.ACCENT};">{M.BACKBONE_PARAMS / 1e6:.2f}M</b> of the '
    f'model\'s {M.TOTAL_PARAMS / 1e6:.2f}M parameters ({M.BACKBONE_PARAMS / M.TOTAL_PARAMS:.0%}). Only the '
    f'{M.HEAD_PARAMS:,}-parameter head was trained in Phase 1; Phase 2 additionally unfroze the top 30 '
    f'backbone layers at a 1e-5 learning rate.</div>',
    unsafe_allow_html=True,
)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Per-class honesty: where the model is weakest on the held-out test set.
# ---------------------------------------------------------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Per-class results</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Where it shines, where it struggles</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="section-sub"><b style="color:{ui.ACCENT};">{M.CLASSES_F1_95}</b> of {M.NUM_CLASSES} classes score '
    f'F1 ≥ 0.95 and <b style="color:{ui.ACCENT};">{M.CLASSES_F1_90}</b> score ≥ 0.90 (macro F1 {M.MACRO_F1:.1f}%). '
    f'{M.CLASSES_F1_BELOW_60} classes fall below 0.60 — the ten weakest are shown here.</div>',
    unsafe_allow_html=True,
)
w_names = [n for n, _ in M.WEAKEST_CLASSES]
w_f1 = [f for _, f in M.WEAKEST_CLASSES]
weak_fig = go.Figure(go.Bar(
    x=w_f1, y=w_names, orientation="h", marker=dict(color=ui.ACCENT2),
    text=[f"{v:.2f}" for v in w_f1], textposition="outside",
    hovertemplate="%{y}<br>F1: %{x:.2f}<extra></extra>",
))
weak_fig.update_layout(
    plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color=ui.TEXT_DIM, family="Inter"),
    xaxis=dict(title="Test F1 score", range=[0, 1], gridcolor=ui.BORDER, zeroline=False),
    yaxis=dict(gridcolor=ui.BORDER, zeroline=False, autorange="reversed"),
    margin=dict(l=10, r=10, t=20, b=40), height=340,
    hoverlabel=dict(bgcolor=ui.BG_ELEV, bordercolor=ui.BORDER, font=dict(color=ui.TEXT, family="Inter")),
)
st.plotly_chart(weak_fig, use_container_width=True, config={"displayModeBar": False})
st.markdown('</div>', unsafe_allow_html=True)

ui.footer_section()
