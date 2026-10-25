"""
ui_components.py
------------------
Shared design system for the multi-page app. Every page calls
inject_global_css() first, then top_nav(active=...) — except the landing
page, which stays nav-free and immersive on purpose.

THEME SYSTEM: Streamlit's own theming (.streamlit/config.toml) is static —
set once at startup, not something a user can toggle at runtime. Instead,
the current theme ("dark" or "light") lives in st.session_state, and
_apply_theme() (called at the top of inject_global_css()) reassigns this
module's color globals (ACCENT, BG, TEXT, etc.) based on it. Because every
color reference throughout the app — in this file and in every view file,
via `ui.ACCENT` etc. — reads the module's CURRENT global value rather than
a value captured at import time, this one reassignment is enough to
retheme the whole app. No other file needs to change. The only exception
is derived string constants (GRADIENT, GRADIENT_LEAF), which are rebuilt
inside _apply_theme() too, since string concatenation doesn't "follow"
its inputs after the fact the way a live reference would.

DESIGN TOKENS (do not introduce new colors elsewhere — reuse these):
  Dark theme : cool neutral dark slate (not brown/orange, not gloomy)
  Light theme: soft warm cream (not stark white, not washed-out pastel) —
               "juicy" comes from deep saturated fruit-color accents
               against that soft background, not from brightness
  Accents    : ACCENT (primary) + ACCENT_DEEP (gradient partner), plus
               ACCENT_YELLOW / ACCENT_BLUE / ACCENT_PURPLE / ACCENT2 /
               ACCENT_TOMATO for variety in labels, chips, bounding boxes
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
import metrics as M

# ---- Theme palettes ----------------------------------------------------
# Dark: cool neutral slate, produce colors as accents (unchanged from before).
DARK_THEME = dict(
    ACCENT="#2DD4A7", ACCENT_DEEP="#0EA5E9", ACCENT2="#FBBF24",
    ACCENT_YELLOW="#FACC15", ACCENT_BLUE="#60A5FA", ACCENT_PURPLE="#A78BFA",
    ACCENT_TOMATO="#FB7161",
    BG="#10141C", BG_ELEV="#181E2A", BG_ELEV_2="#1E2534", BORDER="#2C3346",
    TEXT="#EEF2F8", TEXT_DIM="#98A2B8", TEXT_FAINT="#5C6478",
    BLOB_OPACITY=1.0, GRAIN_OPACITY=1.0,
)
# Light: soft warm cream (not white, not pastel-washed) + deep saturated
# "juicy" fruit-jewel-tone accents — the richness comes from saturation,
# not from being bright. Blobs/grain toned down since bright ambient glow
# reads as "too colorful" rather than "juicy" against a light background.
LIGHT_THEME = dict(
    ACCENT="#1FA971", ACCENT_DEEP="#0C7FBF", ACCENT2="#E0A812",
    ACCENT_YELLOW="#D6971A", ACCENT_BLUE="#1E88C7", ACCENT_PURPLE="#8A4FD1",
    ACCENT_TOMATO="#E1432A",
    BG="#FBF3E6", BG_ELEV="#FFFFFF", BG_ELEV_2="#FFF8EE", BORDER="#E8D9BE",
    TEXT="#2E2013", TEXT_DIM="#7C6A52", TEXT_FAINT="#A99878",
    BLOB_OPACITY=0.45, GRAIN_OPACITY=0.6,
)

# Confidence-based color system — kept constant across themes; these are
# semantic (pass/warn/fail) rather than decorative.
CONF_HIGH = "#34D399"    # >90%
CONF_MID = "#FBBF24"     # 70-90%
CONF_LOW = "#F87171"     # <70%


def get_theme() -> str:
    """Current theme name, defaulting to dark. Persists across page
    navigation automatically since it lives in st.session_state, which
    is shared across the whole multi-page session."""
    return st.session_state.get("theme", "dark")


def _apply_theme():
    """Reassigns this module's color globals based on the current theme.
    Must be called before any code in this script run references a color
    token — inject_global_css() does this first thing, which is why every
    page calls it before anything else."""
    global ACCENT, ACCENT_DEEP, ACCENT2, ACCENT_YELLOW, ACCENT_BLUE, ACCENT_PURPLE, ACCENT_TOMATO
    global BG, BG_ELEV, BG_ELEV_2, BORDER, TEXT, TEXT_DIM, TEXT_FAINT
    global GRADIENT, GRADIENT_LEAF, BLOB_OPACITY, GRAIN_OPACITY

    palette = LIGHT_THEME if get_theme() == "light" else DARK_THEME
    ACCENT = palette["ACCENT"]
    ACCENT_DEEP = palette["ACCENT_DEEP"]
    ACCENT2 = palette["ACCENT2"]
    ACCENT_YELLOW = palette["ACCENT_YELLOW"]
    ACCENT_BLUE = palette["ACCENT_BLUE"]
    ACCENT_PURPLE = palette["ACCENT_PURPLE"]
    ACCENT_TOMATO = palette["ACCENT_TOMATO"]
    BG = palette["BG"]
    BG_ELEV = palette["BG_ELEV"]
    BG_ELEV_2 = palette["BG_ELEV_2"]
    BORDER = palette["BORDER"]
    TEXT = palette["TEXT"]
    TEXT_DIM = palette["TEXT_DIM"]
    TEXT_FAINT = palette["TEXT_FAINT"]
    BLOB_OPACITY = palette["BLOB_OPACITY"]
    GRAIN_OPACITY = palette["GRAIN_OPACITY"]
    GRADIENT = f"linear-gradient(120deg, {ACCENT}, {ACCENT_DEEP})"
    GRADIENT_LEAF = f"linear-gradient(120deg, {ACCENT}, #22C55E)"


# Module-level defaults so `import ui_components as ui; ui.ACCENT` works
# even before inject_global_css() has run once (e.g. at import time).
_apply_theme()


def theme_toggle_button(key: str = "theme_toggle_btn"):
    """Renders a small button that flips between dark and light theme.
    Calls st.rerun() immediately after updating session_state — without
    it, this script run would finish rendering with the OLD theme's CSS,
    since inject_global_css() (which reads the theme) already ran earlier
    in this same run, before this button was reached."""
    current = get_theme()
    label = "☀️ Light" if current == "dark" else "🌙 Dark"
    if st.button(label, key=key, help="Switch color theme", use_container_width=True):
        st.session_state["theme"] = "light" if current == "dark" else "dark"
        st.rerun()


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


def logo_svg(size: int = 34) -> str:
    """A small original logomark — a scanning/vision ring with a leaf,
    standing in for 'AgroVision' (agriculture + computer vision) — used
    instead of a stock icon or generated image so the brand mark is
    actually original. Colored with the current theme's gradient, so it
    re-themes automatically along with everything else.

    Deliberately returned as ONE LINE with no internal newlines. Streamlit
    runs every st.markdown() body through textwrap.dedent() before
    rendering, which strips the common leading whitespace shared by every
    line in the string. A multi-line return value embedded via an
    f-string — with its own internal lines flush-left — breaks dedent's
    ability to find any common prefix across the WHOLE surrounding
    markdown call, leaving the rest of that call's CSS/HTML at its
    original (4+ space) indentation. That's exactly what makes
    Streamlit's markdown parser misread it as an indented code block and
    render it as literal text. A single-line return value can't cause
    this, regardless of where it's embedded or how indented the
    surrounding content is.
    """
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg">'
        f'<defs><linearGradient id="logoGrad" x1="0" y1="0" x2="34" y2="34">'
        f'<stop stop-color="{ACCENT}"/><stop offset="1" stop-color="{ACCENT_DEEP}"/>'
        f'</linearGradient></defs>'
        f'<circle cx="14" cy="18" r="9.5" stroke="url(#logoGrad)" stroke-width="3"/>'
        f'<line x1="20.7" y1="24.7" x2="28" y2="32" stroke="url(#logoGrad)" stroke-width="3" stroke-linecap="round"/>'
        f'<path d="M14 8.5c-2.5-4-8-4.5-8-4.5s0 5.5 4 7.5c2 1 4-1 4-3z" fill="url(#logoGrad)"/>'
        f'</svg>'
    )


def inject_global_css(full_bleed: bool = False):
    _apply_theme()
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap');

    #MainMenu, footer, header {{ visibility: hidden; }}
    section[data-testid="stSidebar"] {{ display: none; }}
    .block-container {{
        padding-top: 0 !important; padding-bottom: 0 !important;
        padding-left: {"0" if full_bleed else "max(1.25rem, 4.5vw)"} !important;
        padding-right: {"0" if full_bleed else "max(1.25rem, 4.5vw)"} !important;
        max-width: 100% !important;
        {"" if full_bleed else "margin-left: auto !important; margin-right: auto !important;"}
    }}
    /* Streamlit's outer app view also carries its own default padding on
       some versions, independent of .block-container — reset that too so
       full-bleed elements (the hero, aurora background, etc.) genuinely
       reach the true viewport edges instead of stopping at an inset. */
    [data-testid="stAppViewContainer"] > .main {{ padding: 0 !important; }}
    section[data-testid="stMain"] {{ padding: 0 !important; }}
    .stApp {{ background: {BG}; color: {TEXT}; }}

    html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}
    h1, h2, h3, h4 {{ font-family: 'Fraunces', serif; color: {TEXT}; }}
    p, span, div {{ color: {TEXT}; }}
    label, .stMarkdown, .stMarkdown p {{ color: {TEXT}; }}

    /* Native widget chrome that isn't already overridden elsewhere —
       needed so text_input/selectbox/checkbox/file-uploader/form-buttons
       follow the runtime theme toggle too, not just the custom
       cards/buttons/nav. BaseWeb-based widgets (selectbox especially)
       inject their own internal styles with high specificity, so plain
       rules without !important get silently ignored — everything here
       uses !important plus a wildcard descendant selector to guarantee
       every nested text node actually repaints, not just the outer box. */
    div[data-testid="stTextInput"] input {{
        background: {BG_ELEV} !important; color: {TEXT} !important; border-color: {BORDER} !important;
    }}
    div[data-testid="stTextInput"] input::placeholder {{
        color: {TEXT_FAINT} !important; opacity: 1 !important;
    }}
    div[data-testid="stSelectbox"],
    div[data-testid="stSelectbox"] * {{
        background-color: {BG_ELEV} !important;
        color: {TEXT} !important;
        fill: {TEXT} !important;
        border-color: {BORDER} !important;
    }}
    /* BaseWeb renders the OPEN dropdown list as a portal appended
       elsewhere in the DOM — it is not a descendant of stSelectbox at
       all, so the wildcard rule above never reaches it. Previous attempts
       guessed at BaseWeb's exact attribute VALUES (data-baseweb="menu",
       role="listbox"), which apparently don't match this version. Using
       attribute-EXISTS selectors instead — [data-baseweb], [role] — casts
       a much wider net that doesn't depend on knowing the exact value. */
    [data-baseweb],
    [data-baseweb] *,
    [role="listbox"], [role="option"], [role="menu"], [role="menuitem"],
    [role="listbox"] *, [role="option"] *, [role="menu"] *, [role="menuitem"] * {{
        background-color: {BG_ELEV} !important;
        color: {TEXT} !important;
        border-color: {BORDER} !important;
        fill: {TEXT} !important;
    }}
    [role="option"]:hover, [role="option"][aria-selected="true"],
    [role="menuitem"]:hover {{
        background-color: {BG_ELEV_2} !important;
    }}
    div[data-testid="stForm"] {{ border-color: {BORDER} !important; background: transparent !important; }}

    /* st.code() uses its own fixed syntax-highlighting theme, entirely
       independent of the app's light/dark setting or config.toml — it
       needs an explicit override or it stays permanently dark. */
    div[data-testid="stCode"], div[data-testid="stCode"] *,
    div[data-testid="stCodeBlock"], div[data-testid="stCodeBlock"] *,
    div[data-testid="stCode"] pre, div[data-testid="stCodeBlock"] pre {{
        background-color: {BG_ELEV} !important;
        color: {TEXT} !important;
    }}

    /* Replace the browser's default blue focus/selection ring on nav
       links with a themed one — otherwise clicking a link can leave it
       looking like selected/highlighted text rather than "active page". */
    div[data-testid="stPageLink"] a:focus,
    div[data-testid="stPageLink"] a:focus-visible {{
        outline: none !important; box-shadow: 0 0 0 2px {ACCENT}55 !important;
    }}

    /* File uploader — both the outer card and the inner dropzone Streamlit
       renders as a separate element with its own background. */
    div[data-testid="stFileUploader"],
    div[data-testid="stFileUploader"] *,
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploaderDropzone"] * {{
        background-color: {BG_ELEV} !important; color: {TEXT} !important; border-color: {BORDER} !important;
    }}

    /* Form submit buttons render under a distinct testid from plain
       st.button, and its exact internal structure isn't stable across
       Streamlit versions, so this targets everything under the testid
       rather than a specific child path — same reasoning as selectbox
       above: a precise selector that doesn't match the real DOM makes
       !important irrelevant, since it never gets a chance to compete. */
    div[data-testid="stFormSubmitButton"],
    div[data-testid="stFormSubmitButton"] * {{
        background-color: {BG_ELEV} !important; color: {TEXT} !important; border-color: {BORDER} !important;
    }}
    div[data-testid="stFormSubmitButton"] button {{
        border: 1.5px solid {BORDER} !important; border-radius: 10px !important;
        font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
        transition: all .25s cubic-bezier(.22,.9,.32,1.35) !important;
    }}
    div[data-testid="stFormSubmitButton"] button:hover {{
        border-color: {ACCENT} !important; color: {ACCENT_DEEP} !important;
    }}

    /* Nav page-links: Streamlit nests the label in a <p>, sometimes inside
       further spans, each of which can carry its own muted/secondary text
       color. Force every descendant, not just the direct <a>, or the
       label ends up a washed-out gray on light backgrounds. */
    div[data-testid="stPageLink"] a, div[data-testid="stPageLink"] a * {{
        color: {TEXT} !important;
    }}

    ::-webkit-scrollbar {{ width: 12px; height: 12px; }}
    ::-webkit-scrollbar-track {{ background: {BG}; }}
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, {ACCENT}, {ACCENT_DEEP}); border-radius: 8px;
        border: 3px solid {BG}; background-clip: padding-box;
    }}
    ::-webkit-scrollbar-thumb:hover {{ background: linear-gradient(180deg, {ACCENT_DEEP}, {ACCENT}); background-clip: padding-box; }}
    * {{ scrollbar-color: {ACCENT} {BG}; scrollbar-width: thin; }}

    /* ---- Fresh ambient background, fixed to viewport ----
       Blob/grain opacity is themed: bright colorful glow reads as "juicy"
       against a dark background, but the same intensity against a light
       background reads as "too colorful" rather than juicy — so light
       mode dials both down via BLOB_OPACITY / GRAIN_OPACITY multipliers. */
    .aurora-bg {{
        position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none;
        background: {BG};
    }}
    .aurora-blob {{
        position: absolute; border-radius: 50%; filter: blur(105px);
    }}
    .blob-a {{ width: 620px; height: 620px; background: {ACCENT_YELLOW}; opacity: {round(.30*BLOB_OPACITY,3)}; top: -12%; left: -8%;
               animation: driftA 20s ease-in-out infinite alternate; }}
    .blob-b {{ width: 580px; height: 580px; background: {ACCENT2}; opacity: {round(.28*BLOB_OPACITY,3)}; bottom: -16%; right: -6%;
               animation: driftB 24s ease-in-out infinite alternate; }}
    .blob-c {{ width: 460px; height: 460px; background: {ACCENT}; opacity: {round(.30*BLOB_OPACITY,3)}; top: 40%; right: 14%;
               animation: driftC 28s ease-in-out infinite alternate; }}
    .blob-d {{ width: 380px; height: 380px; background: {ACCENT_PURPLE}; opacity: {round(.22*BLOB_OPACITY,3)}; top: 4%; left: 40%;
               animation: driftB 32s ease-in-out infinite alternate; }}
    .blob-e {{ width: 420px; height: 420px; background: {ACCENT_BLUE}; opacity: {round(.2*BLOB_OPACITY,3)}; bottom: 6%; left: 12%;
               animation: driftC 26s ease-in-out infinite alternate; }}
    @keyframes driftA {{ 0% {{ transform: translate(0,0) scale(1); }} 100% {{ transform: translate(60px,80px) scale(1.15); }} }}
    @keyframes driftB {{ 0% {{ transform: translate(0,0) scale(1); }} 100% {{ transform: translate(-70px,-50px) scale(1.1); }} }}
    @keyframes driftC {{ 0% {{ transform: translate(0,0); }} 100% {{ transform: translate(-40px,60px); }} }}
    .grain-overlay {{
        position: fixed; inset: 0; z-index: -1; pointer-events: none; opacity: {round(.03*GRAIN_OPACITY,4)};
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='120' height='120'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
    }}

    .section {{ padding: 3.5rem {"6vw" if full_bleed else "0"}; max-width: {"1180px" if full_bleed else "none"}; margin: 0 auto; }}
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

    /* Native Streamlit buttons restyled to match custom nav / CTAs.
       !important is needed here — without it, Streamlit's own base button
       styling (driven by the *static* config.toml theme) can still win
       for some properties, which is exactly why the theme-toggle button
       kept a dark background/invisible text even in light mode. */
    [data-testid="stTooltipContent"] {{ background: {BG_ELEV} !important; color: {TEXT} !important; border: 1px solid {BORDER} !important; }}
    [data-testid="stTooltipContent"] * {{ color: {TEXT} !important; }}
    div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button {{
        background: {BG_ELEV} !important; color: {TEXT} !important; border: 1.5px solid {BORDER} !important;
        border-radius: 10px !important; font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
        padding: .5rem 1.1rem !important; transition: all .25s cubic-bezier(.22,.9,.32,1.35) !important;
        font-size: .85rem !important;
    }}
    div[data-testid="stButton"] button *, div[data-testid="stDownloadButton"] button * {{ color: inherit !important; }}
    div[data-testid="stButton"] button:hover, div[data-testid="stDownloadButton"] button:hover {{ border-color: {ACCENT} !important; color: {ACCENT_DEEP} !important; transform: translateY(-2px) scale(1.02); }}
    div[data-testid="stButton"] button:focus:not(:active), div[data-testid="stDownloadButton"] button:focus:not(:active) {{ border-color: {ACCENT} !important; color: {ACCENT_DEEP} !important; }}

    .nav-active > button {{ border-color: {ACCENT} !important; color: {ACCENT_DEEP} !important; background: {ACCENT}18 !important; }}

    /* Primary CTA buttons (st.button(type="primary") / st.link_button) get the full gradient treatment */
    button[kind="primary"], a[data-testid="stBaseLinkButton-primary"] {{
        background: {GRADIENT} !important; color: #FFFBF3 !important; border: none !important;
        font-weight: 700 !important; box-shadow: 0 10px 26px -8px {ACCENT_DEEP}66 !important;
        transition: transform .2s ease, box-shadow .2s ease !important;
        position: relative; overflow: hidden;
    }}
    button[kind="primary"]:hover, a[data-testid="stBaseLinkButton-primary"]:hover {{
        transform: translateY(-2px); box-shadow: 0 14px 34px -8px {ACCENT_DEEP}88 !important;
    }}
    /* Click-ripple: an instant "punch" the moment you press, since we can't
       control timing across the page navigation that follows a click —
       this makes the click itself feel satisfying and immediate, filling
       the gap while Streamlit processes the actual page switch. */
    button[kind="primary"]::after, a[data-testid="stBaseLinkButton-primary"]::after {{
        content: ""; position: absolute; left: 50%; top: 50%; width: 0; height: 0;
        border-radius: 50%; background: rgba(255,255,255,.55); opacity: 0; pointer-events: none;
        transform: translate(-50%, -50%);
        transition: width .5s ease, height .5s ease, opacity .6s ease;
    }}
    button[kind="primary"]:active::after, a[data-testid="stBaseLinkButton-primary"]:active::after {{
        width: 260%; height: 260%; opacity: .5; transition: width 0s, height 0s, opacity 0s;
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

    /* ---- Page/section mount transition — a "coming into focus" feel
       (blur + rise + fade together) rather than a plain fade, so arriving
       at a new page reads as more deliberate. This is also the main
       source of the "smoother Enter the Experience" feel: since we can't
       control timing across an actual page navigation (Streamlit fully
       swaps the page), the payoff is a satisfying materialize on arrival
       instead of a fake pre-navigation delay. ---- */
    .section {{ animation: sectionIn .65s cubic-bezier(.2,.8,.2,1) both; }}
    @keyframes sectionIn {{
        from {{ opacity: 0; transform: translateY(16px); filter: blur(6px); }}
        to   {{ opacity: 1; transform: translateY(0); filter: blur(0); }}
    }}

    /* ---- Responsive breakpoints ---- */
    @media (max-width: 900px) {{
        div[data-testid="stPageLink"] a {{ font-size: .74rem; padding: .45rem .6rem; gap: .25rem; }}
        .section {{ padding: 2.5rem 5vw; }}
        .section-title {{ font-size: 1.8rem; }}
    }}
    @media (max-width: 640px) {{
        div[data-testid="stPageLink"] a p {{ display: none; }}
        .mcard-row {{ gap: .8rem; }}
        .mcard {{ min-width: 120px; padding: 1.2rem 1.4rem; }}
        .tilt-grid {{ grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); }}
    }}

    /* ---- Shimmer skeleton, for the one real load-delay in the app
       (first cold load of model.h5). Shimmer, not a spinner. ---- */
    .skeleton {{ position: relative; overflow: hidden; background: {BG_ELEV}; border: 1px solid {BORDER}; border-radius: 14px; }}
    .skeleton::after {{
        content: ""; position: absolute; inset: 0;
        background: linear-gradient(90deg, transparent, {BORDER}, transparent);
        transform: translateX(-100%); animation: shimmer 1.4s ease-in-out infinite;
    }}
    @keyframes shimmer {{ to {{ transform: translateX(100%); }} }}
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


def skeleton_block(height_px: int = 60, radius_px: int = 14):
    """A shimmering placeholder for the one real load-delay in the app —
    the first cold load of model.h5 (a few seconds before @st.cache_resource
    kicks in for subsequent reruns). Meant to be shown via st.empty() and
    cleared once the real content is ready."""
    st.markdown(
        f'<div class="skeleton" style="height:{height_px}px; border-radius:{radius_px}px;"></div>',
        unsafe_allow_html=True,
    )


def top_nav(active: str):
    """Custom glass top nav bar. `active` is the page filename, e.g. 'demo.py'.

    Uses st.page_link — Streamlit's own purpose-built widget for linking to
    another registered st.Page — instead of a manually-detected st.button
    click + st.switch_page().

    Active-page highlighting note: this used to wrap the active page's
    st.page_link with an opening <div class="nav-active"> in one st.markdown
    call and a closing </div> in another. That doesn't actually nest the
    link inside the div in the real DOM — each st.markdown call's HTML is
    parsed and auto-closed independently (it's set via its own innerHTML
    assignment), so the "wrapping" div silently self-closed as an empty
    sibling and never really contained anything. Fixed below by targeting
    the active column with a positional CSS selector instead, which
    doesn't depend on cross-call nesting at all.
    """
    active_index = None
    for i, (path, _, _) in enumerate(PAGES):
        if path.endswith(active):
            active_index = i
            break
    # Column layout is [brand-spacer, *nav columns, trailing-spacer], and
    # nth-child is 1-indexed, so the brand spacer is nth-child(1) and the
    # first nav column is nth-child(2).
    active_nth = active_index + 2 if active_index is not None else None
    active_css = (
        f'div[data-testid="stHorizontalBlock"] > div:nth-child({active_nth}) '
        f'div[data-testid="stPageLink"] a '
        f'{{ border-color: {ACCENT} !important; color: {ACCENT_DEEP} !important; '
        f'background: {ACCENT}18 !important; }} '
        f'div[data-testid="stHorizontalBlock"] > div:nth-child({active_nth}) '
        f'div[data-testid="stPageLink"] a * '
        f'{{ color: {ACCENT_DEEP} !important; background: transparent !important; }}'
        if active_nth else ""
    )

    st.markdown(f"""
    <style>
      .nav-wrap {{
        position: sticky; top: 0; z-index: 999; backdrop-filter: blur(14px);
        background: {BG}CC; border-bottom: 1px solid {BORDER};
        padding: .9rem 0 .8rem 0; display:flex; align-items:center; justify-content:space-between;
      }}
      .nav-brand {{ font-family:'Fraunces',serif; font-weight:700; font-size:1.05rem; color:{TEXT};
                    display: flex; align-items: center; gap: .5rem; }}
      .nav-brand span {{ background:{GRADIENT}; -webkit-background-clip:text; background-clip:text; color:transparent; }}
      div[data-testid="stPageLink"] {{ width: 100%; }}
      div[data-testid="stPageLink"] a {{
        display: flex; align-items: center; justify-content: center; gap: .4rem; width: 100%;
        background: {BG_ELEV}; color: {TEXT} !important; border: 1.5px solid {BORDER}; border-radius: 10px;
        font-family: 'Inter', sans-serif; font-weight: 600; font-size: .82rem;
        padding: .5rem .6rem; text-decoration: none !important; white-space: nowrap;
        transition: all .25s cubic-bezier(.22,.9,.32,1.35);
      }}
      div[data-testid="stPageLink"] a:hover {{ border-color: {ACCENT}; color: {ACCENT_DEEP} !important; transform: translateY(-2px) scale(1.02); }}
      div[data-testid="stPageLink"] a p {{ color: inherit !important; font-weight: 600 !important; }}
      {active_css}
    </style>
    <div class="nav-wrap">
      <div class="nav-brand">{logo_svg(26)} Agro<span>Vision</span></div>
    </div>
    """, unsafe_allow_html=True)

    _, *cols_and_pad = st.columns([1.1] + [1] * len(PAGES) + [0.8])
    cols = cols_and_pad[:len(PAGES)]
    toggle_col = cols_and_pad[len(PAGES)]
    for col, (path, label, icon) in zip(cols, PAGES):
        with col:
            st.page_link(path, label=label, icon=icon, use_container_width=True)
    with toggle_col:
        theme_toggle_button(key="theme_toggle_nav")
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
        emoji = produce_emoji(disp.split(" ")[0].capitalize())
        bar_html = f"""
        <div style="margin-bottom:.9rem;">
          <div style="display:flex; justify-content:space-between; font-size:.85rem; margin-bottom:.3rem;">
            <span style="color:{TEXT};">#{i+1} {emoji} {disp}</span>
            <span style="color:{color}; font-weight:600;">{pct}%</span>
          </div>
          <div style="background:{BORDER}; border-radius:999px; height:8px; overflow:hidden;">
            <div class="bar-fill" style="--bar-w:{pct}%; background:{color}; animation-delay:{delay}s;"></div>
          </div>
        </div>
        """
        # .strip() prevents the same blank-line-becomes-code-block bug as
        # class_showcase above — without it, bars after the first render
        # as literal text instead of HTML.
        rows += bar_html.strip()
    st.markdown(f"""
    <style>
    .bar-fill {{ height: 100%; width: 0%; border-radius: 999px;
      animation: barGrow .75s cubic-bezier(.2,.8,.2,1) forwards; }}
    @keyframes barGrow {{ from {{ width: 0%; }} to {{ width: var(--bar-w); }} }}
    </style>
    <div class="glass-card">{rows}</div>
    """, unsafe_allow_html=True)


def metric_counters(val_acc=M.TEST_ACC, params_m=round(M.TOTAL_PARAMS / 1e6, 1), classes=M.NUM_CLASSES,
                    train_imgs=M.TOTAL_TRAIN_FOLDER_IMGS):
    """Renders four metric cards whose numbers count up from 0 as they
    scroll into view — pure CSS, no JS, no iframe. Uses the same
    animation-timeline: view() technique as .reveal-up, combined with an
    animated integer custom property driving a CSS counter().

    CSS counters only support integers, so each metric is split into an
    animated integer part (0 -> 87, 0 -> 4, etc.) plus a static suffix
    appended after ('.81%', '.4M', 'K') — the count-up motion reads the
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
    imgs_int, imgs_suffix = round(train_imgs / 1000), "K"

    metrics = [
        ("c1", acc_int, acc_suffix, "Test Accuracy"),
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
        ("01", "Raw Image", f"Native 100×100 RGB photo resized to {M.IMG_SIZE}×{M.IMG_SIZE}. Raw 0–255 pixels go straight in — no /255 rescaling."),
        ("02", "Augment (train only)", "White studio background swapped ~50% of the time, plus flip, rotation, zoom, shift, brightness/contrast jitter and sensor noise."),
        ("03", "EfficientNetB0", f"ImageNet-pretrained backbone ({M.BACKBONE_PARAMS / 1e6:.2f}M params), frozen first, then the top 30 layers fine-tuned."),
        ("04", f"{M.NUM_CLASSES}-Class Head", f"Global average pooling → Dropout 0.3 → Dense 256 → Dropout 0.2 → {M.NUM_CLASSES}-way softmax."),
        ("05", "Prediction", "argmax gives the top class; the full softmax vector powers the top-k confidence ranking."),
    ]
    cols = st.columns(len(steps))
    for i, (col, (num, title, desc)) in enumerate(zip(cols, steps)):
        with col:
            st.markdown(f"""
            <div class="glass-card reveal-up" style="min-height:230px; animation-delay:{i * 0.08}s;">
              <div style="background:{GRADIENT}; -webkit-background-clip:text; background-clip:text; color:transparent;
                          font-family:'Fraunces',serif; font-size:1.4rem; font-weight:700; margin-bottom:.6rem;">{num}</div>
              <div style="font-family:'Fraunces',serif; font-weight:600; margin-bottom:.5rem;">{title}</div>
              <div style="color:{TEXT_DIM}; font-size:.82rem; line-height:1.5;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def insight_callouts():
    insights = [
        ("Honest headline", f"{M.TEST_ACC:.2f}% on the {M.TEST_IMGS:,}-image held-out test set. Validation peaked higher ({M.BEST_VAL_ACC:.2f}%) because it is a random split of the training folders, where near-identical rotations of the same fruit appear on both sides."),
        ("Fine-tuning plateaued", f"Unfreezing the top 30 backbone layers added no gain: validation stayed at ~{M.P2_VAL_ACC[0]:.1f}% and early stopping ended phase 2 after {M.P2_EPOCHS} epochs. The head, not the backbone, was the limit."),
        ("What's next", f"{M.CLASSES_F1_BELOW_60} classes score F1 < 0.60 (the Blackberry and Cherry variants, Cantaloupe 2, Apple Crimson Snow). Next: targeted data for those, real-photo backgrounds, and a larger EfficientNet at higher resolution."),
    ]
    cols = st.columns(3)
    for i, (col, (title, desc)) in enumerate(zip(cols, insights)):
        with col:
            st.markdown(f"""
            <div class="glass-card reveal-up" style="animation-delay:{i * 0.1}s;">
              <div style="font-family:'Fraunces',serif; color:{ACCENT}; font-weight:600; margin-bottom:.5rem;">{title}</div>
              <div style="color:{TEXT_DIM}; font-size:.85rem; line-height:1.55;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


def class_showcase(groups: dict, show_all: bool = False):
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
        limit = len(names) if show_all else 6
        chip_html = "".join(f'<span class="chip">{n}</span>' for n in names[:limit])
        if len(names) > limit:
            rest = "".join(f'<span class="chip">{n}</span>' for n in names[6:])
            more = (
                f'<details class="more-wrap"><summary class="chip more-chip">'
                f'<span class="t-more">+{len(names) - 6} more</span><span class="t-less">Show less</span></summary>'
                f'<div class="more-body">{rest}</div></details>'
            )
        else:
            more = ""
        card_html = f"""
        <div class="glass-card tilt-card fade-in">
          <div style="font-family:'Fraunces',serif; font-weight:600; color:{TEXT}; margin-bottom:.6rem; font-size:1.05rem;">
            {emoji} {cat} <span style="color:{TEXT_DIM}; font-weight:400; font-size:.8rem;">({len(names)} variant{'s' if len(names) != 1 else ''})</span>
          </div>
          <div>{chip_html}{more}</div>
        </div>
        """
        # .strip() is essential here: without it, concatenating multiple
        # blocks leaves a whitespace-only line between each card, which
        # Streamlit's markdown parser reads as "blank line followed by an
        # indented line" and renders as literal code text instead of HTML.
        cards += card_html.strip()
    st.markdown(f"""
    <style>
    .tilt-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 1rem; }}
    .more-wrap {{ margin-top: .15rem; }}
    .more-wrap > summary {{ list-style: none; cursor: pointer; user-select: none; display: inline-block;
        border-color: {ACCENT}66 !important; color: {ACCENT_DEEP} !important; font-weight: 600; }}
    .more-wrap > summary::-webkit-details-marker {{ display: none; }}
    .more-wrap > summary:hover {{ background: {ACCENT}22; }}
    .more-wrap .t-less {{ display: none; }}
    .more-wrap[open] .t-less {{ display: inline; }}
    .more-wrap[open] .t-more {{ display: none; }}
    .more-body {{ margin-top: .45rem; }}
    .glass-card.tilt-card {{ perspective: 700px; }}
    .glass-card.tilt-card:hover {{
        transform: translateY(-4px);
        border-color: {ACCENT}88; box-shadow: 0 22px 46px -18px {ACCENT}40, inset 0 1px 0 rgba(255,255,255,.04);
    }}
    </style>
    <div class="tilt-grid">{cards}</div>
    """, unsafe_allow_html=True)


def footer_section():
    """Slim footer: brand, track, one source link. The full team lives on the About page."""
    st.markdown(f"""
    <div style="border-top:1px solid {BORDER}; padding:2.2rem 6vw 2.6rem 6vw; text-align:center; margin-top:2rem;">
      <div class="section-label">AgroVision</div>
      <p style="color:{TEXT_DIM}; font-size:.85rem; margin:.8rem 0 1.2rem 0;">
        A graduation project from the ITI {M.TRACK}.
      </p>
      <a class="ghost-btn" href="{M.REPO_URL}" target="_blank" rel="noopener">↗ View source on GitHub</a>
    </div>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Produce type badge + per-image result card (multi-image demo)
# ---------------------------------------------------------------------------
TYPE_STYLE = {
    "Fruit": ("🍎", "#F43F5E"),
    "Vegetable": ("🥦", "#22C55E"),
    "Nut": ("🥜", "#D9A441"),
}


def type_badge_html(ptype: str) -> str:
    emoji, color = TYPE_STYLE.get(ptype, ("🌿", ACCENT))
    return (f'<span style="display:inline-block; padding:.22rem .7rem; border-radius:999px; font-size:.72rem; '
            f'font-weight:700; letter-spacing:.08em; text-transform:uppercase; color:{color}; '
            f'background:{rgba(color, 0.14)}; border:1px solid {rgba(color, 0.45)};">{emoji} {ptype}</span>')


def image_result_card(pil_image, filename: str, results, ptype: str, index: int = 0) -> str:
    """One self-contained card for a single scanned image: thumbnail, name,
    Fruit/Vegetable/Nut badge, confidence bar and two runner-ups. Returns a
    single-line-per-block HTML string (no blank lines, dedent-safe)."""
    raw, disp, conf = results[0]
    pct = round(conf * 100, 1)
    color = confidence_color(pct)
    uri = image_to_data_uri(pil_image, max_dim=360)
    alts = "".join(
        f'<div style="display:flex; justify-content:space-between; font-size:.74rem; color:{TEXT_DIM};">'
        f'<span>{d}</span><span>{round(c * 100, 1)}%</span></div>'
        for _, d, c in results[1:3]
    )
    return (
        f'<div class="glass-card reveal-up" style="padding:1rem; animation-delay:{min(index, 8) * 0.07}s; height:100%;">'
        f'<div style="border-radius:12px; overflow:hidden; background:{BG}; aspect-ratio:1/1; margin-bottom:.8rem;">'
        f'<img src="{uri}" style="width:100%; height:100%; object-fit:contain; display:block;"/></div>'
        f'<div style="color:{TEXT_DIM}; font-size:.78rem; font-weight:600; letter-spacing:.04em; margin-bottom:.35rem;">Image {index + 1}</div>'
        f'<div style="font-family:\'Fraunces\',serif; font-size:1.25rem; font-weight:700; color:{TEXT}; margin-bottom:.45rem;">{disp}</div>'
        f'<div style="margin-bottom:.7rem;">{type_badge_html(ptype)}</div>'
        f'<div style="background:{BORDER}; border-radius:999px; height:9px; overflow:hidden; margin-bottom:.35rem;">'
        f'<div style="width:{pct}%; height:100%; background:linear-gradient(90deg, {rgba(color, 0.6)}, {color});"></div></div>'
        f'<div style="color:{color}; font-weight:700; font-size:.9rem; margin-bottom:.55rem;">{pct}% confidence</div>'
        f'{alts}</div>'
    )
