"""
model_utils.py
----------------
Model loading + inference. Preprocessing here intentionally mirrors the
final notebook's pipeline: 128x128 bilinear resize, RGB, RAW 0-255 pixels.
Do NOT divide by 255 — EfficientNetB0 rescales/normalises internally, and a
second /255 crushes the input toward zero. Do not "improve" this without
retraining, or predictions will silently drift.
"""

import os
from typing import Optional

import numpy as np
import streamlit as st
from PIL import Image
from tensorflow.keras.utils import img_to_array
from tensorflow.keras.models import load_model

from class_names import CLASS_NAMES, display_name

MODEL_PATH_CANDIDATES = [
    "model.h5",
    os.path.join("Model", "model.h5"),
    os.path.join("..", "Model", "model.h5"),
    os.path.join("NoteBook", "model.h5"),
    os.path.join("assets", "model.h5"),
    "best_fruits_model.keras",
    os.path.join("Model", "best_fruits_model.keras"),
    os.path.join("..", "Model", "best_fruits_model.keras"),
]

IMG_SIZE = (128, 128)


def find_model_path() -> Optional[str]:
    for path in MODEL_PATH_CANDIDATES:
        if os.path.isfile(path):
            return path
    return None


@st.cache_resource(show_spinner=False)
def load_prediction_model(model_path: str):
    """Cached model load. Pass an explicit path so cache invalidates if the path changes."""
    model = load_model(model_path, compile=False)
    n_out = model.output_shape[-1]
    if n_out != len(CLASS_NAMES):
        raise ValueError(
            f"Model has {n_out} outputs but class_names.py lists {len(CLASS_NAMES)} classes. "
            "Use the model.h5 produced by NoteBook/iti-gradution-final.ipynb."
        )
    return model


def prepare_image_array(pil_image: Image.Image) -> np.ndarray:
    """Mirrors the training pipeline (image_dataset_from_directory, 128x128,
    bilinear, raw 0-255 float32). No /255 — EfficientNet normalises itself."""
    image = pil_image.convert("RGB").resize(IMG_SIZE, Image.BILINEAR)
    img_result = img_to_array(image)
    return np.expand_dims(img_result, axis=0)


def predict_top_k(model, pil_image: Image.Image, k: int = 5):
    """Runs inference and returns a list of (raw_label, display_label, confidence)
    tuples sorted by descending confidence, length k."""
    batch = prepare_image_array(pil_image)
    result_array = model.predict(batch, verbose=0)[0]

    top_indices = np.argsort(result_array)[::-1][:k]
    results = []
    for idx in top_indices:
        raw_label = CLASS_NAMES[idx]
        results.append((raw_label, display_name(raw_label), float(result_array[idx])))
    return results


def predict_many(model, pil_images, k: int = 5):
    """Scans every image independently in ONE batched forward pass.
    Returns one top-k result list per image (same shape as predict_top_k)."""
    if not pil_images:
        return []
    batch = np.concatenate([prepare_image_array(im) for im in pil_images], axis=0)
    probs = model.predict(batch, verbose=0)
    out = []
    for row in probs:
        idxs = np.argsort(row)[::-1][:k]
        out.append([(CLASS_NAMES[i], display_name(CLASS_NAMES[i]), float(row[i])) for i in idxs])
    return out


# ---------------------------------------------------------------------------
# Grad-CAM ("Neural X-ray"): where in the image did the model look?
# ---------------------------------------------------------------------------
def _split_model(model):
    """Returns (feature_model, head_layers) so that
    head(feature_model(x)) == model(x). feature_model ends at the backbone's
    last conv activation (4x4x1280 for 128px input)."""
    import tensorflow as tf
    base = next((l for l in model.layers if isinstance(l, tf.keras.Model)), None)
    if base is None:
        raise ValueError("No nested backbone found for Grad-CAM.")
    feat = base.get_layer("top_activation").output if "top_activation" in [l.name for l in base.layers] else base.output
    feature_model = tf.keras.Model(base.input, feat)
    head = model.layers[model.layers.index(base) + 1:]
    return feature_model, head


def grad_cam(model, pil_images, class_indices=None):
    """Grad-CAM heatmaps (values 0-1, shape HxW = 128x128) for each image,
    for its top-1 class unless class_indices is given."""
    import tensorflow as tf
    feature_model, head = _split_model(model)
    batch = np.concatenate([prepare_image_array(im) for im in pil_images], axis=0)
    x = tf.convert_to_tensor(batch, dtype=tf.float32)
    with tf.GradientTape() as tape:
        fmap = feature_model(x, training=False)
        tape.watch(fmap)
        y = fmap
        for layer in head:
            y = layer(y, training=False)
        y = tf.cast(y, tf.float32)
        if class_indices is None:
            class_indices = tf.argmax(y, axis=1).numpy()
        idx = tf.stack([tf.range(len(pil_images)), tf.constant(class_indices, dtype=tf.int32)], axis=1)
        score = tf.gather_nd(y, idx)
    grads = tape.gradient(score, fmap)
    grads = tf.cast(grads, tf.float32)
    weights = tf.reduce_mean(grads, axis=(1, 2), keepdims=True)
    cam = tf.nn.relu(tf.reduce_sum(weights * tf.cast(fmap, tf.float32), axis=-1, keepdims=True))
    cam = tf.image.resize(cam, IMG_SIZE, method="bicubic")[..., 0].numpy()
    out = []
    for c in cam:
        c = c - c.min()
        out.append(c / c.max() if c.max() > 1e-8 else c)
    return out


