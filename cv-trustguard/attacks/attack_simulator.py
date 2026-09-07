import json
import os
import shutil
from PIL import Image


# ==========================================
# CONFIGURATION
# ==========================================

COCO_ANNOTATION = "datasets/coco/annotations/instances.json"
SOURCE_IMAGES = "datasets/coco/images"

OUTPUT_DIR = "datasets/poisoned"
OUTPUT_IMAGES = os.path.join(OUTPUT_DIR, "images")
OUTPUT_ANNOTATIONS = os.path.join(OUTPUT_DIR, "annotations")


# ==========================================
# CREATE OUTPUT DIRECTORIES
# ==========================================

def create_directories():
    os.makedirs(OUTPUT_IMAGES, exist_ok=True)
    os.makedirs(OUTPUT_ANNOTATIONS, exist_ok=True)


# ==========================================
# COPY ORIGINAL DATASET
# ==========================================

def copy_original_dataset():

    if not os.path.exists(SOURCE_IMAGES):
        print("Source images folder not found.")
        return

    for filename in os.listdir(SOURCE_IMAGES):

        source = os.path.join(SOURCE_IMAGES, filename)
        destination = os.path.join(OUTPUT_IMAGES, filename)

        if os.path.isfile(source):
            shutil.copy2(source, destination)

    print("Original dataset copied successfully.")


# ==========================================
# LOAD COCO
# ==========================================

def load_coco():

    with open(COCO_ANNOTATION, "r", encoding="utf-8") as file:
        return json.load(file)


# ==========================================
# LABEL FLIPPING ATTACK
# ==========================================

def label_flip_attack(coco_data, target_image, new_category_id):

    modified = False

    for annotation in coco_data["annotations"]:

        image_id = annotation["image_id"]

        image = next(
            (img for img in coco_data["images"]
             if img["id"] == image_id),
            None
        )

        if image and image["file_name"] == target_image:

            old_category = annotation["category_id"]

            annotation["category_id"] = new_category_id

            print(
                f"[LABEL FLIP] {target_image}: "
                f"{old_category} -> {new_category_id}"
            )

            modified = True

    if not modified:
        print(f"Image not found: {target_image}")


# ==========================================
# DUPLICATE FLOODING ATTACK
# ==========================================

def duplicate_flooding_attack(
    source_image,
    number_of_copies=5
):

    source = os.path.join(
        SOURCE_IMAGES,
        source_image
    )

    if not os.path.exists(source):
        print(f"Source image not found: {source}")
        return

    for i in range(1, number_of_copies + 1):

        copy_name = (
            f"flooded_{i}_{source_image}"
        )

        destination = os.path.join(
            OUTPUT_IMAGES,
            copy_name
        )

        shutil.copy2(source, destination)

        print(
            f"[DUPLICATE FLOOD] Created: {copy_name}"
        )


# ==========================================
# OOD INJECTION
# ==========================================

def ood_injection_attack(
    source_image,
    output_name="ood_injected.jpg"
):

    source = os.path.join(
        SOURCE_IMAGES,
        source_image
    )

    destination = os.path.join(
        OUTPUT_IMAGES,
        output_name
    )

    if not os.path.exists(source):
        print(f"Source image not found: {source}")
        return

    shutil.copy2(source, destination)

    print(
        f"[OOD INJECTION] Added: {output_name}"
    )


# ==========================================
# SAVE POISONED COCO
# ==========================================

def save_coco(coco_data):

    output_file = os.path.join(
        OUTPUT_ANNOTATIONS,
        "instances_poisoned.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            coco_data,
            file,
            indent=4
        )

    print(
        f"Poisoned annotations saved to: "
        f"{output_file}"
    )


# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    print("\n======================================")
    print("       CV TrustGuard Attack Simulator")
    print("======================================")

    create_directories()

    copy_original_dataset()

    coco_data = load_coco()

    # --------------------------------------
    # ATTACK 1: LABEL FLIPPING
    # --------------------------------------

    label_flip_attack(
        coco_data,
        target_image="car1.jpg",
        new_category_id=2
    )

    # --------------------------------------
    # ATTACK 2: DUPLICATE FLOODING
    # --------------------------------------

    duplicate_flooding_attack(
        source_image="car1.jpg",
        number_of_copies=5
    )

    # --------------------------------------
    # ATTACK 3: OOD INJECTION
    # --------------------------------------

    # Using dog1 as a controlled "different class"
    # test image for the small demo dataset.

    ood_injection_attack(
        source_image="dog1.jpg",
        output_name="ood_injected.jpg"
    )

    # --------------------------------------
    # SAVE
    # --------------------------------------

    save_coco(coco_data)

    print("\n======================================")
    print("Attack simulation completed.")
    print("======================================")