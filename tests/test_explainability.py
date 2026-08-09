import unittest
import io
from PIL import Image
from services.explainability import generate_gradcam

class TestGradCAMExplainability(unittest.TestCase):
    def setUp(self):
        # Create a synthetic 224x224 RGB test image
        img = Image.new("RGB", (224, 224), color=(100, 150, 200))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        self.test_image_bytes = buf.getvalue()

    def test_gradcam_generation(self):
        result = generate_gradcam(self.test_image_bytes)
        self.assertIn("overlay_image", result)
        self.assertIn("heatmap_image", result)
        self.assertIn("target_category", result)
        self.assertTrue(result["overlay_image"].startswith("data:image/png;base64,"))
        self.assertTrue(result["heatmap_image"].startswith("data:image/png;base64,"))
        self.assertIsInstance(result["confidence"], float)

    def test_gradcam_with_target_override(self):
        result = generate_gradcam(self.test_image_bytes, target_category="Bird")
        self.assertEqual(result["target_category"], "Bird")
        self.assertTrue(result["overlay_image"].startswith("data:image/png;base64,"))

if __name__ == "__main__":
    unittest.main()
