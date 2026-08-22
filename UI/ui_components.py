"""
ui_components.py
------------------
Shared design system for the multi-page app. Every page calls
inject_global_css() first, then top_nav(active=...) — except the landing
page, which stays nav-free and immersive on purpose.

DESIGN TOKENS (do not introduce new colors elsewhere — reuse these):
  Background : warm cream with a slow-moving harvest-color glow
  Accents    : ACCENT (tomato-orange) + ACCENT2 (leaf green), used for gradients/glow only
  Type       : Fraunces (display) / Inter (body)
  Surfaces   : soft cards on cream, warm hairline borders, gradient-glow on hover
"""

import streamlit as st
import streamlit.components.v1 as components

# ---- Design tokens — "premium dark pantry" palette --------------------------
# Rich, warm dark background (charcoal with a brown undertone, not cold
# tech-black) so the tomato/citrus/leaf accents glow against it. Reuse these
# tokens everywhere; don't hardcode new hex colors elsewhere.
ACCENT = "#FF7A50"        # tomato-orange — primary accent, brightened for dark bg contrast
ACCENT_DEEP = "#FF4B2B"   # deeper tomato red, for gradient stops
ACCENT2 = "#5FC26A"       # leaf green — secondary accent, brightened for dark bg
GRADIENT = f"linear-gradient(120deg, {ACCENT}, {ACCENT_DEEP})"
GRADIENT_LEAF = f"linear-gradient(120deg, {ACCENT2}, #3FA34D)"

