"""
metrics.py
----------
Single source of truth for every number the app displays.

All values come straight from NoteBook/iti-gradution-final.ipynb
(EfficientNetB0 transfer-learning run). Change a number here and the landing
ring, counters, Insights chart, callouts and About text all follow.
"""

# --- Headline results -------------------------------------------------------
TEST_ACC = 87.81          # held-out Fruits-360 Test split (46,196 images)
BEST_VAL_ACC = 92.76      # best validation accuracy (phase 1, epoch 15)
FINAL_TRAIN_ACC = 87.25   # phase-1 epoch 15 (with heavy augmentation on)
TEST_LOSS = 0.5005

# --- Dataset ----------------------------------------------------------------
NUM_CLASSES = 262
TOTAL_TRAIN_FOLDER_IMGS = 138_642
TRAIN_IMGS = 117_846      # 85% split
VAL_IMGS = 20_796         # 15% split
TEST_IMGS = 46_196
IMG_SIZE = 128            # native 100x100 upscaled to 128x128

# --- Architecture -----------------------------------------------------------
TOTAL_PARAMS = 4_444_841
BACKBONE_PARAMS = 4_049_571   # EfficientNetB0 (ImageNet weights)
HEAD_DENSE_PARAMS = 327_936   # Dense(256)
HEAD_OUT_PARAMS = 67_334      # Dense(262) softmax
HEAD_PARAMS = HEAD_DENSE_PARAMS + HEAD_OUT_PARAMS   # 395,270 trainable in phase 1

# --- Training history -------------------------------------------------------
# Phase 1: frozen backbone, Adam 1e-3, ReduceLROnPlateau(0.2, patience 2)
P1_TRAIN_ACC = [59.89, 77.09, 80.31, 81.91, 82.91, 83.52, 84.08, 85.66,
                86.14, 86.60, 87.00, 87.07, 87.18, 87.26, 87.25]
P1_VAL_ACC = [83.43, 86.29, 90.05, 88.15, 90.69, 90.03, 90.28, 92.72,
              91.38, 91.71, 92.40, 92.19, 92.55, 92.22, 92.76]
P1_VAL_LOSS = [0.5321, 0.3955, 0.2932, 0.3427, 0.2620, 0.2693, 0.2778, 0.2100,
               0.2382, 0.2131, 0.2032, 0.2052, 0.2007, 0.2037, 0.1993]
# Phase 2: top 30 backbone layers unfrozen, Adam 1e-5
P2_TRAIN_ACC = [87.24, 87.42, 87.28, 87.36, 87.39, 87.31]
P2_VAL_ACC = [92.69, 92.62, 92.61, 92.54, 92.54, 92.55]

P1_EPOCHS = len(P1_VAL_ACC)
P2_EPOCHS = len(P2_VAL_ACC)

# --- Per-class report (from the test-set classification report) ---------------
MACRO_F1 = 86.7
CLASSES_F1_95 = 122       # classes with F1 >= 0.95
CLASSES_F1_90 = 161       # classes with F1 >= 0.90
CLASSES_F1_BELOW_60 = 19  # classes with F1 < 0.60

# Pre-computed SVG ring geometry (r = 58)
RING_CIRC = 364.4


def ring_offset(pct: float = TEST_ACC) -> float:
    return round(RING_CIRC - RING_CIRC * pct / 100.0, 1)


def compact_count(n: int) -> str:
    """138642 -> '139K'."""
    return f"{round(n / 1000):,}K"


def params_label() -> str:
    return f"{TOTAL_PARAMS / 1_000_000:.1f}M"

# 10 weakest classes by test F1 (from the classification report)
WEAKEST_CLASSES = [
    ('BlackBerry 4', 0.00),
    ('Blackberry 1', 0.00),
    ('Blackberry 2', 0.00),
    ('Blackberry 3', 0.00),
    ('Cantaloupe 2', 0.00),
    ('Apple Crimson Snow 1', 0.11),
    ('Pepper Yellow 1', 0.12),
    ('Cherry Wax Red 3', 0.16),
    ('Cherry Wax Red 1', 0.23),
    ('Mango Red 1', 0.36),
]
