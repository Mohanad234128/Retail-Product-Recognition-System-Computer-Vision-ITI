"""
views/gallery.py
------------------
The full 260-class catalog, grouped by base produce type so it reads as
a showcase grid instead of 260 lines of visual noise.

Rerun-vs-animation flag: st.text_input reruns the whole script on every
keystroke by default. With ~79 category cards each carrying a .fade-in /
tilt-hover entrance, a rerun-per-character would regenerate the filtered
HTML and replay every matching card's entrance animation on every single
character typed — visually janky, not smooth. Wrapping the input in
st.form sidesteps this entirely: the script only reruns once, when the
person submits (Enter or the button), not per keystroke.
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

with st.form(key="gallery_search_form", border=False):
    search_col, btn_col = st.columns([4, 1])
    with search_col:
        query = st.text_input(
            "Search classes",
            placeholder="Search by name — e.g. 'cherry', 'golden', 'pepper'…",
            label_visibility="collapsed",
        )
    with btn_col:
        st.form_submit_button("Search", use_container_width=True)

groups = grouped_classes()
query = (query or "").strip().lower()
if query:
    filtered = {}
    for cat, names in groups.items():
        if query in cat.lower():
            filtered[cat] = names  # category itself matches — show every variant
        else:
            matches = [n for n in names if query in n.lower()]
            if matches:
                filtered[cat] = matches
    groups = filtered
    st.markdown(
        f'<div style="color:{ui.TEXT_DIM}; font-size:.85rem; margin-bottom:1rem;">'
        f'{sum(len(v) for v in groups.values())} matching classes across {len(groups)} categories for "{query}"</div>',
        unsafe_allow_html=True,
    )

ui.class_showcase(groups)
st.markdown('</div>', unsafe_allow_html=True)

ui.footer_section()