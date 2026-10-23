"""
views/about.py
----------------
Project credits and background — the "About" destination in the nav.
"""

import streamlit as st

import ui_components as ui
import metrics as M

ui.inject_global_css()
ui.top_nav(active="about.py")

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-label">About</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">The project, in short</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="glass-card reveal-up" style="margin-bottom:1.5rem;">
  <p style="color:{ui.TEXT_DIM}; line-height:1.7; font-size:.95rem;">
    <b style="color:{ui.TEXT};">AgroVision</b> is the interactive showcase for the
    <b style="color:{ui.TEXT};">Retail Product Recognition System</b> — a graduation project from the
    ITI Computer Vision track. It fine-tunes an ImageNet-pretrained EfficientNetB0 on a
    {M.NUM_CLASSES}-category fresh-produce dataset (Fruits-360), used here as a
    representative stand-in for the broader problem of automated product recognition in retail
    shelf, checkout, and inventory pipelines.
  </p>
  <p style="color:{ui.TEXT_DIM}; line-height:1.7; font-size:.95rem;">
    The model scores <b style="color:{ui.ACCENT};">{M.TEST_ACC:.2f}% on the held-out test set</b>
    ({M.TEST_IMGS:,} images) and peaked at {M.BEST_VAL_ACC:.2f}% validation accuracy. Training used
    background-swap and photometric augmentation so it copes better with photos that don't look like
    white-background studio shots.
  </p>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section-label">Team</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title" style="font-size:1.6rem;">Built by</div>', unsafe_allow_html=True)

team = [
    ("Yasser Mogahed", "https://github.com/Yasser-Mogahed"),
    ("Abdallah Ali", None),
    ("Mohanad Ibrahim", None),
    ("Faisal Abdulaziz", None),
    ("Marawan Mohamed", None),
]
cols = st.columns(len(team))
for i, (col, (name, link)) in enumerate(zip(cols, team)):
    with col:
        link_html = f'<a href="{link}" target="_blank" style="color:{ui.ACCENT}; font-size:.78rem; text-decoration:none;">↗ GitHub</a>' if link else ""
        st.markdown(f"""
        <div class="glass-card reveal-up" style="text-align:center; animation-delay:{i * 0.08}s;">
          <div style="font-family:'Fraunces',serif; font-weight:600; font-size:.92rem; margin-bottom:.4rem;">{name}</div>
          {link_html}
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
st.link_button(
    "↗ View source on GitHub",
    "https://github.com/Yasser-Mogahed/Retail-Product-Recognition-System-Computer-Vision-ITI",
)
st.markdown('</div>', unsafe_allow_html=True)
