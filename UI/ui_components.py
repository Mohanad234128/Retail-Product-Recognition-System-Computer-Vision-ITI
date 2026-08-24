"""
ui_components.py
------------------
Shared design system for the multi-page app. Every page calls
inject_global_css() first, then top_nav(active=...) — except the landing
page, which stays nav-free and immersive on purpose.

DESIGN TOKENS (do not introduce new colors elsewhere — reuse these):
  Background : cool neutral dark slate (not brown/orange, not gloomy) —
               produce colors show up as accents, not as the base hue
  Accents    : ACCENT (fresh teal-green) + ACCENT_DEEP (sky blue) form the
               primary gradient; ACCENT_YELLOW / ACCENT_BLUE / ACCENT_PURPLE
               / ACCENT2 add variety for labels, chips, and bounding boxes
  Type       : Fraunces (display) / Inter (body)
  Surfaces   : plain glass cards, static single-color frames — no animated
               color-cycling or gradient-fill effects

IMPORTANT — Streamlit markdown gotcha: inside any HTML string passed to
st.markdown(unsafe_allow_html=True), never put a blank line immediately
before a line indented 4+ spaces. Streamlit's markdown parser treats that
combination as an indented code block and renders the HTML as literal
text instead of parsing it. Keep HTML body content (outside <style> tags)
either free of internal blank lines, or indented under 4 spaces throughout.
"""

import base64
from io import BytesIO

import streamlit as st

# ---- Design tokens — "fresh & professional" palette -------------------------
# Cool dark neutral base (not brown/orange) so produce-color accents (green,
# yellow, blue, purple, tomato-red) pop without tinting the whole app warm.
# Reuse these tokens everywhere; don't hardcode new hex colors elsewhere.
ACCENT = "#2DD4A7"          # fresh teal-green — primary accent
ACCENT_DEEP = "#0EA5E9"     # sky blue — primary gradient partner
ACCENT2 = "#FBBF24"         # lemon yellow — secondary accent
ACCENT_YELLOW = "#FACC15"   # banana / corn
ACCENT_BLUE = "#60A5FA"     # blueberry
ACCENT_PURPLE = "#A78BFA"   # grape
ACCENT_TOMATO = "#FB7161"   # tomato-red, used sparingly (e.g. tomato label)
GRADIENT = f"linear-gradient(120deg, {ACCENT}, {ACCENT_DEEP})"
GRADIENT_LEAF = f"linear-gradient(120deg, {ACCENT}, #22C55E)"

BG = "#10141C"               # cool neutral dark slate — not brown, not gloomy
BG_ELEV = "#181E2A"          # card surface
BG_ELEV_2 = "#1E2534"        # soft alternate surface
BORDER = "#2C3346"           # cool hairline border
TEXT = "#EEF2F8"             # cool near-white text
TEXT_DIM = "#98A2B8"
TEXT_FAINT = "#5C6478"

# Confidence-based color system — used by the demo page's prediction card,
# top-k bars, and any future badge that needs to communicate "how sure".
CONF_HIGH = "#34D399"    # >90%
CONF_MID = "#FBBF24"     # 70-90%
CONF_LOW = "#F87171"     # <70%


def confidence_color(pct: float) -> str:
    """pct is 0-100. Returns the token for that confidence band."""
    if pct >= 90:
        return CONF_HIGH
    if pct >= 70:
        return CONF_MID
    return CONF_LOW