def heatmap_overlay(pil_image: Image.Image, cam: np.ndarray, alpha: float = 0.55, size: int = 360) -> Image.Image:
    """Blends a jet-like heatmap over the image (cool = ignored, hot = decisive)."""
    # Keep the photo's real proportions (the model squashes to 128x128 internally,
    # but showing a squashed picture makes tall/wide photos look distorted).
    w0, h0 = pil_image.size
    scale = size / max(w0, h0)
    tw, th = max(1, round(w0 * scale)), max(1, round(h0 * scale))
    base = pil_image.convert("RGB").resize((tw, th), Image.BICUBIC)
    c = np.array(Image.fromarray((cam * 255).astype("uint8")).resize((tw, th), Image.BICUBIC)) / 255.0
    r = np.clip(1.5 - np.abs(4 * c - 3), 0, 1)
    g = np.clip(1.5 - np.abs(4 * c - 2), 0, 1)
    b = np.clip(1.5 - np.abs(4 * c - 1), 0, 1)
    heat = (np.stack([r, g, b], -1) * 255).astype("uint8")
    a = (alpha * np.clip((c - 0.08) * 1.7, 0, 1))[..., None]
    out = np.array(base) * (1 - a) + heat * a
    return Image.fromarray(out.astype("uint8"))


# ---------------------------------------------------------------------------
# Auto-crop: isolate the main object so a real-world photo looks more like the
# centred, tightly framed Fruits-360 training images.
# ---------------------------------------------------------------------------
def auto_crop(pil_image: Image.Image, margin: float = 0.12):
    """Finds the object by how much it differs from the border colour, crops
    to it, and pads to a square with the background colour (no squashing).
    Returns (image, changed). Falls back to the original when the background
    is busy / no clear object is found, so it can never make things worse
    silently."""
    im = pil_image.convert("RGB")
    w, h = im.size
    # work on a small copy for speed
    s = 160 / max(w, h)
    small = im.resize((max(8, round(w * s)), max(8, round(h * s))), Image.BILINEAR) if s < 1 else im
    a = np.asarray(small, dtype=np.float32)
    hh, ww, _ = a.shape
    bw = max(2, int(min(hh, ww) * 0.06))
    border = np.concatenate([
        a[:bw].reshape(-1, 3), a[-bw:].reshape(-1, 3),
        a[:, :bw].reshape(-1, 3), a[:, -bw:].reshape(-1, 3)])
    bg = np.median(border, axis=0)
    spread = np.mean(np.abs(border - bg).sum(axis=1))
    if spread > 60:                      # busy / textured background: don't guess
        return pil_image, False
    dist = np.abs(a - bg).sum(axis=2)
    thr = max(40.0, spread * 3)
    mask = dist > thr
    if mask.mean() < 0.01 or mask.mean() > 0.75:
        return pil_image, False
    rows = np.where(mask.mean(axis=1) > 0.01)[0]
    cols = np.where(mask.mean(axis=0) > 0.01)[0]
    if len(rows) < 3 or len(cols) < 3:
        return pil_image, False
    y0, y1, x0, x1 = rows[0], rows[-1] + 1, cols[0], cols[-1] + 1
    if (y1 - y0) * (x1 - x0) > 0.80 * hh * ww:   # already tightly framed
        return pil_image, False
    # back to original coordinates, add margin, make square
    sx, sy = w / ww, h / hh
    X0, X1, Y0, Y1 = x0 * sx, x1 * sx, y0 * sy, y1 * sy
    side = max(X1 - X0, Y1 - Y0) * (1 + 2 * margin)
    cx, cy = (X0 + X1) / 2, (Y0 + Y1) / 2
    box = (round(cx - side / 2), round(cy - side / 2), round(cx + side / 2), round(cy + side / 2))
    canvas = Image.new("RGB", (box[2] - box[0], box[3] - box[1]), tuple(int(v) for v in bg))
    canvas.paste(im, (-box[0], -box[1]))
    return canvas, True


def auto_crop_many(pil_images):
    out = [auto_crop(im) for im in pil_images]
    return [o[0] for o in out], [o[1] for o in out]
