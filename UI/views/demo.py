"""
views/demo.py
---------------
Live inference page. Looks for model.h5 in the project root, NoteBook/,
or assets/ (see model_utils.find_model_path). If it's missing, shows a
clear inline notice instead of crashing — nav and page chrome still work.

Note: there's no artificial time.sleep() here anymore. The "scan, then
reveal" feel comes entirely from CSS animation-delay staggering across
three pieces — the vision-scan frame, the prediction card, and the top-k
bars — that all render in the same script run. Inference itself runs
immediately; the sequencing is purely visual. This also means a new
image reruns the script and remounts these elements with fresh content
each time, so the scan sequence naturally replays for every new
prediction — which is exactly the behavior we want here.
"""

import os
import streamlit as st
from PIL import Image

import ui_components as ui
from model_utils import find_model_path, load_prediction_model, predict_top_k

ui.inject_global_css()
ui.top_nav(active="demo.py")

st.markdown('<div class="section">', unsafe_allow_html=True)
st.markdown('<div class="section-label">Live Demo</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Run the model yourself</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Upload a produce image or pick a sample below. Inference runs the exact '
    'preprocessing pipeline the model was trained on: 128×128 resize, RGB, raw 0–255 pixels (EfficientNet normalises internally).</div>',
    unsafe_allow_html=True,
)

model_path = find_model_path()
model = None
model_load_error = None
if model_path:
    # Shown only while the model is actually loading — @st.cache_resource
    # means this is a real, visible delay only on the very first cold load
    # (deserializing an 82M-parameter model can take a few seconds);
    # cached reruns clear it almost instantly.
    loading_placeholder = st.empty()
    with loading_placeholder:
        ui.skeleton_block(height_px=52)
    try:
        model = load_prediction_model(model_path)
    except Exception as e:  # noqa: BLE001 - surface any load failure to the UI
        model_load_error = str(e)
    loading_placeholder.empty()

if model is None:
    st.markdown(f"""
    <div class="glass-card" style="border-color:#EF444455;">
      <div style="color:#EF4444; font-family:'Fraunces',serif; font-weight:600; margin-bottom:.5rem;">
        ⚠ Model weights not found
      </div>
      <div style="color:{ui.TEXT_DIM}; font-size:.88rem; line-height:1.6;">
        No <code>model.h5</code> was found in the project root, <code>NoteBook/</code>, or <code>assets/</code>.
        The demo can't run predictions without it — the rest of the app still works.
        <br/><br/>
        <b>To fix:</b> drop your trained <code>model.h5</code> into the project root, or run
        <code>python train.py</code> (see <code>README.md</code>) if you have the Fruits-360 dataset locally.
        {f'<br/><br/><i>Load error: {model_load_error}</i>' if model_load_error else ''}
      </div>
    </div>
    """, unsafe_allow_html=True)
else:
    sample_dir = os.path.join("assets", "samples")
    sample_files = []
    if os.path.isdir(sample_dir):
        sample_files = sorted(
            f for f in os.listdir(sample_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        )

    col_upload, col_samples = st.columns([1.1, 1])
    with col_upload:
        uploaded = st.file_uploader("Upload a product image", type=["png", "jpg", "jpeg"])

    chosen_image = None
    chosen_source = None

    with col_samples:
        if sample_files:
            st.markdown(
                f'<div style="color:{ui.TEXT_DIM}; font-size:.85rem; margin-bottom:.5rem;">'
                f'Or try a sample:</div>', unsafe_allow_html=True
            )
            sample_cols = st.columns(min(4, len(sample_files)))
            for i, fname in enumerate(sample_files[:8]):
                with sample_cols[i % len(sample_cols)]:
                    img_path = os.path.join(sample_dir, fname)
                    st.image(img_path, use_column_width=True)
                    if st.button("Use this", key=f"sample_{fname}"):
                        st.session_state["chosen_sample"] = img_path
        else:
            st.markdown(f"""
            <div class="glass-card" style="font-size:.82rem; color:{ui.TEXT_DIM};">
              No sample images bundled yet. Drop a few Fruits-360 test images into
              <code>assets/samples/</code> (any produce class works) to enable one-click trials here.
            </div>
            """, unsafe_allow_html=True)

    if uploaded is not None:
        chosen_image = Image.open(uploaded)
        chosen_source = uploaded.name
    elif st.session_state.get("chosen_sample"):
        chosen_image = Image.open(st.session_state["chosen_sample"])
        chosen_source = os.path.basename(st.session_state["chosen_sample"])

    if chosen_image is not None:
        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)
        img_col, result_col = st.columns([1, 1.3])

        # Inference runs immediately — no artificial delay. The visual
        # "scan, then reveal" sequencing below is entirely animation-delay.
        results = predict_top_k(model, chosen_image, k=5)
        top_raw, top_disp, top_conf = results[0]

        with img_col:
            ui.vision_scan_frame(chosen_image, caption=chosen_source, scan_delay=0.0)

        with result_col:
            ui.prediction_card(top_disp, top_raw, top_conf, reveal_delay=1.9)

        st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="color:{ui.TEXT_DIM}; font-size:.85rem; margin-bottom:.6rem;">Top-5 predictions</div>',
            unsafe_allow_html=True,
        )
        ui.top_k_bars(results, reveal_delay=2.2)

        # Copy-able result — st.code ships its own native copy button, so
        # this needs no custom clipboard JS (which wouldn't reliably run
        # inside st.markdown anyway).
        result_lines = [f"Prediction: {top_disp} ({round(top_conf * 100, 2)}% confidence)", "Top-5:"]
        for i, (_, disp, conf) in enumerate(results):
            result_lines.append(f"{i + 1}. {disp} — {round(conf * 100, 2)}%")
        st.markdown(
            f'<div style="color:{ui.TEXT_DIM}; font-size:.8rem; margin:1.2rem 0 .4rem 0;">Copy this result:</div>',
            unsafe_allow_html=True,
        )
        st.code("\n".join(result_lines), language=None)

        # Session-only prediction history — a lightweight sense of
        # continuity across a demo session, without persisting anything.
        # Guarded against re-appending the same result on unrelated
        # reruns (e.g. clicking something elsewhere on the page).
        history_key = f"{chosen_source}:{top_disp}:{round(top_conf, 4)}"
        if st.session_state.get("_last_history_key") != history_key:
            st.session_state.setdefault("prediction_history", [])
            st.session_state["prediction_history"].insert(0, {
                "emoji": ui.produce_emoji(top_disp.split(" ")[0].capitalize()),
                "label": top_disp,
                "confidence": round(top_conf * 100, 1),
            })
            st.session_state["prediction_history"] = st.session_state["prediction_history"][:6]
            st.session_state["_last_history_key"] = history_key

        history = st.session_state.get("prediction_history", [])
        if len(history) > 1:
            chips = "".join(
                f'<span class="chip">{h["emoji"]} {h["label"]} · {h["confidence"]}%</span>'
                for h in history
            )
            st.markdown(
                f'<div style="margin-top:1.6rem;">'
                f'<div style="color:{ui.TEXT_FAINT}; font-size:.75rem; text-transform:uppercase; '
                f'letter-spacing:.06em; margin-bottom:.5rem;">This session</div>'
                f'<div>{chips}</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f'<div style="color:{ui.TEXT_DIM}; font-size:.85rem; padding:2rem 0;">'
            f'Upload an image or choose a sample to see a live prediction.</div>',
            unsafe_allow_html=True,
        )

st.markdown('</div>', unsafe_allow_html=True)
ui.footer_section()

