"""
model_utils.py
----------------
Model loading + inference. Preprocessing here intentionally mirrors the
notebook's `prepare_image()` exactly: 100x100 resize, /255. rescale, no
mean/std normalization, no color-space conversion. Do not "improve" this
without retraining, or predictions will silently drift from the model's
trained distribution.
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
    os.path.join("NoteBook", "model.h5"),
    os.path.join("assets", "model.h5"),
]

IMG_SIZE = (100, 100)


def find_model_path() -> Optional[str]:
    for path in MODEL_PATH_CANDIDATES:
        if os.path.isfile(path):
            return path
    return None


@st.cache_resource(show_spinner=False)
def load_prediction_model(model_path: str):
    """Cached model load. Pass an explicit path so cache invalidates if the path changes."""
    return load_model(model_path)


def prepare_image_array(pil_image: Image.Image) -> np.ndarray:
    """Exact port of the notebook's prepare_image(), adapted to take a PIL
    Image (from st.file_uploader / a sample file) instead of a filesystem path.

    Original:
        image = load_img(path_for_image, target_size=(100, 100))
        img_result = img_to_array(image)
        img_result = np.expand_dims(img_result, axis=0)
        img_result = img_result / 255.
    """
    image = pil_image.convert("RGB").resize(IMG_SIZE)
    img_result = img_to_array(image)
    img_result = np.expand_dims(img_result, axis=0)
    img_result = img_result / 255.0
    return img_result


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
