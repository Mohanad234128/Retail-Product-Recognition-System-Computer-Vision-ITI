"""
views/landing.py
------------------
The landing page is deliberately nav-free and immersive — it's the "wow"
moment before the person ever sees the app's internal navigation. All
motion here is pure CSS (background from ui_components, grid sweep,
self-drawing bounding boxes, an animated accuracy ring) so nothing here
depends on JS execution inside an iframe — which matters because the
CTA buttons below need to be real, native Streamlit buttons wired to
st.switch_page, sitting in the same document flow as the animation.

NOTE on a real bug this file used to have: Streamlit's markdown parser
treats a blank line followed by a 4+-space-indented line as an indented
CODE block, not HTML — it'll render literal "<div>...</div>" text on the
page instead of parsing it. The HTML body below (everything after
</style>) is deliberately written with NO blank lines and minimal/no
indentation to avoid ever triggering that again. Only the <style> block
is safe to format normally, since script/style tags parse as raw HTML
regardless of blank lines inside them.
"""

import streamlit as st
import ui_components as ui

ui.inject_global_css()

st.markdown(f"""
<style>
  .hero {{
    position: relative; width: 100%; min-height: 78vh; overflow: hidden;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 2.5rem 1.5rem 1rem 1.5rem;
  }}
  .grid-bg {{
    position: absolute; inset: 0;
    background-image: linear-gradient({ui.BORDER} 1px, transparent 1px), linear-gradient(90deg, {ui.BORDER} 1px, transparent 1px);
    background-size: 46px 46px; opacity: .35;
    mask-image: radial-gradient(ellipse 70% 60% at 50% 40%, black 40%, transparent 90%);
  }}
  .scan-line {{
    position: absolute; left: 0; width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, {ui.ACCENT}, {ui.ACCENT_DEEP}, transparent);
    box-shadow: 0 0 24px 4px {ui.ACCENT}99; animation: scan 5s ease-in-out infinite;
  }}
  @keyframes scan {{ 0% {{ top:6%; opacity:0; }} 10% {{ opacity:1; }} 90% {{ opacity:1; }} 100% {{ top:88%; opacity:0; }} }}

  /* Simple static bounding-box frames — one fixed color each, no animation
     or color-cycling. They fade in once, then just sit there quietly. */
  .bbox {{ position: absolute; border: 2px solid; border-radius: 10px; opacity: 0; background: transparent;
    animation: bboxIn .9s ease forwards; }}
  .bbox span {{ position: absolute; top: -1.6rem; left: 0; font-size: .68rem; color: {ui.TEXT};
    background: {ui.BG_ELEV}; padding: 3px 8px; border: 1px solid {ui.BORDER}; border-radius: 5px; white-space: nowrap;
    font-family: 'Fraunces', serif; font-weight: 600; }}
  @keyframes bboxIn {{ 0% {{ opacity:0; transform: scale(1.06); }} 100% {{ opacity:1; transform: scale(1); }} }}
  .b1 {{ top: 14%; left: 8%; width: 140px; height: 105px; border-color: {ui.ACCENT}; box-shadow: 0 0 16px {ui.ACCENT}44; animation-delay: .3s; }}
  .b2 {{ top: 58%; left: 76%; width: 115px; height: 88px; border-color: {ui.ACCENT_BLUE}; box-shadow: 0 0 16px {ui.ACCENT_BLUE}44; animation-delay: 1.1s; }}
  .b3 {{ top: 10%; left: 70%; width: 96px; height: 96px; border-color: {ui.ACCENT_YELLOW}; box-shadow: 0 0 16px {ui.ACCENT_YELLOW}44; animation-delay: 1.9s; }}
  .b4 {{ top: 66%; left: 14%; width: 110px; height: 82px; border-color: {ui.ACCENT_PURPLE}; box-shadow: 0 0 16px {ui.ACCENT_PURPLE}44; animation-delay: 2.6s; }}

  .hero-inner {{
    position: relative; z-index: 5; display: flex; align-items: center; justify-content: center;
    gap: 3.5rem; flex-wrap: wrap; max-width: 1100px;
  }}
  .hero-text {{ max-width: 460px; text-align: left; }}
  .badge-pill {{
    display: inline-flex; align-items: center; gap: .4rem; color: {ui.TEXT_DIM}; font-size: .74rem;
    font-weight: 600; margin-bottom: 1.1rem; font-family: 'Inter', sans-serif;
    border: 1px solid {ui.BORDER}; padding: .35rem .85rem; border-radius: 999px; background: {ui.BG_ELEV}99;
  }}
  .kicker {{ color: {ui.ACCENT}; letter-spacing: .22em; text-transform: uppercase; font-size: .72rem;
    font-weight: 700; margin-bottom: .9rem; font-family: 'Inter', sans-serif; }}
  .headline {{ font-size: clamp(1.7rem, 2.6vw + 1rem, 2.5rem); font-weight: 600; color: {ui.TEXT}; line-height: 1.28;
    margin: 0 0 1rem 0; letter-spacing: -.01em; }}
  .headline .grad {{ background: {ui.GRADIENT}; -webkit-background-clip: text; background-clip: text; color: transparent; font-weight: 700; }}
  .sub {{ color: {ui.TEXT_DIM}; font-size: .98rem; line-height: 1.65; margin: 0 0 1.8rem 0; max-width: 46ch; }}

  .stat-row {{ display: flex; gap: 1.8rem; flex-wrap: wrap; }}
  .stat {{ text-align: left; }}
  .stat b {{ display: block; font-size: 1.35rem; background: {ui.GRADIENT}; -webkit-background-clip: text;
    background-clip: text; color: transparent; font-family: 'Fraunces', serif; }}
  .stat span {{ font-size: .7rem; color: {ui.TEXT_FAINT}; text-transform: uppercase; letter-spacing: .07em; }}

  .ring-wrap {{ position: relative; width: 200px; height: 200px; flex-shrink: 0; }}
  .ring-wrap svg {{ transform: rotate(-90deg); }}
  .ring-track {{ fill: none; stroke: {ui.BORDER}; stroke-width: 10; }}
  .ring-fill {{
    fill: none; stroke: url(#ringGradient); stroke-width: 10; stroke-linecap: round;
    stroke-dasharray: 364.4; stroke-dashoffset: 364.4;
    animation: fillRing 2.2s cubic-bezier(.2,.8,.2,1) .3s forwards;
    filter: drop-shadow(0 0 10px {ui.ACCENT}88);
  }}
  @keyframes fillRing {{ to {{ stroke-dashoffset: 21.2; }} }}
  .ring-center {{ position: absolute; inset: 0; display: flex; flex-direction: column;
    align-items: center; justify-content: center; text-align: center; }}
  .ring-center b {{ font-family: 'Fraunces', serif; font-size: 1.9rem; font-weight: 700; color: {ui.TEXT}; line-height: 1; }}
  .ring-center span {{ font-size: .66rem; color: {ui.TEXT_DIM}; text-transform: uppercase; letter-spacing: .07em; margin-top: .35rem; }}

  .scroll-cue {{ color: {ui.TEXT_FAINT}; font-size: .7rem; letter-spacing: .15em; text-transform: uppercase;
    margin-top: 1.5rem; animation: bob 2s ease-in-out infinite; text-align: center; }}
  @keyframes bob {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(6px); }} }}

  .float-emoji {{ position: absolute; font-size: 2rem; opacity: .4; filter: drop-shadow(0 6px 10px rgba(0,0,0,.35));
    animation: floaty 7s ease-in-out infinite; }}
  @keyframes floaty {{ 0%,100% {{ transform: translateY(0) rotate(-4deg); }} 50% {{ transform: translateY(-22px) rotate(5deg); }} }}
  .fe1 {{ top: 6%; left: 22%; animation-delay: .2s; font-size: 2.2rem; }}
  .fe2 {{ top: 20%; right: 8%; animation-delay: 1.4s; font-size: 1.8rem; }}
  .fe3 {{ bottom: 10%; left: 5%; animation-delay: 2.1s; font-size: 2rem; }}
  .fe4 {{ bottom: 18%; right: 20%; animation-delay: .8s; font-size: 1.6rem; }}
  .fe5 {{ top: 46%; left: 2%; animation-delay: 3s; font-size: 1.5rem; opacity: .3; }}
  .fe6 {{ top: 3%; right: 28%; animation-delay: 1.8s; font-size: 1.4rem; opacity: .34; }}
</style>
<div class="hero">
<div class="grid-bg"></div>
<div class="scan-line"></div>
<div class="bbox b1"><span>🍎 apple · 0.94</span></div>
<div class="bbox b2"><span>🍅 tomato · 0.91</span></div>
<div class="bbox b3"><span>🥑 avocado · 0.88</span></div>
<div class="bbox b4"><span>🌰 almond · 0.86</span></div>
<span class="float-emoji fe1">🍊</span>
<span class="float-emoji fe2">🍇</span>
<span class="float-emoji fe3">🥕</span>
<span class="float-emoji fe4">🍓</span>
<span class="float-emoji fe5">🌽</span>
<span class="float-emoji fe6">🥝</span>
<div class="hero-inner">
<div class="hero-text">
<div class="badge-pill">🎓 ITI Computer Vision Graduation Project</div>
<div class="kicker">Fresh Produce Recognition</div>
<h1 class="headline">A CNN trained from scratch to recognize <span class="grad">260 varieties</span> of fruits, vegetables &amp; nuts.</h1>
<p class="sub">Trained on over 137,000 images with no pretrained backbone — a proof of concept for automated recognition at retail scale.</p>
<div class="stat-row">
<div class="stat"><b>82.8M</b><span>Parameters</span></div>
<div class="stat"><b>260</b><span>Classes</span></div>
<div class="stat"><b>137K</b><span>Images</span></div>
</div>
</div>
<div class="ring-wrap">
<svg width="200" height="200" viewBox="0 0 130 130">
<defs>
<linearGradient id="ringGradient" x1="0%" y1="0%" x2="100%" y2="100%">
<stop offset="0%" stop-color="{ui.ACCENT}" />
<stop offset="35%" stop-color="{ui.ACCENT_YELLOW}" />
<stop offset="65%" stop-color="{ui.ACCENT2}" />
<stop offset="100%" stop-color="{ui.ACCENT_DEEP}" />
</linearGradient>
</defs>
<circle class="ring-track" cx="65" cy="65" r="58"></circle>
<circle class="ring-fill" cx="65" cy="65" r="58"></circle>
</svg>
<div class="ring-center">
<b>94.18%</b>
<span>Val Accuracy</span>
</div>
</div>
</div>
<div class="scroll-cue">Scroll to explore ⌄</div>
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
          <div style="font-family:'Fraunces',serif; font-weight:700; font-size:1.15rem; margin-bottom:.5rem;">{title}</div>
          <div style="color:{ui.TEXT_DIM}; font-size:.86rem; line-height:1.55; margin-bottom:1rem;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(cta, key=f"teaser_{target}", use_container_width=True):
            st.switch_page(target)

st.markdown('</div>', unsafe_allow_html=True)

ui.footer_section()