def rgba(hex_color: str, alpha: float) -> str:
    """Convert a '#RRGGBB' token to an 'rgba(r,g,b,a)' string — used for
    confidence-based glow intensity, which needs a variable alpha that a
    plain hex token can't express."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


def image_to_data_uri(pil_image, max_dim: int = 560, quality: int = 82) -> str:
    """Downscale + JPEG-encode a PIL image into an inline data URI, so it
    can be embedded directly inside an st.markdown HTML block (e.g. the
    vision-scan frame) instead of a separate st.image call — necessary
    because Streamlit elements from separate calls can't be nested inside
    each other's raw HTML, and the scan overlay needs the image and its
    corner-bracket/sweep decorations in one single positioned container."""
    img = pil_image.convert("RGB")
    img.thumbnail((max_dim, max_dim))
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=quality)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64}"

PAGES = [
    ("views/landing.py", "Home", "🏠"),
    ("views/demo.py", "Live Demo", "🔍"),
    ("views/insights.py", "Model Insights", "📊"),
    ("views/gallery.py", "Class Gallery", "🗂️"),
    ("views/about.py", "About", "✨"),
]

# Rough base-category -> emoji mapping for produce-themed chips/labels.
# Falls back to a leaf if a category isn't in here.
PRODUCE_EMOJI = {
    "Apple": "🍎", "Apricot": "🍑", "Avocado": "🥑", "Banana": "🍌",
    "Beetroot": "🫐", "Blackberry": "🫐", "Blueberry": "🫐", "Cabbage": "🥬",
    "Cactus": "🌵", "Cantaloupe": "🍈", "Carambola": "⭐", "Carrot": "🥕",
    "Cauliflower": "🥦", "Celery": "🥬", "Cherimoya": "🍈", "Cherry": "🍒",
    "Chestnut": "🌰", "Clementine": "🍊", "Cocos": "🥥", "Corn": "🌽",
    "Cucumber": "🥒", "Dates": "🌴", "Eggplant": "🍆", "Fig": "🫐",
    "Ginger": "🫚", "Gooseberry": "🫐", "Granadilla": "🫐", "Grape": "🍇",
    "Grapefruit": "🍊", "Guava": "🍈", "Hazelnut": "🌰", "Huckleberry": "🫐",
    "Kaki": "🍅", "Kiwi": "🥝", "Kohlrabi": "🥦", "Kumquats": "🍊",
    "Lemon": "🍋", "Limes": "🍋", "Lychee": "🍈", "Mandarine": "🍊",
    "Mango": "🥭", "Mangostan": "🍈", "Maracuja": "🫐", "Melon": "🍈",
    "Mulberry": "🫐", "Nectarine": "🍑", "Nut": "🌰", "Onion": "🧅",
    "Orange": "🍊", "Papaya": "🍈", "Passion": "🫐", "Peach": "🍑",
    "Peanut": "🥜", "Pear": "🍐", "Pepino": "🍈", "Pepper": "🌶️",
    "Physalis": "🫐", "Pineapple": "🍍", "Pistachio": "🥜", "Pitahaya": "🐉",
    "Plum": "🍑", "Pomegranate": "🫐", "Pomelo": "🍊", "Potato": "🥔",
    "Quince": "🍐", "Rambutan": "🍈", "Raspberry": "🫐", "Redcurrant": "🫐",
    "Salak": "🌴", "Strawberry": "🍓", "Tamarillo": "🍅", "Tangelo": "🍊",
    "Tomato": "🍅", "Walnut": "🌰", "Watermelon": "🍉", "Zucchini": "🥒",
    "Almonds": "🌰", "Orange": "🍊",
}


def produce_emoji(category: str) -> str:
    return PRODUCE_EMOJI.get(category, "🌿")


def inject_global_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap');

    #MainMenu, footer, header {{ visibility: hidden; }}
    section[data-testid="stSidebar"] {{ display: none; }}
    .block-container {{ padding-top: 0 !important; padding-bottom: 0 !important; max-width: 100% !important; }}
    .stApp {{ background: {BG}; color: {TEXT}; }}

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    h1, h2, h3, h4 {{ font-family: 'Fraunces', serif; }}

    ::-webkit-scrollbar {{ width: 12px; height: 12px; }}
    ::-webkit-scrollbar-track {{ background: {BG}; }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {ACCENT}, {ACCENT_DEEP}); border-radius: 8px;
        border: 3px solid {BG}; background-clip: padding-box;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: linear-gradient(180deg, {ACCENT_DEEP}, {ACCENT}); background-clip: padding-box; }}
    * {{ scrollbar-color: {ACCENT} {BG}; scrollbar-width: thin; }}

    /* ---- Fresh ambient background, fixed to viewport ---- */
    .aurora-bg {{
        position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none;
        background: {BG};
    }}
    .aurora-blob {{
        position: absolute; border-radius: 50%; filter: blur(105px);
    }}
    .blob-a {{ width: 620px; height: 620px; background: {ACCENT_YELLOW}; opacity: .30; top: -12%; left: -8%;
               animation: driftA 20s ease-in-out infinite alternate; }}
    .blob-b {{ width: 580px; height: 580px; background: {ACCENT2}; opacity: .28; bottom: -16%; right: -6%;
               animation: driftB 24s ease-in-out infinite alternate; }}
    .blob-c {{ width: 460px; height: 460px; background: {ACCENT}; opacity: .30; top: 40%; right: 14%;
               animation: driftC 28s ease-in-out infinite alternate; }}
    .blob-d {{ width: 380px; height: 380px; background: {ACCENT_PURPLE}; opacity: .22; top: 4%; left: 40%;
               animation: driftB 32s ease-in-out infinite alternate; }}
    .blob-e {{ width: 420px; height: 420px; background: {ACCENT_BLUE}; opacity: .2; bottom: 6%; left: 12%;
               animation: driftC 26s ease-in-out infinite alternate; }}
    @keyframes driftA {{ 0% {{ transform: translate(0,0) scale(1); }} 100% {{ transform: translate(60px,80px) scale(1.15); }} }}
    @keyframes driftB {{ 0% {{ transform: translate(0,0) scale(1); }} 100% {{ transform: translate(-70px,-50px) scale(1.1); }} }}
    @keyframes driftC {{ 0% {{ transform: translate(0,0); }} 100% {{ transform: translate(-40px,60px); }} }}
    .grain-overlay {{
        position: fixed; inset: 0; z-index: -1; pointer-events: none; opacity: .03;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    }}

    .section {{ padding: 3.5rem 6vw; max-width: 1180px; margin: 0 auto; }}
    .section-label {{
        display: inline-block; color: {ACCENT_DEEP}; font-family: 'Inter', sans-serif; font-weight: 700;
        letter-spacing: .18em; text-transform: uppercase; font-size: .72rem; margin-bottom: .8rem;
        border: 1px solid {ACCENT}44; padding: .3rem .8rem; border-radius: 999px; background: {ACCENT}14;
    }}
    .section-title {{ font-size: 2.3rem; font-weight: 700; margin-bottom: .5rem; color: {TEXT}; letter-spacing: -.01em; }}
    .section-sub {{ color: {TEXT_DIM}; font-size: 1rem; margin-bottom: 2.5rem; max-width: 620px; line-height: 1.6; }}

    .glass-card {{
        position: relative; overflow: hidden; background: {BG_ELEV};
        border: 1px solid {BORDER}; border-radius: 20px; padding: 1.75rem;
        box-shadow: 0 10px 28px -14px rgba(0, 0, 0, .55), inset 0 1px 0 rgba(255,255,255,.03);
        transition: border-color .3s ease, transform .35s cubic-bezier(.22,.9,.32,1.35), box-shadow .35s ease;
    }}
    .glass-card:hover {{
        border-color: {ACCENT}88; transform: translateY(-6px) scale(1.012);
        box-shadow: 0 24px 50px -16px {ACCENT}40, inset 0 1px 0 rgba(255,255,255,.04);
    }}
    /* CSS-only "sheen" sweep — a fixed diagonal highlight that crosses the
       card on hover. This substitutes for a true cursor-tracked spotlight,
       which would need live mouse coordinates that plain CSS can't read;
       see the feasibility note in inject_global_css's docstring. */
    .glass-card::after {{
        content: ""; position: absolute; top: 0; left: -60%; width: 45%; height: 100%;
        background: linear-gradient(120deg, transparent, {ACCENT}1F, {ACCENT_DEEP}14, transparent);
        transform: skewX(-18deg); transition: left .75s cubic-bezier(.2,.7,.3,1); pointer-events: none;
    }}
    .glass-card:hover::after {{ left: 130%; }}

    .accent-btn {{
        display: inline-block; background: {GRADIENT}; color: #FFFBF3 !important;
        font-family: 'Inter', sans-serif; font-weight: 700; font-size: .95rem;
        padding: .85rem 1.9rem; border-radius: 12px; text-decoration: none !important;
        box-shadow: 0 10px 26px -8px {ACCENT_DEEP}66;
        transition: transform .3s cubic-bezier(.22,.9,.32,1.35), box-shadow .3s ease;
        border: none;
    }}
    .accent-btn:hover {{ transform: translateY(-3px) scale(1.03); box-shadow: 0 16px 38px -8px {ACCENT_DEEP}99; }}
    .ghost-btn {{
        display: inline-block; background: {BG_ELEV}CC; color: {TEXT} !important;
        font-family: 'Inter', sans-serif; font-weight: 600; font-size: .95rem;
        padding: .82rem 1.85rem; border-radius: 12px; text-decoration: none !important;
        border: 1.5px solid {BORDER}; transition: border-color .2s ease, color .2s ease, transform .3s cubic-bezier(.22,.9,.32,1.35);
        backdrop-filter: blur(6px);
    }}
    .ghost-btn:hover {{ border-color: {ACCENT}; color: {ACCENT_DEEP} !important; transform: translateY(-2px); }}

    .chip {{
        display: inline-block; background: {BG_ELEV_2}; border: 1px solid {BORDER};
        color: {TEXT_DIM}; font-size: .8rem; padding: .38rem .9rem; border-radius: 999px;
        margin: .2rem; transition: all .2s ease;
    }}
    .chip:hover {{ border-color: {ACCENT}; color: {ACCENT_DEEP}; background: {ACCENT}12; transform: translateY(-1px); }}

    /* Native Streamlit buttons restyled to match custom nav / CTAs */
    div[data-testid="stButton"] > button {{
        background: {BG_ELEV}; color: {TEXT}; border: 1.5px solid {BORDER}; border-radius: 10px;
        font-family: 'Inter', sans-serif; font-weight: 600; font-size: .85rem;
        padding: .5rem 1.1rem; transition: all .25s cubic-bezier(.22,.9,.32,1.35);
    }}
    div[data-testid="stButton"] > button:hover {{ border-color: {ACCENT}; color: {ACCENT_DEEP}; transform: translateY(-2px) scale(1.02); }}
    div[data-testid="stButton"] > button:focus:not(:active) {{ border-color: {ACCENT}; color: {ACCENT_DEEP}; }}

    .nav-active > button {{ border-color: {ACCENT} !important; color: {ACCENT_DEEP} !important; background: {ACCENT}18 !important; }}

    /* Primary CTA buttons (st.button(type="primary") / st.link_button) get the full gradient treatment */
    button[kind="primary"], a[data-testid="stBaseLinkButton-primary"] {{
        background: {GRADIENT} !important; color: #FFFBF3 !important; border: none !important;
        font-weight: 700 !important; box-shadow: 0 10px 26px -8px {ACCENT_DEEP}66 !important;
        transition: transform .2s ease, box-shadow .2s ease !important;
    }}
    button[kind="primary"]:hover, a[data-testid="stBaseLinkButton-primary"]:hover {{
        transform: translateY(-2px); box-shadow: 0 14px 34px -8px {ACCENT_DEEP}88 !important;
    }}
    a[data-testid="stBaseLinkButton-secondary"] {{
        background: {BG_ELEV}CC !important; border: 1.5px solid {BORDER} !important; backdrop-filter: blur(6px);
        color: {TEXT} !important;
    }}
    a[data-testid="stBaseLinkButton-secondary"]:hover {{ border-color: {ACCENT} !important; color: {ACCENT_DEEP} !important; }}

    div[data-testid="stFileUploader"] {{
        background: {BG_ELEV}CC; border: 1.5px dashed {ACCENT}88; border-radius: 16px; padding: 1rem;
        backdrop-filter: blur(6px);
    }}
    .stProgress > div > div > div > div {{ background: {GRADIENT}; }}

    .fade-in {{ animation: fadeUp .7s ease both; }}
    @keyframes fadeUp {{ from {{ opacity:0; transform: translateY(14px); }} to {{ opacity:1; transform: translateY(0); }} }}

    /* ---- Scroll-driven reveal (CSS-only, no JS/IntersectionObserver) ----
       animation-timeline: view() ties the animation's progress directly to
       the element's position in the scrollport. Falls back to a plain
       one-shot fade-in on mount for browsers that don't support it yet
       (Chrome/Edge 115+ and current Firefox do). */
    .reveal-up {{ opacity: 0; transform: translateY(24px); animation: fadeUp .7s ease both; }}
    @supports (animation-timeline: view()) {{
        .reveal-up {{
            animation: revealUp linear both;
            animation-timeline: view();
            animation-range: entry 0% cover 30%;
        }}
        @keyframes revealUp {{
            from {{ opacity: 0; transform: translateY(36px) scale(.97); }}
            to   {{ opacity: 1; transform: translateY(0) scale(1); }}
        }}
    }}
    /* Stagger children of a reveal group without JS, using animation-delay
       on nth-child — apply .reveal-group to a row of columns' parent and
       .reveal-up to each card inside for a staggered cascade. */
    .reveal-group > div:nth-child(1) .reveal-up {{ animation-delay: 0s; }}
    .reveal-group > div:nth-child(2) .reveal-up {{ animation-delay: .08s; }}
    .reveal-group > div:nth-child(3) .reveal-up {{ animation-delay: .16s; }}
    .reveal-group > div:nth-child(4) .reveal-up {{ animation-delay: .24s; }}

    /* ---- Page/section mount transition ---- */
    .section {{ animation: sectionIn .5s ease both; }}
    @keyframes sectionIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
    <div class="aurora-bg">
    <div class="aurora-blob blob-a"></div>
    <div class="aurora-blob blob-b"></div>
    <div class="aurora-blob blob-c"></div>
    <div class="aurora-blob blob-d"></div>
    <div class="aurora-blob blob-e"></div>
    </div>
    <div class="grain-overlay"></div>
    """, unsafe_allow_html=True)


