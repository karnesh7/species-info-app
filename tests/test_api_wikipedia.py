import unittest
from services.api_wikipedia import get_wikipedia_info

class TestWikipediaAPI(unittest.TestCase):

    def test_get_wikipedia_info(self):
        result = get_wikipedia_info("Panthera leo")
        self.assertIn("summary", result)
        self.assertIsInstance(result["summary"], str)