BG = "#161210"             # warm near-black, brown undertone — not cold cyber-black
BG_ELEV = "#211A15"        # card surface
BG_ELEV_2 = "#271F19"      # soft alternate surface
BORDER = "#3A2E24"         # warm dark hairline border
TEXT = "#F3E9DA"           # warm cream text, not stark white
TEXT_DIM = "#AB9B87"
TEXT_FAINT = "#6E6151"

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

    ::-webkit-scrollbar {{ width: 10px; }}
    ::-webkit-scrollbar-track {{ background: {BG}; }}
    ::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 6px; }}

    /* ---- Harvest-glow ambient background, fixed to viewport ---- */
    .aurora-bg {{
        position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none;
        background: {BG};
    }}
    .aurora-blob {{
        position: absolute; border-radius: 50%; filter: blur(100px); opacity: .32;
    }}
    .blob-a {{ width: 640px; height: 640px; background: #FFC24B; top: -14%; left: -8%;
               animation: driftA 22s ease-in-out infinite alternate; }}
    .blob-b {{ width: 580px; height: 580px; background: {ACCENT2}; bottom: -16%; right: -6%;
               animation: driftB 26s ease-in-out infinite alternate; }}
    .blob-c {{ width: 420px; height: 420px; background: {ACCENT}; top: 42%; right: 16%; opacity: .2;
               animation: driftC 30s ease-in-out infinite alternate; }}
    .blob-d {{ width: 340px; height: 340px; background: #C86BFF; top: 6%; left: 42%; opacity: .12;
               animation: driftB 34s ease-in-out infinite alternate; }}
    @keyframes driftA {{ 0% {{ transform: translate(0,0) scale(1); }} 100% {{ transform: translate(60px,80px) scale(1.15); }} }}
    @keyframes driftB {{ 0% {{ transform: translate(0,0) scale(1); }} 100% {{ transform: translate(-70px,-50px) scale(1.1); }} }}
    @keyframes driftC {{ 0% {{ transform: translate(0,0); }} 100% {{ transform: translate(-40px,60px); }} }}
    .grain-overlay {{
        position: fixed; inset: 0; z-index: -1; pointer-events: none; opacity: .025;
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
        position: relative; background: {BG_ELEV};
        border: 1px solid {BORDER}; border-radius: 20px; padding: 1.75rem;
        box-shadow: 0 10px 28px -14px rgba(0, 0, 0, .55), inset 0 1px 0 rgba(255,255,255,.03);
        transition: border-color .3s ease, transform .3s ease, box-shadow .3s ease;
    }}
    .glass-card:hover {{
        border-color: {ACCENT}88; transform: translateY(-4px);
        box-shadow: 0 22px 46px -16px {ACCENT}3D, inset 0 1px 0 rgba(255,255,255,.04);
    }}

    .accent-btn {{
        display: inline-block; background: {GRADIENT}; color: #FFFBF3 !important;
        font-family: 'Inter', sans-serif; font-weight: 700; font-size: .95rem;
        padding: .85rem 1.9rem; border-radius: 12px; text-decoration: none !important;
        box-shadow: 0 10px 26px -8px {ACCENT_DEEP}66; transition: transform .2s ease, box-shadow .2s ease;
        border: none;
    }}
    .accent-btn:hover {{ transform: translateY(-2px); box-shadow: 0 14px 34px -8px {ACCENT_DEEP}88; }}
    .ghost-btn {{
        display: inline-block; background: {BG_ELEV}CC; color: {TEXT} !important;
        font-family: 'Inter', sans-serif; font-weight: 600; font-size: .95rem;
        padding: .82rem 1.85rem; border-radius: 12px; text-decoration: none !important;
        border: 1.5px solid {BORDER}; transition: border-color .2s ease, color .2s ease;
        backdrop-filter: blur(6px);
    }}
    .ghost-btn:hover {{ border-color: {ACCENT}; color: {ACCENT_DEEP} !important; }}

    .chip {{
        display: inline-block; background: {BG_ELEV_2}; border: 1px solid {BORDER};
        color: {TEXT_DIM}; font-size: .8rem; padding: .38rem .9rem; border-radius: 999px;
        margin: .2rem; transition: all .2s ease;
    }}
    .chip:hover {{ border-color: {ACCENT}; color: {ACCENT_DEEP}; background: {ACCENT}12; }}

    /* Native Streamlit buttons restyled to match custom nav / CTAs */
    div[data-testid="stButton"] > button {{
        background: {BG_ELEV}; color: {TEXT}; border: 1.5px solid {BORDER}; border-radius: 10px;
        font-family: 'Inter', sans-serif; font-weight: 600; font-size: .85rem;
        padding: .5rem 1.1rem; transition: all .2s ease;
    }}
    div[data-testid="stButton"] > button:hover {{ border-color: {ACCENT}; color: {ACCENT_DEEP}; }}
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
    </style>

    <div class="aurora-bg">
      <div class="aurora-blob blob-a"></div>
      <div class="aurora-blob blob-b"></div>
      <div class="aurora-blob blob-c"></div>
      <div class="aurora-blob blob-d"></div>
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


def prediction_card(display_label: str, raw_label: str, confidence: float):
    pct = round(confidence * 100, 2)
    st.markdown(f"""
    <div class="glass-card fade-in" style="text-align:center; padding:2.4rem 1.5rem;">
      <div class="section-label">Top Prediction</div>
      <div style="font-family:'Fraunces',serif; font-size:2rem; font-weight:700; color:{TEXT}; margin:.6rem 0 .2rem 0;">
        {display_label}
      </div>
      <div style="color:{TEXT_FAINT}; font-size:.78rem; margin-bottom:1.3rem;">raw label: {raw_label}</div>
      <div style="background:{BORDER}; border-radius:999px; height:14px; overflow:hidden; margin-bottom:.6rem;">
        <div style="width:{pct}%; height:100%; background:{GRADIENT}; box-shadow:0 0 14px {ACCENT}66;"></div>
      </div>
      <div style="font-family:'Fraunces',serif; font-size:1.5rem; background:{GRADIENT}; -webkit-background-clip:text; background-clip:text; color:transparent; font-weight:700;">{pct}%</div>
      <div style="color:{TEXT_DIM}; font-size:.75rem; text-transform:uppercase; letter-spacing:.1em;">confidence</div>
    </div>
    """, unsafe_allow_html=True)