def top_nav(active: str):
    """Custom glass top nav bar. `active` is the page filename, e.g. 'demo.py'."""
    st.markdown(f"""
    <style>
      .nav-wrap {{
        position: sticky; top: 0; z-index: 999; backdrop-filter: blur(14px);
        background: {BG}CC; border-bottom: 1px solid {BORDER};
        padding: .9rem 6vw .8rem 6vw; display:flex; align-items:center; justify-content:space-between;
      }}
      .nav-brand {{ font-family:'Fraunces',serif; font-weight:700; font-size:1.05rem; color:{TEXT}; }}
      .nav-brand span {{ background:{GRADIENT}; -webkit-background-clip:text; background-clip:text; color:transparent; }}
    </style>
    <div class="nav-wrap">
      <div class="nav-brand">🧺 Harvest<span>Vision</span></div>
    </div>
    """, unsafe_allow_html=True)

    _, *cols_and_pad = st.columns([2.4] + [1] * len(PAGES) + [0.2])
    cols = cols_and_pad[:len(PAGES)]
    for col, (path, label, icon) in zip(cols, PAGES):
        is_active = path.endswith(active)
        with col:
            wrapper = st.container()
            with wrapper:
                if is_active:
                    st.markdown('<div class="nav-active">', unsafe_allow_html=True)
                clicked = st.button(f"{icon} {label}", key=f"nav_{path}", use_container_width=True)
                if is_active:
                    st.markdown('</div>', unsafe_allow_html=True)
            if clicked and not is_active:
                st.switch_page(path)
    st.markdown("<div style='height:.5rem;'></div>", unsafe_allow_html=True)


