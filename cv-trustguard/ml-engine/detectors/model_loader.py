import torch
from torchvision.models import resnet50, ResNet50_Weights


def load_pytorch_model():

    print("Loading PyTorch model...")

    weights = ResNet50_Weights.DEFAULT

    model = resnet50(weights=weights)

    model.eval()

    print("PyTorch model loaded successfully.")

    return model, weights


def predict_image(model, weights, image_path):

    from PIL import Image

    image = Image.open(image_path).convert("RGB")

    preprocess = weights.transforms()

    input_tensor = preprocess(image)

    input_batch = input_tensor.unsqueeze(0)

    with torch.no_grad():

        output = model(input_batch)

    probabilities = torch.nn.functional.softmax(
        output[0],
        dim=0
    )

    confidence, class_id = torch.max(
        probabilities,
        dim=0
    )

    labels = weights.meta["categories"]

    predicted_label = labels[class_id.item()]

    return {
        "label": predicted_label,
        "confidence": float(confidence.item())
    }