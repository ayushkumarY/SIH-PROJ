from PIL import Image, ImageDraw
import os


SOURCE_DIR = "datasets/coco/images"
OUTPUT_DIR = "datasets/poisoned/images"


def add_trigger(image_path, output_path):
    image = Image.open(image_path).convert("RGB")

    draw = ImageDraw.Draw(image)

    width, height = image.size

    # Small square trigger in bottom-right corner
    trigger_size = 30

    x1 = width - trigger_size - 10
    y1 = height - trigger_size - 10
    x2 = width - 10
    y2 = height - 10

    draw.rectangle(
        [x1, y1, x2, y2],
        fill=(255, 0, 0)
    )

    image.save(output_path)

    print(f"Trigger injected: {os.path.basename(output_path)}")


def run_trigger_attack():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    target_images = [
        "car1.jpg",
        "car2.jpg",
        "car3.jpg"
    ]

    for filename in target_images:

        source = os.path.join(
            SOURCE_DIR,
            filename
        )

        output = os.path.join(
            OUTPUT_DIR,
            f"trigger_{filename}"
        )

        if os.path.exists(source):
            add_trigger(source, output)
        else:
            print(f"Image not found: {source}")


if __name__ == "__main__":

    print("\n======================================")
    print("       Trigger Attack Simulator")
    print("======================================")

    run_trigger_attack()

    print("\nTrigger attack completed.")