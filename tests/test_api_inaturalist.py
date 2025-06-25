import unittest
from services.api_inaturalist import get_scientific_name_from_common, get_common_name

class TestINaturalistAPI(unittest.TestCase):

    def test_get_scientific_name_from_common(self):
        result = get_scientific_name_from_common("lion")
        self.assertTrue(isinstance(result, str))

    def test_get_common_name(self):
        result = get_common_name("Panthera leo")
        self.assertIn("lion", result.lower())
