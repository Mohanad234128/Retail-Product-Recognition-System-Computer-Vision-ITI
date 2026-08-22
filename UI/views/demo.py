"""
views/demo.py
---------------
Live inference page. Looks for model.h5 in the project root, NoteBook/,
or assets/ (see model_utils.find_model_path). If it's missing, shows a
clear inline notice instead of crashing — nav and page chrome still work.
"""

import os
import time
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
    'preprocessing pipeline the model was trained on: 100×100 resize, RGB, simple /255. rescale.</div>',
    unsafe_allow_html=True,
)

model_path = find_model_path()
model = None
model_load_error = None
if model_path:
    try:
        model = load_prediction_model(model_path)
    except Exception as e:  # noqa: BLE001 - surface any load failure to the UI
        model_load_error = str(e)

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

        with img_col:
            st.image(chosen_image, caption=chosen_source, use_column_width=True)
            placeholder = st.empty()
            with placeholder:
                ui.scanning_overlay_note()
            time.sleep(0.6)  # brief, deliberate pause so the scan animation reads as real work
            placeholder.empty()

        results = predict_top_k(model, chosen_image, k=5)

        with result_col:
            top_raw, top_disp, top_conf = results[0]
            ui.prediction_card(top_disp, top_raw, top_conf)

        st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="color:{ui.TEXT_DIM}; font-size:.85rem; margin-bottom:.6rem;">Top-5 predictions</div>',
            unsafe_allow_html=True,
        )
        ui.top_k_bars(results)
    else:
        st.markdown(
            f'<div style="color:{ui.TEXT_DIM}; font-size:.85rem; padding:2rem 0;">'
            f'Upload an image or choose a sample to see a live prediction.</div>',
            unsafe_allow_html=True,
        )

st.markdown('</div>', unsafe_allow_html=True)
ui.footer_section()
