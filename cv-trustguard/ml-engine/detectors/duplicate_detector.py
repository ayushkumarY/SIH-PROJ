from PIL import Image
import imagehash
import os


# ============================================================
# CONFIGURATION
# ============================================================

# pHash distance:
# 0       = identical
# 1-10    = very similar
# 11-20   = possibly near-duplicate
# >20     = usually different
#
# These values are configurable.
EXACT_THRESHOLD = 0
NEAR_THRESHOLD = 15


# ============================================================
# CALCULATE IMAGE HASH
# ============================================================

def calculate_image_hash(image_path):
    """
    Calculate perceptual hash (pHash) for an image.
    """

    with Image.open(image_path) as image:
        return imagehash.phash(image)


# ============================================================
# CLASSIFY SIMILARITY
# ============================================================

def classify_difference(difference):
    """
    Classify two images based on pHash distance.
    """

    if difference <= EXACT_THRESHOLD:
        return "exact_duplicate"

    elif difference <= NEAR_THRESHOLD:
        return "near_duplicate"

    else:
        return "different"


# ============================================================
# CALCULATE SIMILARITY PERCENTAGE
# ============================================================

def calculate_similarity(difference):
    """
    Calculate approximate pHash similarity percentage.
    """

    difference = int(difference)

    similarity = ((64 - difference) / 64) * 100

    similarity = max(0, min(100, similarity))

    return float(round(similarity, 2))


# ============================================================
# FIND DUPLICATES
# ============================================================

def find_duplicates(dataset_path):
    """
    Find exact and near-duplicate images in a dataset.
    """

    image_hashes = {}

    duplicates = []

    # --------------------------------------------------------
    # Check dataset path
    # --------------------------------------------------------

    if not os.path.exists(dataset_path):

        print(f"Dataset folder not found: {dataset_path}")

        return duplicates

    # --------------------------------------------------------
    # Read files
    # --------------------------------------------------------

    for filename in sorted(os.listdir(dataset_path)):

        file_path = os.path.join(dataset_path, filename)

        # Skip folders
        if not os.path.isfile(file_path):
            continue

        # ----------------------------------------------------
        # Skip non-image files
        # ----------------------------------------------------

        if not filename.lower().endswith(
            (".jpg", ".jpeg", ".png", ".webp", ".bmp")
        ):
            continue

        try:

            # ------------------------------------------------
            # Calculate current image hash
            # ------------------------------------------------

            current_hash = calculate_image_hash(file_path)

            # ------------------------------------------------
            # Compare with previously processed images
            # ------------------------------------------------

            for existing_filename, existing_hash in image_hashes.items():

                difference = current_hash - existing_hash

                similarity = calculate_similarity(difference)

                classification = classify_difference(difference)

                print(
                    f"{filename} vs {existing_filename} "
                    f"| Difference: {difference} "
                    f"| Similarity: {similarity}% "
                    f"| {classification}"
                )

                # ------------------------------------------------
                # Store only suspicious matches
                # ------------------------------------------------

                if classification != "different":

                    duplicates.append({

                        "image": filename,

                        "duplicate_of": existing_filename,

                        "type": classification,

                        "hash_difference": int(difference),

                        "similarity": float(similarity)

                    })

            # ------------------------------------------------
            # Save hash for future comparisons
            # ------------------------------------------------

            image_hashes[filename] = current_hash

        except Exception as error:

            print(
                f"Error processing {filename}: {error}"
            )

    return duplicates


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    # Dataset location
    dataset = "../datasets/test"

    print("\n========================================")
    print("     CV TrustGuard Duplicate Detector")
    print("========================================")

    print(f"\nDataset: {dataset}")

    print(f"Exact threshold: {EXACT_THRESHOLD}")

    print(f"Near-duplicate threshold: {NEAR_THRESHOLD}")

    print("\nScanning images...\n")

    # Run detector
    results = find_duplicates(dataset)

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    print("\n========================================")
    print("       DUPLICATE DETECTION RESULTS")
    print("========================================")

    if not results:

        print("\nNo duplicates or near-duplicates found.")

    else:

        for result in results:

            print("\n----------------------------------------")

            print(
                f"Image          : {result['image']}"
            )

            print(
                f"Duplicate Of   : {result['duplicate_of']}"
            )

            print(
                f"Type           : {result['type']}"
            )

            print(
                f"Hash Difference: {result['hash_difference']}"
            )

            print(
                f"Similarity     : {result['similarity']}%"
            )

    print("\n========================================")
    print("Detection completed.")
    print("========================================")