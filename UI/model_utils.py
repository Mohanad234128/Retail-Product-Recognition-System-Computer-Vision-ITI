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
