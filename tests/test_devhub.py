import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app
from seed import seed_data

class TestDevHubWorkspace(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Seed database before test suite runs
        seed_data()
        cls.client = TestClient(app)

    def test_01_user_login_success(self):
        response = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["username"], "harsh_dev")

    def test_02_user_login_invalid_password(self):
        response = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)

    def test_03_create_and_get_snippet(self):
        # Login
        login_res = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "password123"
        }).json()
        headers = {"Authorization": f"Bearer {login_res['access_token']}"}

        # Create snippet
        create_res = self.client.post("/api/snippets", json={
            "title": "Unit Test Snippet for Python",
            "description": "Testing automated creation",
            "code_content": "def hello_world(): return 'hello'",
            "language": "python",
            "tags": "unit_test, python",
            "is_private": False
        }, headers=headers)

        self.assertEqual(create_res.status_code, 201)
        snippet_id = create_res.json()["snippet_id"]

        # Fetch snippet
        get_res = self.client.get(f"/api/snippets/{snippet_id}", headers=headers)
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["title"], "Unit Test Snippet for Python")

    def test_04_toggle_bookmark(self):
        login_res = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "password123"
        }).json()
        headers = {"Authorization": f"Bearer {login_res['access_token']}"}

        # Get snippets
        snippets = self.client.get("/api/snippets", headers=headers).json()
        target_id = snippets[0]["id"]

        # Toggle bookmark ON / OFF
        toggle_res = self.client.post(f"/api/bookmarks/{target_id}/toggle", headers=headers)
        self.assertEqual(toggle_res.status_code, 200)
        self.assertIn("is_bookmarked", toggle_res.json())

    def test_05_dashboard_stats(self):
        login_res = self.client.post("/api/auth/login", json={
            "email": "admin@devhub.com",
            "password": "password123"
        }).json()
        headers = {"Authorization": f"Bearer {login_res['access_token']}"}

        stats_res = self.client.get("/api/dashboard/stats", headers=headers)
        self.assertEqual(stats_res.status_code, 200)
        data = stats_res.json()
        self.assertIn("total_accessible_snippets", data)
        self.assertIn("language_breakdown", data)

if __name__ == "__main__":
    unittest.main()
