"""
app.py
-------
Entry point for the multi-page app. Run with:

    streamlit run app.py

Pages live in views/ as separate files — the landing page stays nav-free
and immersive; every other page renders the shared custom top nav via
ui_components.top_nav(). Built-in Streamlit page chrome (sidebar nav) is
hidden via position="hidden" since we render our own nav bar instead.
"""

import streamlit as st

st.set_page_config(
    page_title="RetailVision | CV Product Recognition",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

landing = st.Page("views/landing.py", title="Home", icon="🏠", default=True)
demo = st.Page("views/demo.py", title="Live Demo", icon="🔍")
insights = st.Page("views/insights.py", title="Model Insights", icon="📊")
gallery = st.Page("views/gallery.py", title="Class Gallery", icon="🗂️")
about = st.Page("views/about.py", title="About", icon="✨")

pg = st.navigation([landing, demo, insights, gallery, about], position="hidden")
pg.run()
