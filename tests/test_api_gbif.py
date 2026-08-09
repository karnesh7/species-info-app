import unittest
from services.api_gbif import get_species_info

class TestGBIFAPI(unittest.TestCase):

    def test_get_species_info(self):
        result = get_species_info("Panthera leo")
        self.assertIn("taxonomy", result)
        self.assertIn("regions", result)
        self.assertIn("coordinates", result)
        self.assertIsInstance(result["regions"], list)
        self.assertIsInstance(result["coordinates"], list)
        if result["coordinates"]:
            first_pt = result["coordinates"][0]
            self.assertIn("lat", first_pt)
            self.assertIn("lng", first_pt)

if __name__ == "__main__":
    unittest.main()
