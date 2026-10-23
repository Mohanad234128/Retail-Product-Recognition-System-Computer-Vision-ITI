"""
views/landing.py
------------------
The landing page is deliberately nav-free and immersive — it's the "wow"
moment before the person ever sees the app's internal navigation. All
motion here is pure CSS (background from ui_components, grid sweep,
drifting bounding boxes, an animated accuracy ring, an auto-cycling
sample strip) so nothing here depends on JS execution inside an iframe —
which matters because the CTA buttons below need to be real, native
Streamlit buttons wired to st.switch_page, sitting in the same document
flow as the animation.

FEASIBILITY NOTE — no true mouse-tracked parallax here on purpose:
real parallax driven by cursor position needs a JS mousemove listener
with access to the whole page, but <script> tags inside st.markdown
never execute (browsers don't run scripts inserted via innerHTML), and
components.html's JS is sandboxed inside its own iframe, away from this
page's DOM. Instead, the grid, floating emoji, and bounding boxes each
drift on independent, differently-timed CSS animations — a "layers
moving at different speeds" illusion of depth without real cursor
tracking. If you want genuine mouse-tracked parallax later, it's
possible via a fragile same-origin iframe hack; flagged, not built,
since I can't test real mouse interaction in my sandbox.

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
import metrics as M

ui.inject_global_css(full_bleed=True)

# A slim, unobtrusive theme-toggle row — landing has no top_nav (by design,
# to stay immersive), so this is its own unique home for the toggle.
_, toggle_col = st.columns([9, 1.3])
with toggle_col:
    ui.theme_toggle_button(key="theme_toggle_landing")

st.markdown(f"""
<style>
  .hero {{
    position: relative; width: 100%; min-height: 78vh; overflow: hidden;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    padding: 2.5rem 1.5rem 1rem 1.5rem;
  }}
  .starfield {{
    position: absolute; inset: -10%; opacity: .5; pointer-events: none;
    background-image:
      radial-gradient(1.6px 1.6px at 18% 28%, {ui.TEXT_DIM}CC, transparent),
      radial-gradient(1.2px 1.2px at 62% 68%, {ui.TEXT_DIM}99, transparent),
      radial-gradient(1.6px 1.6px at 82% 18%, {ui.ACCENT}CC, transparent),
      radial-gradient(1.2px 1.2px at 32% 82%, {ui.ACCENT_BLUE}AA, transparent),
      radial-gradient(1.6px 1.6px at 48% 46%, {ui.TEXT_DIM}88, transparent),
      radial-gradient(1.2px 1.2px at 92% 58%, {ui.ACCENT_YELLOW}AA, transparent),
      radial-gradient(1.6px 1.6px at 8% 58%, {ui.TEXT_DIM}AA, transparent),
      radial-gradient(1.2px 1.2px at 72% 8%, {ui.ACCENT_PURPLE}AA, transparent),
      radial-gradient(1.4px 1.4px at 40% 12%, {ui.TEXT_DIM}88, transparent),
      radial-gradient(1.2px 1.2px at 55% 92%, {ui.ACCENT2}99, transparent);
    mask-image: radial-gradient(ellipse 72% 62% at 50% 40%, black 45%, transparent 92%);
    animation: starDrift 50s ease-in-out infinite alternate, starTwinkle 4s ease-in-out infinite alternate;
  }}
  @keyframes starDrift {{ from {{ translate: 0 0; }} to {{ translate: -26px 18px; }} }}
  @keyframes starTwinkle {{ from {{ opacity: .38; }} to {{ opacity: .62; }} }}
  .scan-line {{
    position: absolute; left: 0; width: 100%; height: 2px;
    background: linear-gradient(90deg, transparent, {ui.ACCENT_YELLOW}, {ui.ACCENT}, {ui.ACCENT_BLUE}, {ui.ACCENT_PURPLE}, transparent);
    box-shadow: 0 0 28px 5px {ui.ACCENT}AA; animation: scan 5s ease-in-out infinite;
  }}
  @keyframes scan {{ 0% {{ top:6%; opacity:0; }} 10% {{ opacity:1; }} 90% {{ opacity:1; }} 100% {{ top:88%; opacity:0; }} }}

  /* "Juicy" ambient color band — landing page only. This makes permanent
     and always-visible the vivid multi-color blend that used to only
     flash briefly right when the page (re)mounts, since every button
     click fully reruns the script and restarts these CSS animations
     from their initial state. Heavily blurred and kept fairly low
     opacity so it reads as atmosphere behind the hero text, not a
     distracting stripe. */
  .juicy-band {{
    position: absolute; top: 10%; left: -15%; width: 130%; height: 220px;
    background: linear-gradient(100deg, transparent, {ui.ACCENT_YELLOW}66, {ui.ACCENT}66, {ui.ACCENT_BLUE}5C, {ui.ACCENT_PURPLE}52, transparent);
    filter: blur(46px); opacity: .6; pointer-events: none;
    animation: juicyDrift 16s ease-in-out infinite alternate, juicyHue 14s linear infinite;
  }}
  @keyframes juicyDrift {{ from {{ translate: -4% -6px; }} to {{ translate: 4% 10px; }} }}
  @keyframes juicyHue {{
    0%   {{ filter: blur(46px) hue-rotate(0deg); }}
    50%  {{ filter: blur(52px) hue-rotate(45deg); }}
    100% {{ filter: blur(46px) hue-rotate(0deg); }}
  }}
  /* The two blobs nearest this band get a boost specifically on landing,
     so the ambient glow blends with them rather than looking like two
     unrelated effects layered on top of each other. */
  .aurora-blob.blob-a {{ opacity: .5 !important; }}
  .aurora-blob.blob-e {{ opacity: .38 !important; }}

  /* Bounding boxes now drift continuously along a slow organic path — like
     they're actively tracking something — instead of fading in and sitting
     still. `scale`/`translate`/`rotate` are used as independent CSS
     properties (not the shorthand `transform`) so the one-time entrance
     animation and the infinite drift animation can run together without
     one overwriting the other. */
  .bbox {{ position: absolute; border: 2px solid; border-radius: 10px; opacity: 0; background: transparent; scale: 1.06; }}
  .bbox span {{ position: absolute; top: -1.6rem; left: 0; font-size: .68rem; color: {ui.TEXT};
    background: {ui.BG_ELEV}; padding: 3px 8px; border: 1px solid {ui.BORDER}; border-radius: 5px; white-space: nowrap;
    font-family: 'Fraunces', serif; font-weight: 600; }}
  @keyframes bboxFade {{ from {{ opacity: 0; scale: 1.06; }} to {{ opacity: 1; scale: 1; }} }}
  @keyframes bboxDrift1 {{ 0%,100% {{ translate: 0 0 rotate(0deg); }} 30% {{ translate: 10px -8px; }} 60% {{ translate: -6px 6px; }} 85% {{ translate: 5px 4px; }} }}
  @keyframes bboxDrift2 {{ 0%,100% {{ translate: 0 0; }} 35% {{ translate: -9px 7px; }} 65% {{ translate: 7px -5px; }} }}
  @keyframes bboxDrift3 {{ 0%,100% {{ translate: 0 0; }} 40% {{ translate: 6px 9px; }} 70% {{ translate: -8px -4px; }} }}
  @keyframes bboxDrift4 {{ 0%,100% {{ translate: 0 0; }} 25% {{ translate: -7px -6px; }} 55% {{ translate: 8px 5px; }} 80% {{ translate: -4px 7px; }} }}
  .b1 {{ top: 14%; left: 8%; width: 140px; height: 105px; border-color: {ui.ACCENT}; box-shadow: 0 0 16px {ui.ACCENT}44;
    animation: bboxFade .9s ease .3s forwards, bboxDrift1 9s ease-in-out .3s infinite; }}
  .b2 {{ top: 58%; left: 76%; width: 115px; height: 88px; border-color: {ui.ACCENT_BLUE}; box-shadow: 0 0 16px {ui.ACCENT_BLUE}44;
    animation: bboxFade .9s ease 1.1s forwards, bboxDrift2 11s ease-in-out 1.1s infinite; }}
  .b3 {{ top: 10%; left: 70%; width: 96px; height: 96px; border-color: {ui.ACCENT_YELLOW}; box-shadow: 0 0 16px {ui.ACCENT_YELLOW}44;
    animation: bboxFade .9s ease 1.9s forwards, bboxDrift3 8s ease-in-out 1.9s infinite; }}
  .b4 {{ top: 66%; left: 14%; width: 110px; height: 82px; border-color: {ui.ACCENT_PURPLE}; box-shadow: 0 0 16px {ui.ACCENT_PURPLE}44;
    animation: bboxFade .9s ease 2.6s forwards, bboxDrift4 10s ease-in-out 2.6s infinite; }}

  .hero-inner {{
    position: relative; z-index: 5; display: flex; align-items: center; justify-content: center;
    gap: 3.5rem; flex-wrap: wrap; max-width: 1100px;
  }}
  .hero-text {{ max-width: 460px; text-align: left; }}
  .brand-wordmark {{
    display: flex; align-items: center; gap: .5rem; font-family: 'Fraunces', serif;
    font-size: 1.3rem; font-weight: 600; color: {ui.TEXT}; margin-bottom: 1.3rem;
  }}
  .brand-wordmark b {{
    background: {ui.GRADIENT}; -webkit-background-clip: text; background-clip: text;
    color: transparent; font-weight: 700;
  }}
  .badge-pill {{
    display: inline-flex; align-items: center; gap: .4rem; color: {ui.TEXT_DIM}; font-size: .74rem;
    font-weight: 600; margin-bottom: 1.1rem; font-family: 'Inter', sans-serif;
    border: 1px solid {ui.BORDER}; padding: .35rem .85rem; border-radius: 999px; background: {ui.BG_ELEV}99;
  }}
  .kicker {{ color: {ui.ACCENT}; letter-spacing: .22em; text-transform: uppercase; font-size: .72rem;
    font-weight: 700; margin-bottom: .9rem; font-family: 'Inter', sans-serif; }}
  .headline {{ font-size: clamp(1.7rem, 2.6vw + 1rem, 2.5rem); font-weight: 600; color: {ui.TEXT}; line-height: 1.28;
    margin: 0 0 1rem 0; letter-spacing: -.01em; }}
  .headline .grad {{
    background: linear-gradient(90deg, {ui.ACCENT}, {ui.ACCENT_YELLOW}, {ui.ACCENT2}, {ui.ACCENT_DEEP}, {ui.ACCENT});
    background-size: 300% auto; -webkit-background-clip: text; background-clip: text; color: transparent;
    font-weight: 700; animation: shimmerText 6s ease-in-out infinite;
  }}
  @keyframes shimmerText {{ 0%, 100% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} }}
  .sub {{ color: {ui.TEXT_DIM}; font-size: .98rem; line-height: 1.65; margin: 0 0 1.8rem 0; max-width: 46ch; }}

  .stat-row {{ display: flex; gap: 1.8rem; flex-wrap: wrap; }}
  .stat {{ text-align: left; opacity: 0; animation: fadeUp .6s ease both; }}
  .stat b {{ display: block; font-size: 1.35rem; background: {ui.GRADIENT}; -webkit-background-clip: text;
    background-clip: text; color: transparent; font-family: 'Fraunces', serif; }}
  .stat span {{ font-size: .7rem; color: {ui.TEXT_FAINT}; text-transform: uppercase; letter-spacing: .07em; }}
  .stat:nth-child(1) {{ animation-delay: .5s; }}
  .stat:nth-child(2) {{ animation-delay: .62s; }}
  .stat:nth-child(3) {{ animation-delay: .74s; }}
  @keyframes fadeUp {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}

  /* Accuracy ring, now with a second, faster, thinner "scanner" arc
     spinning behind it plus a pulse loosely timed to the bbox reveals. */
  .ring-wrap {{ position: relative; width: 200px; height: 200px; flex-shrink: 0;
    animation: ringPulse 3.2s ease-in-out infinite; }}
  @keyframes ringPulse {{
    0%, 100% {{ scale: 1; }}
    9% {{ scale: 1.035; }}
    12% {{ scale: 1; }}
    34% {{ scale: 1.035; }}
    38% {{ scale: 1; }}
    59% {{ scale: 1.035; }}
    63% {{ scale: 1; }}
    81% {{ scale: 1.035; }}
    85% {{ scale: 1; }}
  }}
  .ring-wrap svg {{ transform: rotate(-90deg); position: absolute; inset: 0; }}
  .ring-scanner {{
    fill: none; stroke: {ui.ACCENT}; stroke-width: 2; stroke-linecap: round;
    stroke-dasharray: 18 100; opacity: .8; filter: drop-shadow(0 0 6px {ui.ACCENT}); transform-origin: center;
    animation: spinScanner 2.4s linear infinite;
  }}
  @keyframes spinScanner {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
  .ring-track {{ fill: none; stroke: {ui.BORDER}; stroke-width: 10; }}
  .ring-fill {{
    fill: none; stroke: url(#ringGradient); stroke-width: 10; stroke-linecap: round;
    stroke-dasharray: 364.4; stroke-dashoffset: 364.4;
    animation: fillRing 2.2s cubic-bezier(.2,.8,.2,1) .3s forwards;
    filter: drop-shadow(0 0 10px {ui.ACCENT}88);
  }}
  @keyframes fillRing {{ to {{ stroke-dashoffset: {M.ring_offset()}; }} }}
  .ring-center {{ position: absolute; inset: 0; display: flex; flex-direction: column;
    align-items: center; justify-content: center; text-align: center; }}
  .ring-center b {{ font-family: 'Fraunces', serif; font-size: 1.9rem; font-weight: 700; color: {ui.TEXT}; line-height: 1; }}
  .ring-center span {{ font-size: .66rem; color: {ui.TEXT_DIM}; text-transform: uppercase; letter-spacing: .07em; margin-top: .35rem; }}

  /* Orbiting produce icons circling the accuracy ring — a signature
     "no one could imagine" flourish for the hero's focal point. */
  .orbit {{ position: absolute; inset: -45px; animation: orbitSpin 24s linear infinite; }}
  @keyframes orbitSpin {{ to {{ transform: rotate(360deg); }} }}
  .orbit-item {{
    position: absolute; top: 50%; left: 50%; width: 28px; height: 28px; margin: -14px;
    display: flex; align-items: center; justify-content: center; font-size: 1.3rem;
    filter: drop-shadow(0 3px 8px rgba(0,0,0,.45));
  }}

  .scroll-cue {{ color: {ui.TEXT_FAINT}; font-size: .7rem; letter-spacing: .15em; text-transform: uppercase;
    margin-top: 1.5rem; animation: bob 2s ease-in-out infinite; text-align: center; }}
  @keyframes bob {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(6px); }} }}

  /* Float-emoji durations diversified so each reads as its own depth layer. */
  .float-emoji {{ position: absolute; font-size: 2rem; opacity: .4; filter: drop-shadow(0 6px 10px rgba(0,0,0,.35)); }}
  @keyframes floaty {{ 0%,100% {{ translate: 0 0; rotate: -4deg; }} 50% {{ translate: 0 -22px; rotate: 5deg; }} }}
  .fe1 {{ top: 6%; left: 22%; font-size: 2.2rem; animation: floaty 6s ease-in-out .2s infinite; }}
  .fe2 {{ top: 20%; right: 8%; font-size: 1.8rem; animation: floaty 8.5s ease-in-out 1.4s infinite; }}
  .fe3 {{ bottom: 10%; left: 5%; font-size: 2rem; animation: floaty 7.2s ease-in-out 2.1s infinite; }}
  .fe4 {{ bottom: 18%; right: 20%; font-size: 1.6rem; animation: floaty 9.4s ease-in-out .8s infinite; }}
  .fe5 {{ top: 46%; left: 2%; font-size: 1.5rem; opacity: .3; animation: floaty 10.2s ease-in-out 3s infinite; }}
  .fe6 {{ top: 3%; right: 28%; font-size: 1.4rem; opacity: .34; animation: floaty 6.8s ease-in-out 1.8s infinite; }}

  /* "Wow" strip — auto-cycling sample tiles above the fold, a trailer for
     the real Live Demo page. No real images bundled by default, so this
     uses emoji tiles rather than assuming files exist in assets/samples/. */
  .wow-strip {{ display: flex; gap: 1rem; overflow-x: auto; padding: .3rem .2rem 1.4rem .2rem; scrollbar-width: none; }}
  .wow-strip::-webkit-scrollbar {{ display: none; }}
  .wow-tile {{
    position: relative; flex: 0 0 108px; height: 108px; border-radius: 16px;
    background: {ui.BG_ELEV}; border: 1px solid {ui.BORDER}; display: flex;
    align-items: center; justify-content: center; overflow: hidden;
  }}
  .wow-emoji {{ font-size: 2.3rem; filter: drop-shadow(0 4px 8px rgba(0,0,0,.35)); }}
  .wow-box {{
    position: absolute; inset: 9px; border: 2px solid var(--tile-accent); border-radius: 10px;
    opacity: 0; animation: wowBox 4.4s ease-in-out infinite; animation-delay: inherit;
  }}
  .wow-label {{
    position: absolute; bottom: 6px; left: 6px; right: 6px; font-size: .6rem; text-align: center;
    color: {ui.TEXT}; background: {ui.BG}DD; border-radius: 5px; padding: 2px 4px; opacity: 0;
    font-family: 'Inter', sans-serif; font-weight: 600; animation: wowLabel 4.4s ease-in-out infinite;
    animation-delay: inherit;
  }}
  @keyframes wowBox {{ 0%, 58%, 100% {{ opacity: 0; scale: 1.05; }} 15%, 45% {{ opacity: 1; scale: 1; }} }}
  @keyframes wowLabel {{ 0%, 58%, 100% {{ opacity: 0; }} 18%, 45% {{ opacity: 1; }} }}

  @media (max-width: 900px) {{
    .hero-inner {{ flex-direction: column; text-align: center; gap: 2.2rem; }}
    .hero-text {{ text-align: center; max-width: 100%; }}
    .stat-row {{ justify-content: center; }}
  }}
  @media (max-width: 480px) {{
    .ring-wrap {{ width: 160px; height: 160px; }}
    .ring-wrap svg {{ width: 160px; height: 160px; }}
    .orbit {{ display: none; }}
  }}
