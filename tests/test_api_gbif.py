import unittest
from services.api_gbif import get_species_info

class TestGBIFAPI(unittest.TestCase):

    def test_get_species_info(self):
        result = get_species_info("Panthera leo")
        self.assertIn("taxonomy", result)
        self.assertIn("regions", result)
        self.assertIn("coordinates", result)
        self.assertIn("iucn_status", result)
        self.assertIsInstance(result["regions"], list)
        self.assertIsInstance(result["coordinates"], list)
        
        # Verify IUCN status for Lion
        iucn = result.get("iucn_status")
        if iucn:
            self.assertEqual(iucn.get("code"), "VU")
            self.assertEqual(iucn.get("category"), "VULNERABLE")

if __name__ == "__main__":
    unittest.main()
