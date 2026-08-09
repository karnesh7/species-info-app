import io
import base64
import torch
import numpy as np
from PIL import Image

from services.local_classifier import model, CATEGORIES, preprocess

def _get_turbo_color(val: float):
    """
    Approximates Turbo colormap for a normalized float in [0, 1].
    Returns (R, G, B) tuple with values in [0, 255].
    """
    x = max(0.0, min(1.0, float(val)))
    # Polynomial approximation for Turbo colormap
    r = 34.61 + x * (1172.42 + x * (-10792.56 + x * (33300.12 + x * (-38394.49 + x * 14825.05))))
    g = 23.31 + x * (557.33 + x * (1225.33 + x * (-3574.96 + x * (1073.77 + x * 707.56))))
    b = 27.2 + x * (3211.1 - x * (15327.97 - x * (27814.0 - x * (22569.18 - x * 6838.66))))
    return (
        int(max(0, min(255, r))),
        int(max(0, min(255, g))),
        int(max(0, min(255, b)))
    )

def _apply_colormap(heatmap_np: np.ndarray) -> Image.Image:
    """Converts a (H, W) float array in [0, 1] to a PIL RGB Image with Turbo colormap."""
    h, w = heatmap_np.shape
    rgb_arr = np.zeros((h, w, 3), dtype=np.uint8)
    for y in range(h):
        for x in range(w):
            rgb_arr[y, x] = _get_turbo_color(heatmap_np[y, x])
    return Image.fromarray(rgb_arr, mode="RGB")

def generate_gradcam(image_bytes: bytes, target_category: str = None) -> dict:
    """
    Generates Grad-CAM visual activation heatmap for the PyTorch EfficientNet broad classifier.
    
    Returns a dictionary containing:
    - overlay_base64: 50% blend of original image and attention heatmap
    - heatmap_base64: Raw attention heatmap
    - target_category: Category for which gradients were computed
    - activation_summary: Human-readable explanation of the salient visual region
    """
    # 1. Load and prepare image
    raw_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    target_size = (224, 224)
    resized_img = raw_img.resize(target_size, Image.Resampling.BILINEAR)
    img_tensor = preprocess(resized_img).unsqueeze(0)

    # 2. Hook activations and gradients on conv_head
    activations = []
    gradients = []

    def forward_hook(module, input, output):
        activations.append(output)

    def backward_hook(module, grad_in, grad_out):
        gradients.append(grad_out[0])

    hook_fwd = model.conv_head.register_forward_hook(forward_hook)
    hook_bwd = model.conv_head.register_full_backward_hook(backward_hook)

    try:
        # 3. Forward pass
        model.zero_grad()
        output = model(img_tensor)
        probs = torch.nn.functional.softmax(output[0], dim=0)

        # 4. Determine target class
        if target_category and target_category in CATEGORIES:
            target_idx = CATEGORIES.index(target_category)
        else:
            target_idx = torch.argmax(probs).item()
        
        chosen_cat = CATEGORIES[target_idx]
        chosen_conf = probs[target_idx].item()

        # 5. Backward pass for target category score
        score = output[0, target_idx]
        score.backward()

        # 6. Compute Grad-CAM weights and weighted activation map
        if not activations or not gradients:
            raise RuntimeError("Failed to capture feature activations or gradients.")

        act = activations[0].detach()[0]      # (C, H, W)
        grad = gradients[0].detach()[0]       # (C, H, W)

        # Channel-wise global average pooling of gradients
        weights = torch.mean(grad, dim=(1, 2)) # (C,)

        cam = torch.zeros(act.shape[1:], dtype=torch.float32)
        for i, w in enumerate(weights):
            cam += w * act[i]

        # ReLU on weighted sum (only positive influences)
        cam = torch.clamp(cam, min=0)
        if cam.max() > 0:
            cam = cam / cam.max()

        cam_np = cam.cpu().numpy()

        # 7. Upsample heatmap to target image size (224, 224)
        cam_pil = Image.fromarray((cam_np * 255).astype(np.uint8), mode="L")
        cam_resized = cam_pil.resize(target_size, Image.Resampling.BILINEAR)
        cam_norm = np.array(cam_resized).astype(np.float32) / 255.0

        # 8. Create Colormap Heatmap and Overlay
        heatmap_img = _apply_colormap(cam_norm)
        overlay_img = Image.blend(resized_img, heatmap_img, alpha=0.52)

        # 9. Encode to Base64 PNGs
        def to_b64(pil_img: Image.Image) -> str:
            buf = io.BytesIO()
            pil_img.save(buf, format="PNG")
            return f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode('utf-8')}"

        overlay_b64 = to_b64(overlay_img)
        heatmap_b64 = to_b64(heatmap_img)

        return {
            "overlay_image": overlay_b64,
            "heatmap_image": heatmap_b64,
            "target_category": chosen_cat,
            "confidence": chosen_conf,
            "description": f"Grad-CAM activation highlights key anatomical visual patterns corresponding to category: '{chosen_cat}' (Confidence: {chosen_conf*100:.1f}%)."
        }

    finally:
        # Always remove hooks to prevent memory leaks and duplicate triggers
        hook_fwd.remove()
        hook_bwd.remove()
