"""
views/gallery.py
------------------
The full 260-class catalog, grouped by base produce type so it reads as
a showcase grid instead of 260 lines of visual noise.
"""

import streamlit as st

import ui_components as ui
from class_names import grouped_classes

ui.inject_global_css()
ui.top_nav(active="gallery.py")

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Coverage</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">260 categories, grouped</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Raw class labels include variant numbers (e.g. "Apple Red Delicious 1"). '
    'Grouped here by base produce type so the full catalog reads as a showcase, not noise.</div>',
    unsafe_allow_html=True,
)
ui.class_showcase(grouped_classes())
st.markdown('</div>', unsafe_allow_html=True)

ui.footer_section()
