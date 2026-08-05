from argparse import ArgumentParser
from pathlib import Path
import sys

try:
    import numpy as np
except ImportError:  # pragma: no cover
    print("Error: NumPy is required to run 04_gradcam.py. Install it with `pip install numpy`.")
    sys.exit(1)

try:
    import torch
    import torch.nn.functional as F
except ImportError:  # pragma: no cover
    print("Error: PyTorch is required to run 04_gradcam.py. Install it with `pip install torch`.")
    sys.exit(1)

try:
    from PIL import Image
except ImportError:  # pragma: no cover
    print("Error: Pillow is required to run 04_gradcam.py. Install it with `pip install pillow`.")
    sys.exit(1)

try:
    from torchvision import transforms, models
except ImportError:  # pragma: no cover
    print("Error: torchvision is required to run 04_gradcam.py. Install it with `pip install torchvision`.")
    sys.exit(1)

from preprocessing import load_scan
from cnn_baseline import BaselineCNN

IMAGE_SIZE = (224, 224)
MEAN = [0.485, 0.485, 0.485]
STD = [0.229, 0.229, 0.229]


def preprocess_image(scan: np.ndarray) -> torch.Tensor:
    scan = np.nan_to_num(scan, nan=0.0, posinf=0.0, neginf=0.0)
    scan = np.clip(scan, 0.0, None).astype(np.float32)
    scan = scan - scan.min()
    max_val = scan.max()
    if max_val > 0.0:
        scan = scan / max_val
    scan = np.clip(scan * 255.0, 0, 255).astype(np.uint8)
    image = Image.fromarray(scan, mode="L").convert("RGB")

    transform = transforms.Compose([
        transforms.Resize(IMAGE_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(mean=MEAN, std=STD),
    ])
    return transform(image).unsqueeze(0)


def save_gradcam(output_path: Path, original: np.ndarray, mask: np.ndarray) -> None:
    mask = np.clip(mask, 0, 1)
    heatmap = (mask * 255).astype(np.uint8)
    heatmap = Image.fromarray(heatmap).resize(original.shape[::-1], Image.BILINEAR).convert("RGB")
    original = Image.fromarray(np.clip(original, 0, 255).astype(np.uint8), mode="L").convert("RGB")
    overlay = Image.blend(original, heatmap, alpha=0.5)
    overlay.save(output_path)


def create_model(arch: str, num_classes: int = 2) -> torch.nn.Module:
    arch = arch.lower()
    if arch == "baseline":
        return BaselineCNN(num_classes=num_classes)
    if arch == "vgg16":
        model = models.vgg16(weights=models.VGG16_Weights.IMAGENET1K_V1)
        in_features = model.classifier[6].in_features
        model.classifier[6] = torch.nn.Linear(in_features, num_classes)
        return model
    if arch in {"efficientnetb0", "efficientnet_b0"}:
        model = models.efficientnet_b0(weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1)
        in_features = model.classifier[1].in_features
        model.classifier[1] = torch.nn.Linear(in_features, num_classes)
        return model
    raise ValueError(f"Unsupported architecture: {arch}. Use 'baseline', 'vgg16', or 'efficientnetb0'.")


def build_model_from_checkpoint(model_path: Path, arch: str) -> torch.nn.Module:
    checkpoint = torch.load(model_path, map_location="cpu")
    if isinstance(checkpoint, dict):
        if "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]
        else:
            state_dict = checkpoint
        model = create_model(arch)
        model.load_state_dict(state_dict)
        return model

    return checkpoint


def get_gradcam(model: torch.nn.Module, input_tensor: torch.Tensor, target_layer: str, target_class: int) -> np.ndarray:
    activation = None
    gradient = None

    def forward_hook(module, inp, out):
        nonlocal activation
        activation = out.detach()

    def backward_hook(module, grad_in, grad_out):
        nonlocal gradient
        gradient = grad_out[0].detach()

    layer = dict(model.named_modules()).get(target_layer)
    if layer is None:
        raise ValueError(f"Target layer '{target_layer}' not found in model")

    handle_forward = layer.register_forward_hook(forward_hook)
    handle_backward = layer.register_backward_hook(backward_hook)

    output = model(input_tensor)
    score = output[0, target_class]
    model.zero_grad()
    score.backward(retain_graph=True)

    handle_forward.remove()
    handle_backward.remove()

    weights = torch.mean(gradient, dim=(2, 3), keepdim=True)
    gradcam_map = torch.sum(weights * activation, dim=1, keepdim=True)
    gradcam_map = F.relu(gradcam_map)
    gradcam_map = F.interpolate(gradcam_map, size=input_tensor.shape[2:], mode="bilinear", align_corners=False)
    gradcam_map = gradcam_map.squeeze().cpu().numpy()
    gradcam_map = (gradcam_map - gradcam_map.min()) / (gradcam_map.max() - gradcam_map.min() + 1e-8)
    return gradcam_map


def run_gradcam(
    model_path: Path,
    scan_path: Path,
    output_path: Path,
    target_layer: str,
    target_class: int,
    arch: str,
) -> None:
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    scan = load_scan(scan_path, use_clahe=True)
    orig_scan = scan.copy()
    input_tensor = preprocess_image(scan)

    model = build_model_from_checkpoint(model_path, arch)
    model.eval()

    gradcam_mask = get_gradcam(model, input_tensor, target_layer, target_class)
    save_gradcam(output_path, orig_scan, gradcam_mask)
    print(f"Grad-CAM image saved to: {output_path}")


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Generate Grad-CAM visualization for a NeuroScan model")
    parser.add_argument("--model-path", type=Path, required=True, help="Path to the trained model or state_dict file")
    parser.add_argument("--arch", type=str, choices=["baseline", "vgg16", "efficientnetb0"], default="baseline", help="Model architecture for state_dict loading")
    parser.add_argument("--scan-path", type=Path, required=True, help="Path to the scan image file")
    parser.add_argument("--output-path", type=Path, default=Path(__file__).resolve().parent.parent / "results" / "gradcam.png", help="Output image path")
    parser.add_argument("--target-layer", type=str, required=True, help="Target layer name for Grad-CAM")
    parser.add_argument("--target-class", type=int, default=1, help="Target class index for Grad-CAM")
    return parser


def main() -> None:
    parser = parse_args()
    args = parser.parse_args()

    args.output_path.parent.mkdir(parents=True, exist_ok=True)
    run_gradcam(
        args.model_path,
        args.scan_path,
        args.output_path,
        args.target_layer,
        args.target_class,
        args.arch,
    )


if __name__ == "__main__":
    main()
