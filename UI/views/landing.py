"""
views/landing.py
------------------
The landing page is deliberately nav-free and immersive — it's the "wow"
moment before the person ever sees the app's internal navigation. All
motion here is pure CSS (aurora background from ui_components, grid
sweep, self-drawing bounding boxes, typewriter reveal) so nothing here
depends on JS execution inside an iframe — which matters because the
CTA buttons below need to be real, native Streamlit buttons wired to
st.switch_page, sitting in the same document flow as the animation.
"""

import streamlit as st
import ui_components as ui

ui.inject_global_css()

# ---------------------------------------------------------------------------
# Hero visual layer — pure CSS, transparent background so the fixed aurora
# glow behind it shows through and blends seamlessly into the CTA row below.
# ---------------------------------------------------------------------------
st.markdown(f"""
<style>
  .hero {{
    position: relative; width: 100%; min-height: 82vh; overflow: hidden;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    text-align: center; padding: 2rem 1.5rem 1rem 1.5rem;
  }}
  .grid-bg {{
    position: absolute; inset: 0;
    background-image: linear-gradient({ui.BORDER} 1px, transparent 1px), linear-gradient(90deg, {ui.BORDER} 1px, transparent 1px);
    background-size: 46px 46px; opacity: .3;
    mask-image: radial-gradient(ellipse 70% 60% at 50% 40%, black 40%, transparent 90%);
  }}
  .scan-line {{
    position: absolute; left: 0; width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, {ui.CYAN}, {ui.VIOLET}, transparent);
    box-shadow: 0 0 24px 4px {ui.CYAN}99; animation: scan 5s ease-in-out infinite;
  }}
  @keyframes scan {{ 0% {{ top:6%; opacity:0; }} 10% {{ opacity:1; }} 90% {{ opacity:1; }} 100% {{ top:88%; opacity:0; }} }}

  .bbox {{ position: absolute; border: 1.5px solid {ui.CYAN}; border-radius: 8px; opacity: 0;
    animation: bboxIn .9s ease forwards; box-shadow: 0 0 22px {ui.CYAN}33; }}
  .bbox span {{ position: absolute; top: -1.5rem; left: 0; font-size: .68rem; color: {ui.CYAN};
    background: {ui.BG}; padding: 2px 7px; border: 1px solid {ui.CYAN}55; border-radius: 5px; white-space: nowrap;
    font-family: 'Space Grotesk', sans-serif; }}
  @keyframes bboxIn {{ 0% {{ opacity:0; transform: scale(1.1); }} 100% {{ opacity:1; transform: scale(1); }} }}
  .b1 {{ top: 16%; left: 10%; width: 150px; height: 110px; animation-delay: .3s; border-color: {ui.CYAN}; }}
  .b2 {{ top: 60%; left: 74%; width: 120px; height: 90px; animation-delay: 1.1s; border-color: {ui.VIOLET}; }}
  .b3 {{ top: 12%; left: 68%; width: 100px; height: 100px; animation-delay: 1.9s; border-color: {ui.CYAN}; }}
  .b4 {{ top: 68%; left: 16%; width: 115px; height: 85px; animation-delay: 2.6s; border-color: {ui.VIOLET}; }}
  .b2 span, .b4 span {{ color: {ui.VIOLET}; border-color: {ui.VIOLET}55; }}

  .hero-content {{ position: relative; z-index: 5; max-width: 860px; }}
  .kicker {{ color: {ui.CYAN}; letter-spacing: .28em; text-transform: uppercase; font-size: .74rem;
    font-weight: 600; margin-bottom: 1.3rem; font-family: 'Space Grotesk', sans-serif; }}
  .headline {{ font-size: clamp(2.3rem, 5.2vw, 3.9rem); font-weight: 700; color: {ui.TEXT}; line-height: 1.14;
    margin: 0 0 1.2rem 0; letter-spacing: -.01em; }}
  .headline .grad {{ background: {ui.GRADIENT}; -webkit-background-clip: text; background-clip: text; color: transparent; }}

  .sub-wrap {{ overflow: hidden; display: inline-block; max-width: 640px; }}
  .sub {{
    color: {ui.TEXT_DIM}; font-size: 1.08rem; line-height: 1.6; margin: 0 auto 2.3rem auto;
    white-space: nowrap; overflow: hidden; border-right: 2px solid {ui.CYAN};
    animation: typewriter 2.6s steps(46, end) 1 both, blink .8s step-end 4;
    max-width: 46ch; display: block;
  }}
  @keyframes typewriter {{ from {{ max-width: 0; }} to {{ max-width: 46ch; }} }}
  @keyframes blink {{ 50% {{ border-color: transparent; }} }}

  .stat-row {{ display: flex; gap: 2.4rem; justify-content: center; margin-bottom: 2.6rem; flex-wrap: wrap; }}
  .stat {{ text-align: center; }}
  .stat b {{ display: block; font-size: 1.7rem; background: {ui.GRADIENT}; -webkit-background-clip: text;
    background-clip: text; color: transparent; font-family: 'Space Grotesk', sans-serif; }}
  .stat span {{ font-size: .74rem; color: {ui.TEXT_DIM}; text-transform: uppercase; letter-spacing: .08em; }}

  .scroll-cue {{ color: {ui.TEXT_FAINT}; font-size: .7rem; letter-spacing: .15em; text-transform: uppercase;
    margin-top: .5rem; animation: bob 2s ease-in-out infinite; }}
  @keyframes bob {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(6px); }} }}
</style>

<div class="hero">
  <div class="grid-bg"></div>
  <div class="scan-line"></div>
  <div class="bbox b1"><span>product · 0.94</span></div>
  <div class="bbox b2"><span>product · 0.88</span></div>
  <div class="bbox b3"><span>product · 0.91</span></div>
  <div class="bbox b4"><span>product · 0.86</span></div>

  <div class="hero-content">
    <div class="kicker">CNN · Retail Product Recognition · ITI Computer Vision</div>
    <h1 class="headline">A CNN built <span class="grad">from scratch</span>,<br/>
        260 product categories,<br/>
        <span class="grad">94.18%</span> validation accuracy</h1>
    <span class="sub">A proof-of-concept for automated product recognition at retail scale.</span>
    <div class="stat-row">
      <div class="stat"><b>82.8M</b><span>Parameters</span></div>
      <div class="stat"><b>260</b><span>Classes</span></div>
      <div class="stat"><b>137K</b><span>Training Images</span></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# CTA row — native Streamlit widgets, same transparent background as the
# hero above, so it reads as one continuous immersive section.
# ---------------------------------------------------------------------------
_, c1, c2, _ = st.columns([2.6, 1.1, 1.1, 2.6])
with c1:
    if st.button("Enter the Experience →", type="primary", use_container_width=True):
        st.switch_page("views/demo.py")
with c2:
    st.link_button(
        "↗ View on GitHub",
        "https://github.com/Yasser-Mogahed/Retail-Product-Recognition-System-Computer-Vision-ITI",
        use_container_width=True,
    )

st.markdown('<div style="text-align:center;" class="scroll-cue">Scroll to explore ⌄</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Teaser cards — three doors into the rest of the app
# ---------------------------------------------------------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Explore the project</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Three ways in</div>', unsafe_allow_html=True)

teasers = [
    ("🔍", "Live Demo", "Upload a product photo or try a sample — watch the model classify it in real time with a full top-5 confidence breakdown.", "views/demo.py", "Try the demo →"),
    ("📊", "Model Insights", "The architecture, training curve, and honest roadmap — how a from-scratch CNN reached 94.18% validation accuracy in 5 epochs.", "views/insights.py", "See the numbers →"),
    ("🗂️", "Class Gallery", "All 260 recognized categories, grouped by base produce type so the full catalog reads as a showcase, not noise.", "views/gallery.py", "Browse classes →"),
]

cols = st.columns(3)
for col, (icon, title, desc, target, cta) in zip(cols, teasers):
    with col:
        st.markdown(f"""
        <div class="glass-card fade-in" style="min-height:230px;">
          <div style="font-size:1.8rem; margin-bottom:.7rem;">{icon}</div>
          <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:1.15rem; margin-bottom:.5rem;">{title}</div>
          <div style="color:{ui.TEXT_DIM}; font-size:.86rem; line-height:1.55; margin-bottom:1rem;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(cta, key=f"teaser_{target}", use_container_width=True):
            st.switch_page(target)

st.markdown('</div>', unsafe_allow_html=True)

ui.footer_section()
