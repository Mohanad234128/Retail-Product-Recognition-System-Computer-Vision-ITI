"""
views/gallery.py
------------------
The full 262-class catalog, grouped by base produce type so it reads as
a showcase grid instead of 262 lines of visual noise.

Rerun-vs-animation flag: st.text_input reruns the whole script on every
keystroke by default. With ~79 category cards each carrying a .fade-in /
tilt-hover entrance, a rerun-per-character would regenerate the filtered
HTML and replay every matching card's entrance animation on every single
character typed — visually janky, not smooth. Wrapping the input in
st.form sidesteps this entirely: the script only reruns once, when the
person submits (Enter or the button), not per keystroke.
"""

import random

import streamlit as st

import ui_components as ui
from class_names import grouped_classes

ui.inject_global_css()
ui.top_nav(active="gallery.py")

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Coverage</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">262 categories, grouped</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Raw class labels include variant numbers (e.g. "Apple Red Delicious 1"). '
    'Grouped here by base produce type so the full catalog reads as a showcase, not noise.</div>',
    unsafe_allow_html=True,
)

if "gallery_query_input" not in st.session_state:
    st.session_state["gallery_query_input"] = ""

surprise_col, toggle_col, sort_col = st.columns([1, 1, 1.6])
with surprise_col:
    if st.button("🎲 Surprise me", use_container_width=True):
        # Setting session_state for the not-yet-rendered text_input below,
        # earlier in this same script run, is enough — Streamlit picks it
        # up when that widget instantiates further down, no rerun needed.
        st.session_state["gallery_query_input"] = random.choice(list(grouped_classes().keys()))
with toggle_col:
    show_all = st.toggle("Show all variants", value=False, key="gallery_show_all",
                         help="Expand every card to list all of its variants.")
with sort_col:
    sort_mode = st.selectbox(
        "Sort", ["Alphabetical", "Most variants first"], label_visibility="collapsed",
    )

with st.form(key="gallery_search_form", border=False):
    search_col, btn_col = st.columns([4, 1])
    with search_col:
        query = st.text_input(
            "Search classes",
            key="gallery_query_input",
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

if sort_mode == "Most variants first":
    groups = dict(sorted(groups.items(), key=lambda kv: len(kv[1]), reverse=True))
else:
    groups = dict(sorted(groups.items(), key=lambda kv: kv[0].lower()))

ui.class_showcase(groups, show_all=show_all)
st.markdown('</div>', unsafe_allow_html=True)

ui.footer_section()