</style>
<div class="hero">
<div class="starfield"></div>
<div class="juicy-band"></div>
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
<div class="brand-wordmark">{ui.logo_svg(30)} <span>Agro<b>Vision</b></span></div>
<div class="badge-pill">🎓 ITI Computer Vision Graduation Project</div>
<div class="kicker">Fresh Produce Recognition</div>
<h1 class="headline">A CNN-based computer vision system for multi-class <span class="grad">fruit, vegetable &amp; nut recognition</span>.</h1>
<p class="sub">Transfer learning on {M.TOTAL_TRAIN_FOLDER_IMGS:,} images, hardened with background-swap augmentation — a proof of concept for automated recognition at retail scale.</p>
<div class="stat-row">
<div class="stat"><b>{M.params_label()}</b><span>Parameters</span></div>
<div class="stat"><b>{M.NUM_CLASSES}</b><span>Classes</span></div>
<div class="stat"><b>{M.compact_count(M.TOTAL_TRAIN_FOLDER_IMGS)}</b><span>Images</span></div>
</div>
</div>
<div class="ring-wrap">
<div class="orbit">
<span class="orbit-item" style="transform: rotate(0deg) translate(135px) rotate(0deg);">🍊</span>
<span class="orbit-item" style="transform: rotate(60deg) translate(135px) rotate(-60deg);">🍇</span>
<span class="orbit-item" style="transform: rotate(120deg) translate(135px) rotate(-120deg);">🥕</span>
<span class="orbit-item" style="transform: rotate(180deg) translate(135px) rotate(-180deg);">🍓</span>
<span class="orbit-item" style="transform: rotate(240deg) translate(135px) rotate(-240deg);">🌽</span>
<span class="orbit-item" style="transform: rotate(300deg) translate(135px) rotate(-300deg);">🥝</span>
</div>
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
<circle class="ring-scanner" cx="65" cy="65" r="50"></circle>
</svg>
<div class="ring-center">
<b>{M.TEST_ACC:.2f}%</b>
<span>Test Accuracy</span>
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
# "Wow" strip — a trailer for the Live Demo, auto-classifying itself on loop
# ---------------------------------------------------------------------------
wow_tiles = [
    ("🍎", "Apple · 0.94", ui.ACCENT),
    ("🍅", "Tomato · 0.91", ui.ACCENT_TOMATO),
    ("🥑", "Avocado · 0.88", ui.ACCENT2),
    ("🌽", "Corn · 0.90", ui.ACCENT_YELLOW),
    ("🍇", "Grape · 0.87", ui.ACCENT_PURPLE),
    ("🥕", "Carrot · 0.93", ui.ACCENT_TOMATO),
    ("🍓", "Strawberry · 0.89", ui.ACCENT),
    ("🌰", "Almond · 0.86", ui.ACCENT_BLUE),
]
tiles_html = ""
for i, (emoji, label, color) in enumerate(wow_tiles):
    delay = round(i * 0.45, 2)
    tiles_html += (
        f'<div class="wow-tile" style="animation-delay:{delay}s; --tile-accent:{color};">'
        f'<span class="wow-emoji">{emoji}</span>'
        f'<div class="wow-box"></div>'
        f'<div class="wow-label">{label}</div>'
        f'</div>'
    )
