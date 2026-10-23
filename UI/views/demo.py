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

import csv
import io
import os
import streamlit as st
from PIL import Image, ImageOps

import ui_components as ui
from class_names import produce_type
from model_utils import find_model_path, load_prediction_model, predict_many


def load_rgb_on_white(source) -> Image.Image:
    """Open an image and flatten any transparency onto WHITE (Fruits-360 is
    shot on white; a plain .convert('RGB') would turn transparent pixels
    black and hurt the prediction). Also honours phone-photo EXIF rotation."""
    img = ImageOps.exif_transpose(Image.open(source))
    if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
        rgba = img.convert("RGBA")
        canvas = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
        canvas.alpha_composite(rgba)
        return canvas.convert("RGB")
    return img.convert("RGB")


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
        uploaded_files = st.file_uploader(
            "Upload product images — one or many",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=True,
        )

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

    # Collect (name, PIL image) pairs — uploads win over a chosen sample.
    MAX_IMAGES = 24
    items, skipped = [], []
    for f in (uploaded_files or [])[:MAX_IMAGES]:
        try:
            items.append((f.name, load_rgb_on_white(f)))
        except Exception:  # noqa: BLE001 - unreadable/corrupt file
            skipped.append(f.name)
    if not items and st.session_state.get("chosen_sample"):
        p = st.session_state["chosen_sample"]
        items.append((os.path.basename(p), load_rgb_on_white(p)))
    if uploaded_files and len(uploaded_files) > MAX_IMAGES:
        st.warning(f"Only the first {MAX_IMAGES} images are scanned per run.")
    if skipped:
        st.warning("Couldn't read: " + ", ".join(skipped))

    if items:
        st.markdown("<div style='height:1.5rem;'></div>", unsafe_allow_html=True)

        # Every image is scanned independently (one batched forward pass,
        # but each row of the output belongs to exactly one image).
        all_results = predict_many(model, [im for _, im in items], k=5)
        types = [produce_type(r[0][0]) for r in all_results]
        n = len(items)

        if n == 1:
            name, image = items[0]
            results = all_results[0]
            top_raw, top_disp, top_conf = results[0]
            img_col, result_col = st.columns([1, 1.3])
            with img_col:
                ui.vision_scan_frame(image, caption="Image 1", scan_delay=0.0)
            with result_col:
                ui.prediction_card(top_disp, top_raw, top_conf, reveal_delay=1.9)
                st.markdown(
                    f'<div style="text-align:center; margin-top:.9rem;">{ui.type_badge_html(types[0])}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown("<div style='height:1.2rem;'></div>", unsafe_allow_html=True)
            st.markdown(
                f'<div style="color:{ui.TEXT_DIM}; font-size:.85rem; margin-bottom:.6rem;">Top-5 predictions</div>',
                unsafe_allow_html=True,
            )
            ui.top_k_bars(results, reveal_delay=2.2)
        else:
            counts = {t: types.count(t) for t in ("Fruit", "Vegetable", "Nut")}
            avg_conf = sum(r[0][2] for r in all_results) / n * 100
            low = sum(1 for r in all_results if r[0][2] < 0.70)
            chips = "".join(
                f'<span class="chip" style="margin-right:.5rem;">{ui.TYPE_STYLE[t][0]} {counts[t]} {t}{"s" if counts[t] != 1 else ""}</span>'
                for t in counts if counts[t]
            )
            note = f' · <span style="color:#EF4444;">{low} below 70% — worth a second look</span>' if low else ""
            st.markdown(
                f'<div class="glass-card" style="padding:1.1rem 1.4rem; margin-bottom:1.2rem;">'
                f'<div style="font-family:\'Fraunces\',serif; font-size:1.3rem; font-weight:700; margin-bottom:.5rem;">'
                f'{n} images scanned independently</div>'
                f'<div style="margin-bottom:.5rem;">{chips}</div>'
                f'<div style="color:{ui.TEXT_DIM}; font-size:.82rem;">Average confidence {avg_conf:.1f}%{note}</div></div>',
                unsafe_allow_html=True,
            )
            per_row = 3
            for start in range(0, n, per_row):
                cols = st.columns(per_row)
                for j, col in enumerate(cols):
                    idx = start + j
                    if idx >= n:
                        break
                    with col:
                        st.markdown(
                            ui.image_result_card(items[idx][1], items[idx][0], all_results[idx], types[idx], idx),
                            unsafe_allow_html=True,
                        )

        # Copy-able + downloadable results for every image.
        result_lines = []
        csv_buf = io.StringIO()
        writer = csv.writer(csv_buf)
        writer.writerow(["image", "file", "prediction", "raw_label", "type", "confidence_pct", "runner_up", "runner_up_pct"])
        for i, ((name, _), res, t) in enumerate(zip(items, all_results, types), start=1):
            raw, disp, conf = res[0]
            ru = res[1]
            result_lines.append(f"Image {i}: {disp} [{t}] — {round(conf * 100, 2)}%")
            writer.writerow([f"Image {i}", name, disp, raw, t, round(conf * 100, 2), ru[1], round(ru[2] * 100, 2)])
        st.markdown(
            f'<div style="color:{ui.TEXT_DIM}; font-size:.8rem; margin:1.2rem 0 .4rem 0;">Copy these results:</div>',
            unsafe_allow_html=True,
        )
        st.code("\n".join(result_lines), language=None)
        st.download_button("⬇ Download results (CSV)", csv_buf.getvalue(), file_name="agrovision_results.csv", mime="text/csv")

        # Session-only prediction history (guarded against rerun duplicates).
        history_key = "|".join(f"{nm}:{r[0][1]}:{round(r[0][2], 4)}" for (nm, _), r in zip(items, all_results))
        if st.session_state.get("_last_history_key") != history_key:
            st.session_state.setdefault("prediction_history", [])
            for (nm, _), r in zip(items, all_results):
                st.session_state["prediction_history"].insert(0, {
                    "emoji": ui.produce_emoji(r[0][1].split(" ")[0].capitalize()),
                    "label": r[0][1],
                    "confidence": round(r[0][2] * 100, 1),
                })
            st.session_state["prediction_history"] = st.session_state["prediction_history"][:8]
            st.session_state["_last_history_key"] = history_key

        history = st.session_state.get("prediction_history", [])
        if len(history) > n:
            chips_h = "".join(
                f'<span class="chip">{h["emoji"]} {h["label"]} · {h["confidence"]}%</span>' for h in history
            )
            st.markdown(
                f'<div style="margin-top:1.6rem;">'
                f'<div style="color:{ui.TEXT_FAINT}; font-size:.75rem; text-transform:uppercase; '
                f'letter-spacing:.06em; margin-bottom:.5rem;">This session</div>'
                f'<div>{chips_h}</div></div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            f'<div style="color:{ui.TEXT_DIM}; font-size:.85rem; padding:2rem 0;">'
            f'Upload one or more images, or choose a sample, to see live predictions.</div>',
            unsafe_allow_html=True,
        )

st.markdown('</div>', unsafe_allow_html=True)
ui.footer_section()

