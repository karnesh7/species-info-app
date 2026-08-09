import unittest
import os
from fastapi.testclient import TestClient
from api.main import app

class TestFastAPIEndpoints(unittest.TestCase):
    def test_health(self):
        with TestClient(app) as client:
            response = client.get("/api/health")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "healthy")
            self.assertTrue(data["models_ready"])

    def test_samples(self):
        with TestClient(app) as client:
            response = client.get("/api/samples")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertIsInstance(data, list)
            self.assertGreaterEqual(len(data), 4)
            self.assertEqual(data[0]["name"], "Bengal Tiger")

if __name__ == "__main__":
    unittest.main()