def vision_scan_frame(pil_image, caption: str = "", scan_delay: float = 0.0):
    """Renders the analyzed image inside a targeting-reticle frame: four
    corner brackets snap into place, then a single sweep line passes over
    the image once. This is a pure-CSS timed sequence, not a real-time
    scan — the actual inference call can (and should) happen immediately
    in Python; staggering this frame's animation-delay against the
    prediction card's own delay is what sells the illusion of "scan, then
    reveal", without an artificial time.sleep() blocking the script.

    The image is embedded as a base64 data URI in the same HTML block as
    the corner/sweep overlays, rather than using a separate st.image call,
    because Streamlit elements from different calls can't be nested inside
    one another's raw HTML — the overlay needs to sit directly on top of
    the image in one positioned container.
    """
    data_uri = image_to_data_uri(pil_image)
    st.markdown(f"""
    <style>
    .scan-frame {{ position: relative; width: 100%; border-radius: 16px; overflow: hidden;
      background: {BG_ELEV}; border: 1px solid {BORDER}; line-height: 0; }}
    .scan-frame img {{ display: block; width: 100%; height: auto; }}
    .scan-corner {{ position: absolute; width: 28px; height: 28px; border-color: {ACCENT};
      border-style: solid; opacity: 0; animation: cornerSnap .45s ease forwards; filter: drop-shadow(0 0 6px {ACCENT}88); }}
    .scan-corner.tl {{ top: 10px; left: 10px; border-width: 3px 0 0 3px; border-radius: 6px 0 0 0; animation-delay: {scan_delay + 0.1}s; }}
    .scan-corner.tr {{ top: 10px; right: 10px; border-width: 3px 3px 0 0; border-radius: 0 6px 0 0; animation-delay: {scan_delay + 0.22}s; }}
    .scan-corner.bl {{ bottom: 10px; left: 10px; border-width: 0 0 3px 3px; border-radius: 0 0 0 6px; animation-delay: {scan_delay + 0.34}s; }}
    .scan-corner.br {{ bottom: 10px; right: 10px; border-width: 0 3px 3px 0; border-radius: 0 0 6px 0; animation-delay: {scan_delay + 0.46}s; }}
    @keyframes cornerSnap {{ from {{ opacity: 0; scale: 1.5; }} to {{ opacity: 1; scale: 1; }} }}
    .scan-sweep {{ position: absolute; left: 0; width: 100%; height: 3px; top: -6%; opacity: 0;
      background: linear-gradient(90deg, transparent, {ACCENT}, {ACCENT_DEEP}, transparent);
      box-shadow: 0 0 18px 3px {ACCENT}AA; animation: sweepOnce 1.1s ease {scan_delay + 0.6}s forwards; }}
    @keyframes sweepOnce {{
      0% {{ top: -6%; opacity: 0; }}
      8% {{ opacity: 1; }}
      90% {{ opacity: 1; }}
      100% {{ top: 102%; opacity: 0; }}
    }}
    .scan-caption {{ position: absolute; bottom: 8px; left: 8px; right: 8px; font-size: .72rem;
      color: {TEXT_DIM}; background: {BG}DD; border-radius: 6px; padding: 3px 8px; opacity: 0;
      animation: scanCaptionIn .4s ease {scan_delay + 1.7}s forwards; font-family: 'Inter', sans-serif; }}
    @keyframes scanCaptionIn {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
    <div class="scan-frame">
    <img src="{data_uri}" alt="analyzed image" />
    <div class="scan-corner tl"></div>
    <div class="scan-corner tr"></div>
    <div class="scan-corner bl"></div>
    <div class="scan-corner br"></div>
    <div class="scan-sweep"></div>
    <div class="scan-caption">{caption}</div>
    </div>
    """, unsafe_allow_html=True)


