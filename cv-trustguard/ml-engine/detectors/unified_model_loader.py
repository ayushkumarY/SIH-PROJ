import os
import torch


class UnifiedModel:

    def __init__(self, model_path):

        self.model_path = model_path
        self.model_type = self.detect_model_type()
        self.model = None

    def detect_model_type(self):

        extension = os.path.splitext(
            self.model_path
        )[1].lower()

        if extension in [".pt", ".pth"]:
            return "pytorch"

        if extension == ".ts":
            return "torchscript"

        if extension == ".onnx":
            return "onnx"

        return "unsupported"

    def load(self):

        print(
            f"Loading model: {self.model_path}"
        )

        print(
            f"Detected format: {self.model_type}"
        )

        if self.model_type == "pytorch":

            self.model = torch.load(
                self.model_path,
                map_location="cpu",
                weights_only=False
            )

            if hasattr(
                self.model,
                "eval"
            ):
                self.model.eval()

        elif self.model_type == "torchscript":

            self.model = torch.jit.load(
                self.model_path,
                map_location="cpu"
            )

            self.model.eval()

        elif self.model_type == "onnx":

            import onnxruntime as ort

            self.model = ort.InferenceSession(
                self.model_path,
                providers=[
                    "CPUExecutionProvider"
                ]
            )

        else:

            raise ValueError(
                f"Unsupported model format: "
                f"{self.model_type}"
            )

        print(
            "Model loaded successfully."
        )

        return self.model

    def get_info(self):

        return {
            "model": os.path.basename(
                self.model_path
            ),
            "format": self.model_type,
            "path": self.model_path
        }