st.markdown(
    f'<div style="padding:0 6vw;"><div class="wow-strip">{tiles_html}</div></div>',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Teaser cards — three doors into the rest of the app
# ---------------------------------------------------------------------------
st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Explore the project</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Three ways in</div>', unsafe_allow_html=True)

teasers = [
    ("🔍", "Live Demo", "Upload a product photo or try a sample — watch the model classify it in real time with a full top-5 confidence breakdown.", "views/demo.py", "Try the demo →"),
    ("📊", "Model Insights", f"The architecture, training curve, and honest roadmap — how an EfficientNetB0 transfer-learning model reached {M.TEST_ACC:.2f}% on the held-out test set.", "views/insights.py", "See the numbers →"),
    ("🗂️", "Class Gallery", f"All {M.NUM_CLASSES} recognized categories, grouped by base produce type so the full catalog reads as a showcase, not noise.", "views/gallery.py", "Browse classes →"),
]

cols = st.columns(3)
for i, (col, (icon, title, desc, target, cta)) in enumerate(zip(cols, teasers)):
    with col:
        st.markdown(f"""
        <div class="glass-card reveal-up" style="min-height:230px; animation-delay:{i * 0.1}s;">
          <div style="font-size:1.8rem; margin-bottom:.7rem;">{icon}</div>
          <div style="font-family:'Fraunces',serif; font-weight:700; font-size:1.15rem; margin-bottom:.5rem;">{title}</div>
          <div style="color:{ui.TEXT_DIM}; font-size:.86rem; line-height:1.55; margin-bottom:1rem;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(cta, key=f"teaser_{target}", use_container_width=True):
            st.switch_page(target)

st.markdown('</div>', unsafe_allow_html=True)

ui.footer_section()