def prediction_card(display_label: str, raw_label: str, confidence: float, reveal_delay: float = 1.4):
    pct = round(confidence * 100, 2)
    color = confidence_color(pct)
    band = "High confidence" if pct >= 90 else ("Moderate confidence" if pct >= 70 else "Lower confidence — worth a second look")
    glow_blur = int(16 + (pct / 100) * 34)
    glow = rgba(color, round(0.22 + (pct / 100) * 0.38, 2))
    st.markdown(f"""
    <style>
    @keyframes predictionIn {{ from {{ opacity: 0; scale: .96; transform: translateY(8px); }} to {{ opacity: 1; scale: 1; transform: translateY(0); }} }}
    </style>
    <div class="glass-card" style="text-align:center; padding:2.4rem 1.5rem; opacity:0;
      animation: predictionIn .55s cubic-bezier(.2,.8,.2,1) {reveal_delay}s forwards;
      border-color:{color}99; box-shadow: 0 10px 28px -14px rgba(0,0,0,.55), 0 0 {glow_blur}px {glow};">
      <div class="section-label" style="border-color:{color}55; background:{rgba(color, 0.12)}; color:{color};">Top Prediction</div>
      <div style="font-family:'Fraunces',serif; font-size:2rem; font-weight:700; color:{TEXT}; margin:.6rem 0 .2rem 0;">
        {display_label}
      </div>
      <div style="color:{TEXT_FAINT}; font-size:.78rem; margin-bottom:.5rem;">raw label: {raw_label}</div>
      <div style="color:{color}; font-size:.78rem; font-weight:600; margin-bottom:1rem;">{band}</div>
      <div style="background:{BORDER}; border-radius:999px; height:14px; overflow:hidden; margin-bottom:.6rem;">
        <div style="width:{pct}%; height:100%; background:linear-gradient(90deg, {rgba(color,0.6)}, {color}); box-shadow:0 0 14px {rgba(color,0.5)};"></div>
      </div>
      <div style="font-family:'Fraunces',serif; font-size:1.5rem; color:{color}; font-weight:700;">{pct}%</div>
      <div style="color:{TEXT_DIM}; font-size:.75rem; text-transform:uppercase; letter-spacing:.1em;">confidence</div>
    </div>
    """, unsafe_allow_html=True)


