"""
ui_components.py
------------------
All custom-styled HTML/CSS pieces for the app. Streamlit's default chrome
is overridden globally via inject_global_css(); everything else here
returns HTML strings meant for st.markdown(..., unsafe_allow_html=True)
or components.html(...).

Design system: deep charcoal background, one accent color (electric cyan),
Space Grotesk display font / Inter body font, glassmorphism cards, subtle
glow on interactive elements. Keep new components consistent with these
tokens rather than introducing new colors.
"""

import streamlit as st
import streamlit.components.v1 as components

ACCENT = "#00E5C7"       # electric cyan-green — the one accent color
ACCENT_DIM = "#00E5C733"
BG = "#0A0E14"
BG_ELEV = "#11161F"
BORDER = "#1F2733"
TEXT = "#E6EDF3"
TEXT_DIM = "#8B96A5"


def inject_global_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    #MainMenu, footer, header {{ visibility: hidden; }}
    .block-container {{ padding-top: 0 !important; padding-bottom: 0 !important; max-width: 100% !important; }}
    .stApp {{ background: {BG}; color: {TEXT}; }}

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    h1, h2, h3, h4 {{ font-family: 'Space Grotesk', sans-serif; }}

    ::-webkit-scrollbar {{ width: 10px; }}
    ::-webkit-scrollbar-track {{ background: {BG}; }}
    ::-webkit-scrollbar-thumb {{ background: {BORDER}; border-radius: 6px; }}

    .section {{ padding: 5rem 6vw; max-width: 1200px; margin: 0 auto; }}
    .section-label {{
        color: {ACCENT}; font-family: 'Space Grotesk', sans-serif; font-weight: 600;
        letter-spacing: .2em; text-transform: uppercase; font-size: .75rem; margin-bottom: .75rem;
    }}
    .section-title {{ font-size: 2.2rem; font-weight: 700; margin-bottom: .5rem; color: {TEXT}; }}
    .section-sub {{ color: {TEXT_DIM}; font-size: 1rem; margin-bottom: 2.5rem; max-width: 640px; }}

    .glass-card {{
        background: linear-gradient(180deg, {BG_ELEV} 0%, #0D1219 100%);
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 1.75rem;
        transition: border-color .25s ease, transform .25s ease, box-shadow .25s ease;
    }}
    .glass-card:hover {{
        border-color: {ACCENT}55;
        transform: translateY(-3px);
        box-shadow: 0 12px 32px -12px {ACCENT_DIM};
    }}

    .accent-btn {{
        display: inline-block; background: {ACCENT}; color: #061410 !important;
        font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: .95rem;
        padding: .8rem 1.8rem; border-radius: 10px; text-decoration: none !important;
        box-shadow: 0 0 24px {ACCENT_DIM}; transition: transform .2s ease, box-shadow .2s ease;
    }}
    .accent-btn:hover {{ transform: translateY(-2px); box-shadow: 0 0 36px {ACCENT}66; }}
    .ghost-btn {{
        display: inline-block; background: transparent; color: {TEXT} !important;
        font-family: 'Space Grotesk', sans-serif; font-weight: 600; font-size: .95rem;
        padding: .78rem 1.8rem; border-radius: 10px; text-decoration: none !important;
        border: 1px solid {BORDER}; transition: border-color .2s ease, color .2s ease;
    }}
    .ghost-btn:hover {{ border-color: {ACCENT}; color: {ACCENT} !important; }}

    .chip {{
        display: inline-block; background: {BG_ELEV}; border: 1px solid {BORDER};
        color: {TEXT_DIM}; font-size: .78rem; padding: .35rem .8rem; border-radius: 999px;
        margin: .2rem; transition: all .2s ease;
    }}
    .chip:hover {{ border-color: {ACCENT}; color: {ACCENT}; }}

    /* Streamlit widget restyle */
    div[data-testid="stFileUploader"] {{
        background: {BG_ELEV}; border: 1.5px dashed {BORDER}; border-radius: 14px; padding: 1rem;
    }}
    .stProgress > div > div > div > div {{ background-color: {ACCENT}; }}
    </style>
    """, unsafe_allow_html=True)


def hero_section():
    components.html(f"""
    <div style="font-family:'Space Grotesk',sans-serif;">
    <style>
      .hero {{ position:relative; width:100%; height:92vh; background:{BG}; overflow:hidden;
               display:flex; flex-direction:column; align-items:center; justify-content:center;
               border-bottom:1px solid {BORDER}; }}
      .grid-bg {{ position:absolute; inset:0;
        background-image: linear-gradient({BORDER} 1px, transparent 1px), linear-gradient(90deg, {BORDER} 1px, transparent 1px);
        background-size: 42px 42px; opacity:.35; }}
      .scan-line {{ position:absolute; left:0; width:100%; height:2px;
        background: linear-gradient(90deg, transparent, {ACCENT}, transparent);
        box-shadow: 0 0 20px 4px {ACCENT}99; animation: scan 4.5s ease-in-out infinite; }}
      @keyframes scan {{ 0% {{ top:8%; opacity:0; }} 10% {{ opacity:1; }} 90% {{ opacity:1; }} 100% {{ top:92%; opacity:0; }} }}

      .bbox {{ position:absolute; border:1.5px solid {ACCENT}; border-radius:6px; opacity:0;
        animation: bboxIn 1s ease forwards; box-shadow: 0 0 18px {ACCENT_DIM}; }}
      .bbox span {{ position:absolute; top:-1.4rem; left:0; font-size:.7rem; color:{ACCENT};
        background:{BG}; padding:1px 6px; border:1px solid {ACCENT}55; border-radius:4px; white-space:nowrap; }}
      @keyframes bboxIn {{ 0% {{ opacity:0; transform:scale(1.08); }} 100% {{ opacity:1; transform:scale(1); }} }}

      .b1 {{ top:22%; left:14%; width:150px; height:110px; animation-delay:.3s; }}
      .b2 {{ top:58%; left:68%; width:120px; height:90px; animation-delay:1.1s; }}
      .b3 {{ top:14%; left:64%; width:95px; height:95px; animation-delay:1.9s; }}
      .b4 {{ top:66%; left:20%; width:110px; height:80px; animation-delay:2.6s; }}

      .hero-content {{ position:relative; z-index:5; text-align:center; padding:0 1.5rem; max-width:820px; }}
      .kicker {{ color:{ACCENT}; letter-spacing:.25em; text-transform:uppercase; font-size:.75rem; font-weight:600; margin-bottom:1.2rem; }}
      .headline {{ font-size:clamp(2.1rem, 5vw, 3.6rem); font-weight:700; color:{TEXT}; line-height:1.15; margin:0 0 1.1rem 0; }}
      .headline .accent {{ color:{ACCENT}; }}
      .sub {{ color:{TEXT_DIM}; font-family:'Inter',sans-serif; font-size:1.05rem; line-height:1.6; margin-bottom:2.2rem; }}
      .stat-row {{ display:flex; gap:2.2rem; justify-content:center; margin-bottom:2.4rem; flex-wrap:wrap; }}
      .stat {{ text-align:center; }}
      .stat b {{ display:block; font-size:1.6rem; color:{ACCENT}; }}
      .stat span {{ font-family:'Inter',sans-serif; font-size:.75rem; color:{TEXT_DIM}; text-transform:uppercase; letter-spacing:.08em; }}
      .cta-row {{ display:flex; gap:1rem; justify-content:center; flex-wrap:wrap; }}
      .accent-btn {{ background:{ACCENT}; color:#061410; font-weight:700; padding:.85rem 1.9rem;
        border-radius:10px; text-decoration:none; box-shadow:0 0 26px {ACCENT_DIM}; font-family:'Space Grotesk',sans-serif; }}
      .ghost-btn {{ background:transparent; color:{TEXT}; font-weight:600; padding:.83rem 1.9rem;
        border-radius:10px; text-decoration:none; border:1px solid {BORDER}; font-family:'Space Grotesk',sans-serif; }}
      .scroll-cue {{ position:absolute; bottom:2rem; left:50%; transform:translateX(-50%); color:{TEXT_DIM};
        font-size:.7rem; letter-spacing:.15em; text-transform:uppercase; animation:bob 2s ease-in-out infinite; }}
      @keyframes bob {{ 0%,100% {{ transform:translate(-50%,0); }} 50% {{ transform:translate(-50%,8px); }} }}
    </style>

    <div class="hero">
      <div class="grid-bg"></div>
      <div class="scan-line"></div>
      <div class="bbox b1"><span>produce · 0.94</span></div>
      <div class="bbox b2"><span>produce · 0.88</span></div>
      <div class="bbox b3"><span>produce · 0.91</span></div>
      <div class="bbox b4"><span>produce · 0.86</span></div>

      <div class="hero-content">
        <div class="kicker">CNN · Retail Product Recognition · ITI Computer Vision</div>
        <h1 class="headline">A CNN built <span class="accent">from scratch</span>,<br/>260 product categories,<br/><span class="accent">94.18%</span> validation accuracy</h1>
        <p class="sub">A from-scratch convolutional network trained on a 260-category fresh-produce dataset —
        a proof-of-concept for automated product recognition across retail shelf, checkout, and inventory pipelines.</p>
        <div class="stat-row">
          <div class="stat"><b>82.8M</b><span>Parameters</span></div>
          <div class="stat"><b>260</b><span>Classes</span></div>
          <div class="stat"><b>137K</b><span>Training Images</span></div>
        </div>
        <div class="cta-row">
          <a class="accent-btn" href="#live-demo" target="_parent">Try the live demo ↓</a>
          <a class="ghost-btn" href="https://github.com/Yasser-Mogahed/Retail-Product-Recognition-System-Computer-Vision-ITI" target="_blank">View on GitHub</a>
        </div>
      </div>
      <div class="scroll-cue">Scroll to explore ⌄</div>
    </div>
    </div>
    """, height=760, scrolling=False)


def prediction_card(display_label: str, raw_label: str, confidence: float):
    pct = round(confidence * 100, 2)
    st.markdown(f"""
    <div class="glass-card" style="text-align:center; padding:2.2rem 1.5rem;">
      <div class="section-label" style="margin-bottom:.4rem;">Top Prediction</div>
      <div style="font-family:'Space Grotesk',sans-serif; font-size:1.9rem; font-weight:700; color:{TEXT}; margin-bottom:.2rem;">
        {display_label}
      </div>
      <div style="color:{TEXT_DIM}; font-size:.8rem; margin-bottom:1.2rem;">raw label: {raw_label}</div>
      <div style="background:{BORDER}; border-radius:999px; height:14px; overflow:hidden; margin-bottom:.6rem;">
        <div style="width:{pct}%; height:100%; background:linear-gradient(90deg, {ACCENT}88, {ACCENT}); box-shadow:0 0 12px {ACCENT_DIM};"></div>
      </div>
      <div style="font-family:'Space Grotesk',sans-serif; font-size:1.4rem; color:{ACCENT}; font-weight:700;">{pct}%</div>
      <div style="color:{TEXT_DIM}; font-size:.75rem; text-transform:uppercase; letter-spacing:.1em;">confidence</div>
    </div>
    """, unsafe_allow_html=True)


def top_k_bars(results):
    """results: list of (raw_label, display_label, confidence) sorted descending, excluding rank 1 if desired."""
    rows = ""
    for i, (raw, disp, conf) in enumerate(results):
        pct = round(conf * 100, 2)
        rows += f"""
        <div style="margin-bottom:.85rem;">
          <div style="display:flex; justify-content:space-between; font-size:.85rem; margin-bottom:.3rem;">
            <span style="color:{TEXT};">#{i+1} {disp}</span>
            <span style="color:{ACCENT}; font-weight:600;">{pct}%</span>
          </div>
          <div style="background:{BORDER}; border-radius:999px; height:8px; overflow:hidden;">
            <div style="width:{pct}%; height:100%; background:{ACCENT};"></div>
          </div>
        </div>
        """
    st.markdown(f'<div class="glass-card">{rows}</div>', unsafe_allow_html=True)


def scanning_overlay_note():
    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:.6rem; color:{ACCENT}; font-family:'Space Grotesk',sans-serif;
                font-size:.85rem; margin:.5rem 0;">
      <span style="width:8px;height:8px;border-radius:50%;background:{ACCENT};box-shadow:0 0 8px {ACCENT};
                    animation:pulse 1s ease-in-out infinite;"></span>
      Scanning image…
    </div>
    <style>@keyframes pulse {{ 0%,100% {{ opacity:1; }} 50% {{ opacity:.3; }} }}</style>
    """, unsafe_allow_html=True)


