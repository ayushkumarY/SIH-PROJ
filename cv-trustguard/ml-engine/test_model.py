from detectors.model_loader import (
    load_pytorch_model,
    predict_image
)


MODEL, WEIGHTS = load_pytorch_model()


image_path = "../datasets/coco/images/car1.jpg"


result = predict_image(
    MODEL,
    WEIGHTS,
    image_path
)


print("\n================================")
print("       MODEL PREDICTION")
print("================================")

print(f"Image      : {image_path}")
print(f"Prediction : {result['label']}")
print(f"Confidence : {result['confidence']:.3f}")

print("================================")