def top_k_bars(results, reveal_delay: float = 1.6):
    rows = ""
    for i, (raw, disp, conf) in enumerate(results):
        pct = round(conf * 100, 2)
        color = confidence_color(pct)
        delay = round(reveal_delay + i * 0.12, 2)
        rows += f"""
        <div style="margin-bottom:.9rem;">
          <div style="display:flex; justify-content:space-between; font-size:.85rem; margin-bottom:.3rem;">
            <span style="color:{TEXT};">#{i+1} {disp}</span>
            <span style="color:{color}; font-weight:600;">{pct}%</span>
          </div>
          <div style="background:{BORDER}; border-radius:999px; height:8px; overflow:hidden;">
            <div class="bar-fill" style="--bar-w:{pct}%; background:{color}; animation-delay:{delay}s;"></div>
          </div>
        </div>
        """
    st.markdown(f"""
    <style>
    .bar-fill {{ height: 100%; width: 0%; border-radius: 999px;
      animation: barGrow .75s cubic-bezier(.2,.8,.2,1) forwards; }}
    @keyframes barGrow {{ from {{ width: 0%; }} to {{ width: var(--bar-w); }} }}
    </style>
    <div class="glass-card">{rows}</div>
    """, unsafe_allow_html=True)


def metric_counters(val_acc=94.18, params_m=82.8, classes=260, train_imgs=137221):
    """Renders four metric cards whose numbers count up from 0 as they
    scroll into view — pure CSS, no JS, no iframe. Uses the same
    animation-timeline: view() technique as .reveal-up, combined with an
    animated integer custom property driving a CSS counter().

    CSS counters only support integers, so each metric is split into an
    animated integer part (0 -> 94, 0 -> 82, etc.) plus a static suffix
    appended after ('.18%', '.8M', 'K') — the count-up motion reads the
    same as a fully animated decimal without needing JS to get there.

    Browsers without animation-timeline: view() support get the plain
    final number immediately (no animation, no missing content) via the
    @supports fallback below.
    """
    def split(value, decimals, unit):
        int_part = int(value)
        if decimals == 0:
            return int_part, unit
        frac_str = f"{value - int_part:.{decimals}f}"[1:]  # ".18" from 0.18
        return int_part, frac_str + unit

    acc_int, acc_suffix = split(val_acc, 2, "%")
    params_int, params_suffix = split(params_m, 1, "M")
    classes_int, classes_suffix = int(classes), ""
    imgs_int, imgs_suffix = int(train_imgs / 1000), "K"

    metrics = [
        ("c1", acc_int, acc_suffix, "Val Accuracy"),
        ("c2", params_int, params_suffix, "Parameters"),
        ("c3", classes_int, classes_suffix, "Classes"),
        ("c4", imgs_int, imgs_suffix, "Training Images"),
    ]

    cards_html = ""
    counter_css = ""
    for cid, target, suffix, label in metrics:
        cards_html += (
            f'<div class="mcard">'
            f'<b><span class="num-fallback">{target}{suffix}</span>'
            f'<span class="num-animated {cid}"><span class="num-count"></span>{suffix}</span></b>'
            f'<span>{label}</span></div>'
        )
        counter_css += f"""
        @property --num-{cid} {{ syntax: '<integer>'; inherits: false; initial-value: 0; }}
        .num-animated.{cid} .num-count {{
            --num-{cid}: 0; counter-reset: n-{cid} var(--num-{cid});
            animation: count-{cid} linear both; animation-timeline: view(); animation-range: entry 0% cover 55%;
        }}
        .num-animated.{cid} .num-count::after {{ content: counter(n-{cid}); }}
        @keyframes count-{cid} {{ to {{ --num-{cid}: {target}; }} }}
        """

    st.markdown(f"""
    <style>
      .mcard-row {{ display:flex; gap:1.4rem; flex-wrap:wrap; justify-content:center; }}
      .mcard {{ background:{BG_ELEV}; border:1px solid {BORDER}; border-radius:16px; padding:1.7rem 2.3rem;
                text-align:center; min-width:150px; }}
      .mcard b {{ display:block; font-family:'Fraunces',serif; font-size:2.1rem; background:{GRADIENT};
                  -webkit-background-clip:text; background-clip:text; color:transparent; }}
      .mcard span {{ font-family:'Inter',sans-serif; color:{TEXT_DIM}; font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; }}
      .num-fallback {{ display:inline; }}
      .num-animated {{ display:none; }}
      @supports (animation-timeline: view()) {{
        .num-fallback {{ display:none; }}
        .num-animated {{ display:inline; }}
      }}
      {counter_css}
    </style>
    <div class="mcard-row">{cards_html}</div>
    """, unsafe_allow_html=True)