def metric_counters(val_acc=94.18, params_m=82.8, classes=260, train_imgs=137221):
    components.html(f"""
    <div style="font-family:'Space Grotesk',sans-serif; display:flex; gap:1.5rem; flex-wrap:wrap; justify-content:center;">
      <style>
        .mcard {{ background:{BG_ELEV}; border:1px solid {BORDER}; border-radius:14px; padding:1.6rem 2.2rem;
                  text-align:center; min-width:150px; }}
        .mcard b {{ display:block; font-size:2rem; color:{ACCENT}; }}
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
        ("05", "Prediction", "argmax gives the top class; full softmax vector powers the top-k confidence ranking."),
    ]
    cols = st.columns(len(steps))
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="min-height:220px;">
              <div style="color:{ACCENT}; font-family:'Space Grotesk',sans-serif; font-size:1.3rem; font-weight:700; margin-bottom:.6rem;">{num}</div>
              <div style="font-family:'Space Grotesk',sans-serif; font-weight:600; margin-bottom:.5rem;">{title}</div>
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
            <div class="glass-card">
              <div style="font-family:'Space Grotesk',sans-serif; color:{ACCENT}; font-weight:600; margin-bottom:.5rem;">{title}</div>
              <div style="color:{TEXT_DIM}; font-size:.85rem; line-height:1.55;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def class_showcase(groups: dict):
    html = ""
    for cat, names in groups.items():
        chip_html = "".join(f'<span class="chip">{n}</span>' for n in names[:6])
        more = f'<span class="chip">+{len(names)-6} more</span>' if len(names) > 6 else ""
        html += f"""
        <div class="glass-card" style="margin-bottom:1rem;">
          <div style="font-family:'Space Grotesk',sans-serif; font-weight:600; color:{TEXT}; margin-bottom:.6rem;">
            {cat} <span style="color:{TEXT_DIM}; font-weight:400; font-size:.8rem;">({len(names)} variant{'s' if len(names) != 1 else ''})</span>
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
    <div style="border-top:1px solid {BORDER}; padding:3rem 6vw; text-align:center;">
      <div class="section-label">Retail Product Recognition System</div>
      <p style="color:{TEXT_DIM}; font-size:.85rem; margin-bottom:1.2rem;">
        A graduation project from the ITI Computer Vision track.
      </p>
      <div style="margin-bottom:1.5rem;">{team_html}</div>
      <a class="ghost-btn" href="https://github.com/Yasser-Mogahed/Retail-Product-Recognition-System-Computer-Vision-ITI" target="_blank">
        ↗ View source on GitHub
      </a>
      <p style="color:{TEXT_DIM}; font-size:.72rem; margin-top:2rem;">
        Add your portfolio / LinkedIn links in <code>ui_components.py → footer_section()</code>.
      </p>
    </div>
    """, unsafe_allow_html=True)