def top_k_bars(results):
    rows = ""
    for i, (raw, disp, conf) in enumerate(results):
        pct = round(conf * 100, 2)
        rows += f"""
        <div style="margin-bottom:.9rem;">
          <div style="display:flex; justify-content:space-between; font-size:.85rem; margin-bottom:.3rem;">
            <span style="color:{TEXT};">#{i+1} {disp}</span>
            <span style="color:{ACCENT}; font-weight:600;">{pct}%</span>
          </div>
          <div style="background:{BORDER}; border-radius:999px; height:8px; overflow:hidden;">
            <div style="width:{pct}%; height:100%; background:{GRADIENT};"></div>
          </div>
        </div>
        """
    st.markdown(f'<div class="glass-card fade-in">{rows}</div>', unsafe_allow_html=True)


def scanning_overlay_note():
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:.6rem; color:{ACCENT}; font-family:'Fraunces',serif;
                font-size:.85rem; margin:.5rem 0;">
      <span style="width:8px;height:8px;border-radius:50%;background:{ACCENT};box-shadow:0 0 10px {ACCENT};
                    animation:pulse 1s ease-in-out infinite;"></span>
      Scanning image…
    </div>
    <style>@keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:.3; }} }}</style>
    """, unsafe_allow_html=True)


def metric_counters(val_acc=94.18, params_m=82.8, classes=260, train_imgs=137221):
    components.html(f"""
    <div style="font-family:'Fraunces',serif; display:flex; gap:1.4rem; flex-wrap:wrap; justify-content:center;">
      <style>
        .mcard {{ background:{BG_ELEV}; border:1px solid {BORDER}; border-radius:16px; padding:1.7rem 2.3rem;
                  text-align:center; min-width:150px; }}
        .mcard b {{ display:block; font-size:2.1rem; background:{GRADIENT}; -webkit-background-clip:text;
                    background-clip:text; color:transparent; }}
        .mcard span {{ font-family:'Inter',sans-serif; color:{TEXT_DIM}; font-size:.75rem; text-transform:uppercase; letter-spacing:.08em; }}
      </style>
      <div class="mcard"><b id="c1">0%</b><span>Val Accuracy</span></div>
      <div class="mcard"><b id="c2">0M</b><span>Parameters</span></div>
      <div class="mcard"><b id="c3">0</b><span>Classes</span></div>
      <div class="mcard"><b id="c4">0K</b><span>Training Images</span></div>
    </div>
    <script>
      function animate(id, end, suffix, decimals) {{
        let el = document.getElementById(id);
        let start = 0; let duration = 1400; let startTime = null;
        function step(ts) {{
          if (!startTime) startTime = ts;
          let progress = Math.min((ts - startTime) / duration, 1);
          let value = start + (end - start) * progress;
          el.innerText = value.toFixed(decimals) + suffix;
          if (progress < 1) requestAnimationFrame(step);
        }}
        requestAnimationFrame(step);
      }}
      animate("c1", {val_acc}, "%", 2);
      animate("c2", {params_m}, "M", 1);
      animate("c3", {classes}, "", 0);
      animate("c4", {train_imgs/1000:.0f}, "K", 0);
    </script>
    """, height=150)


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
    html = ""
    for cat, names in groups.items():
        emoji = produce_emoji(cat)
        chip_html = "".join(f'<span class="chip">{n}</span>' for n in names[:6])
        more = f'<span class="chip">+{len(names)-6} more</span>' if len(names) > 6 else ""
        html += f"""
        <div class="glass-card fade-in" style="margin-bottom:1rem;">
          <div style="font-family:'Fraunces',serif; font-weight:600; color:{TEXT}; margin-bottom:.6rem; font-size:1.05rem;">
            {emoji} {cat} <span style="color:{TEXT_DIM}; font-weight:400; font-size:.8rem;">({len(names)} variant{'s' if len(names) != 1 else ''})</span>
          </div>
          <div>{chip_html}{more}</div>
        </div>
        """
    st.markdown(html, unsafe_allow_html=True)


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