def pipeline_steps():
    steps = [
        ("01", "Raw Image", "100×100 RGB input, loaded and resized to match training-time preprocessing exactly."),
        ("02", "Rescale + Augment", "Pixel values rescaled to [0,1] via /255.; training-only augmentation used shear, horizontal/vertical flip, and zoom."),
        ("03", "From-Scratch CNN", "3 convolutional blocks (128→64→32 filters) with max-pooling and dropout, no pretrained backbone."),
        ("04", "260-Class Softmax", "Two dense layers (5000 → 1000 units) feed a 260-way softmax over produce categories."),
        ("05", "Prediction", "argmax gives the top class; the full softmax vector powers the top-k confidence ranking."),
    ]
    cols = st.columns(len(steps))
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div class="glass-card fade-in" style="min-height:230px;">
              <div style="background:{GRADIENT}; -webkit-background-clip:text; background-clip:text; color:transparent;
                          font-family:'Fraunces',serif; font-size:1.4rem; font-weight:700; margin-bottom:.6rem;">{num}</div>
              <div style="font-family:'Fraunces',serif; font-weight:600; margin-bottom:.5rem;">{title}</div>
              <div style="color:{TEXT_DIM}; font-size:.82rem; line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def insight_callouts():
    insights = [
        ("Still climbing", "Trained for only 5 epochs with early-stopping patience of 5 — the val-accuracy curve hadn't plateaued yet, so there's clear headroom left on the table."),
        ("No pretrained backbone", "The network was trained entirely from scratch (no ImageNet weights), which makes the 94.18% result a stronger signal of the architecture itself."),
        ("What's next", "Roadmap: more epochs, a confusion matrix to find per-class weak spots, and a MobileNetV2 transfer-learning comparison for a lighter, faster model."),
    ]
    cols = st.columns(3)
    for col, (title, desc) in zip(cols, insights):
        with col:
            st.markdown(f"""
            <div class="glass-card fade-in">
              <div style="font-family:'Fraunces',serif; color:{ACCENT}; font-weight:600; margin-bottom:.5rem;">{title}</div>
              <div style="color:{TEXT_DIM}; font-size:.85rem; line-height:1.55;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def class_showcase(groups: dict):
    """Renders each base-produce category as a card in a responsive grid.
    Cards get a fixed-direction 3D tilt on hover (perspective + rotateX/Y)
    rather than a flat lift — a CSS-only stand-in for true cursor-tracked
    tilt, which would need live mouse coordinates plain CSS can't read.
    """
    if not groups:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; color:{TEXT_DIM};">
          No categories match that search.
        </div>
        """, unsafe_allow_html=True)
        return

    cards = ""
    for cat, names in groups.items():
        emoji = produce_emoji(cat)
        chip_html = "".join(f'<span class="chip">{n}</span>' for n in names[:6])
        more = f'<span class="chip">+{len(names)-6} more</span>' if len(names) > 6 else ""
        cards += f"""
        <div class="glass-card tilt-card fade-in">
          <div style="font-family:'Fraunces',serif; font-weight:600; color:{TEXT}; margin-bottom:.6rem; font-size:1.05rem;">
            {emoji} {cat} <span style="color:{TEXT_DIM}; font-weight:400; font-size:.8rem;">({len(names)} variant{'s' if len(names) != 1 else ''})</span>
          </div>
          <div>{chip_html}{more}</div>
        </div>
        """
    st.markdown(f"""
    <style>
    .tilt-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 1rem; }}
    .glass-card.tilt-card {{ perspective: 700px; }}
    .glass-card.tilt-card:hover {{
        transform: perspective(700px) rotateX(6deg) rotateY(-8deg) translateY(-6px) scale(1.02);
        border-color: {ACCENT}88; box-shadow: 0 22px 46px -18px {ACCENT}40, inset 0 1px 0 rgba(255,255,255,.04);
    }}
    </style>
    <div class="tilt-grid">{cards}</div>
    """, unsafe_allow_html=True)


