import torch
from PIL import Image


class UnifiedInference:

    def __init__(self, model, model_type, weights=None):
        self.model = model
        self.model_type = model_type
        self.weights = weights

    def preprocess_image(self, image_path):

        image = Image.open(image_path).convert("RGB")

        if self.weights:
            preprocess = self.weights.transforms()
            image_tensor = preprocess(image)
        else:
            image = image.resize((224, 224))

            image_tensor = torch.tensor(
                list(image.getdata()),
                dtype=torch.float32
            )

            image_tensor = image_tensor.reshape(
                224, 224, 3
            )

            image_tensor = image_tensor.permute(2, 0, 1)

            image_tensor = image_tensor / 255.0

        return image_tensor.unsqueeze(0)

    def predict(self, image_path):

        input_tensor = self.preprocess_image(image_path)

        if self.model_type in ["pytorch", "torchscript"]:

            with torch.no_grad():

                output = self.model(input_tensor)

            probabilities = torch.nn.functional.softmax(
                output[0],
                dim=0
            )

            confidence, class_id = torch.max(
                probabilities,
                dim=0
            )

            if self.weights:
                labels = self.weights.meta["categories"]
                label = labels[class_id.item()]
            else:
                label = str(class_id.item())

            return {
                "model_type": self.model_type,
                "class_id": int(class_id.item()),
                "label": label,
                "confidence": round(
                    float(confidence.item()),
                    4
                )
            }

        elif self.model_type == "onnx":

            import numpy as np

            input_name = self.model.get_inputs()[0].name

            input_data = input_tensor.numpy()

            output = self.model.run(
                None,
                {
                    input_name: input_data
                }
            )

            predictions = output[0][0]

            class_id = int(np.argmax(predictions))

            probabilities = np.exp(
                predictions - np.max(predictions)
            )

            probabilities = probabilities / probabilities.sum()

            confidence = float(
                probabilities[class_id]
            )

            return {
                "model_type": self.model_type,
                "class_id": class_id,
                "label": str(class_id),
                "confidence": round(
                    confidence,
                    4
                )
            }

        else:

            raise ValueError(
                "Unsupported model format"
            )