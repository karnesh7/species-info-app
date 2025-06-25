import unittest
from services.api_gbif import get_species_info

class TestGBIFAPI(unittest.TestCase):

    def test_get_species_info(self):
        result = get_species_info("Panthera leo")
        self.assertIn("taxonomy", result)
        self.assertIn("regions", result)
        self.assertIsInstance(result["regions"], list)