def footer_section():
    team = [
        ("Yasser Mogahed", "https://github.com/Yasser-Mogahed"),
        ("Abdallah Ali", None),
        ("Mohanad Ibrahim", None),
        ("Faisal Abdulaziz", None),
        ("Marawan Mohamed", None),
    ]
    team_html = ""
    for name, link in team:
        if link:
            team_html += f'<a class="chip" href="{link}" target="_blank" style="text-decoration:none;">{name}</a>'
        else:
            team_html += f'<span class="chip">{name}</span>'

    st.markdown(f"""
    <div style="border-top:1px solid {BORDER}; padding:3rem 6vw; text-align:center; margin-top:2rem;">
      <div class="section-label">Retail Product Recognition System</div>
      <p style="color:{TEXT_DIM}; font-size:.85rem; margin:.8rem 0 1.2rem 0;">
        A graduation project from the ITI Computer Vision track.
      </p>
      <div style="margin-bottom:1.5rem;">{team_html}</div>
      <a class="ghost-btn" href="https://github.com/Yasser-Mogahed/Retail-Product-Recognition-System-Computer-Vision-ITI" target="_blank">
        ↗ View source on GitHub
      </a>
      <p style="color:{TEXT_FAINT}; font-size:.72rem; margin-top:2rem;">
        Add your portfolio / LinkedIn links in <code>ui_components.py → footer_section()</code>.
      </p>
    </div>
    """, unsafe_allow_html=True)