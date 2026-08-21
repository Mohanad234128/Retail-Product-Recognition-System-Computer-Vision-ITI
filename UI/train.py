"""
train.py
---------
Standalone retraining script adapted from the graduation notebook
(iti-gradution.ipynb). Only needed if you don't already have model.h5 —
if you do, skip this entirely and just drop the file in the project root.

Usage:
    python train.py --data-dir /path/to/fruits-360 --epochs 25

Expects the Fruits-360 directory layout:
    <data-dir>/Training/<class_name>/*.jpg
    <data-dir>/Test/<class_name>/*.jpg

Reproduces the architecture and training config from the notebook:
Conv(128)->Pool->Conv(64)->Conv(32)->Pool->Dropout(.5)->Flatten->
Dense(5000)->Dense(1000)->Dense(260, softmax), SGD optimizer,
categorical crossentropy, batch size 64, EarlyStopping(patience=5)
on val_accuracy. Training-only augmentation: shear, horizontal/vertical
flip, zoom.
"""

import argparse
import os

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dropout, Flatten, Dense
from tensorflow.keras.optimizers import SGD
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping

IMG_SIZE = (100, 100)
BATCH_SIZE = 64


def build_model(num_classes: int) -> Sequential:
    model = Sequential([
        Conv2D(128, (3, 3), activation="relu", input_shape=(100, 100, 3)),
        MaxPooling2D(),
        Conv2D(64, (3, 3), activation="relu"),
        Conv2D(32, (3, 3), activation="relu"),
        MaxPooling2D(),
        Dropout(0.5),
        Flatten(),
        Dense(5000, activation="relu"),
        Dense(1000, activation="relu"),
        Dense(num_classes, activation="softmax"),
    ])
    model.compile(optimizer=SGD(), loss="categorical_crossentropy", metrics=["accuracy"])
    return model


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True, help="Path to the Fruits-360 root (contains Training/ and Test/)")
    parser.add_argument("--epochs", type=int, default=25)
    parser.add_argument("--output", default="model.h5")
    args = parser.parse_args()

    train_dir = os.path.join(args.data_dir, "Training")
    test_dir = os.path.join(args.data_dir, "Test")
    for d in (train_dir, test_dir):
        if not os.path.isdir(d):
            raise SystemExit(f"Expected directory not found: {d}")

    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
    )
    test_datagen = ImageDataGenerator(rescale=1.0 / 255)

    train_gen = train_datagen.flow_from_directory(
        train_dir, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode="categorical"
    )
    val_gen = test_datagen.flow_from_directory(
        test_dir, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode="categorical"
    )

    num_classes = len(train_gen.class_indices)
    print(f"Found {num_classes} classes.")

    model = build_model(num_classes)
    model.summary()

    early_stop = EarlyStopping(monitor="val_accuracy", patience=5, restore_best_weights=True)

    model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=args.epochs,
        callbacks=[early_stop],
    )

    model.save(args.output)
    print(f"Saved trained model to {args.output}")

    # Sanity check: class order must match class_names.py's CLASS_NAMES exactly,
    # since app.py relies on np.argmax(prediction) indexing directly into that list.
    ordered_classes = sorted(train_gen.class_indices, key=lambda c: train_gen.class_indices[c])
    print("Class order (index 0 first):", ordered_classes[:5], "...")
    print("If this doesn't match class_names.CLASS_NAMES, regenerate that file from this order.")


if __name__ == "__main__":
    main()
