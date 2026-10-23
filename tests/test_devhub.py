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

    def test_01_health_check(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("version", data)

    def test_02_user_login_success(self):
        response = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "password123"
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertEqual(data["username"], "harsh_dev")

    def test_03_user_login_invalid_password(self):
        response = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 401)

    def test_04_user_registration_prevents_privilege_escalation(self):
        response = self.client.post("/api/auth/register", json={
            "username": "attacker",
            "email": "attacker@example.com",
            "password": "password123",
            "full_name": "Test Attacker",
            "role": "Admin"  # Attempting privilege escalation
        })
        self.assertEqual(response.status_code, 201)
        data = response.json()
        # Should be downgraded to Developer
        self.assertEqual(data["role"], "Developer")

    def test_05_unauthorized_access_rejected(self):
        response = self.client.get("/api/snippets")
        self.assertEqual(response.status_code, 401)

    def test_06_create_and_get_snippet(self):
        login_res = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "password123"
        }).json()
        headers = {"Authorization": f"Bearer {login_res['access_token']}"}

        # Create public snippet
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
        data = get_res.json()
        self.assertEqual(data["title"], "Unit Test Snippet for Python")
        self.assertEqual(data["language"], "python")

    def test_07_snippet_view_counter(self):
        login_res = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "password123"
        }).json()
        headers = {"Authorization": f"Bearer {login_res['access_token']}"}

        create_res = self.client.post("/api/snippets", json={
            "title": "View Count Test",
            "description": "Checking views increment",
            "code_content": "x = 42",
            "language": "python",
            "is_private": False
        }, headers=headers)
        snippet_id = create_res.json()["snippet_id"]

        res1 = self.client.get(f"/api/snippets/{snippet_id}", headers=headers).json()
        initial_views = res1["views_count"]

        res2 = self.client.get(f"/api/snippets/{snippet_id}", headers=headers).json()
        self.assertEqual(res2["views_count"], initial_views + 1)

    def test_08_private_snippet_access_control(self):
        dev_res = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "password123"
        }).json()
        dev_headers = {"Authorization": f"Bearer {dev_res['access_token']}"}

        member_res = self.client.post("/api/auth/login", json={
            "email": "member@devhub.com",
            "password": "password123"
        }).json()
        member_headers = {"Authorization": f"Bearer {member_res['access_token']}"}

        admin_res = self.client.post("/api/auth/login", json={
            "email": "admin@devhub.com",
            "password": "password123"
        }).json()
        admin_headers = {"Authorization": f"Bearer {admin_res['access_token']}"}

        # Dev creates a private snippet
        create_res = self.client.post("/api/snippets", json={
            "title": "Confidential Dev Snippet",
            "code_content": "SECRET_KEY = 'hidden'",
            "language": "python",
            "is_private": True
        }, headers=dev_headers)
        snippet_id = create_res.json()["snippet_id"]

        # Member attempts to view -> 403 Forbidden
        view_member = self.client.get(f"/api/snippets/{snippet_id}", headers=member_headers)
        self.assertEqual(view_member.status_code, 403)

        # Admin attempts to view -> 200 OK
        view_admin = self.client.get(f"/api/snippets/{snippet_id}", headers=admin_headers)
        self.assertEqual(view_admin.status_code, 200)

        # Author attempts to view -> 200 OK
        view_dev = self.client.get(f"/api/snippets/{snippet_id}", headers=dev_headers)
        self.assertEqual(view_dev.status_code, 200)

    def test_09_fork_snippet(self):
        dev_res = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "password123"
        }).json()
        dev_headers = {"Authorization": f"Bearer {dev_res['access_token']}"}

        member_res = self.client.post("/api/auth/login", json={
            "email": "member@devhub.com",
            "password": "password123"
        }).json()
        member_headers = {"Authorization": f"Bearer {member_res['access_token']}"}

        # Dev creates a public snippet
        create_res = self.client.post("/api/snippets", json={
            "title": "Forkable Utility Function",
            "code_content": "def add(a, b): return a + b",
            "language": "python",
            "is_private": False
        }, headers=dev_headers)
        original_id = create_res.json()["snippet_id"]

        # Member forks the snippet
        fork_res = self.client.post(f"/api/snippets/{original_id}/fork", headers=member_headers)
        self.assertEqual(fork_res.status_code, 201)
        forked_id = fork_res.json()["snippet_id"]

        # Check forked snippet has member as owner
        get_forked = self.client.get(f"/api/snippets/{forked_id}", headers=member_headers).json()
        self.assertIn("(Forked)", get_forked["title"])
        self.assertEqual(get_forked["author_username"], "alex_member")

    def test_10_raw_snippet_endpoint(self):
        dev_res = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "password123"
        }).json()
        headers = {"Authorization": f"Bearer {dev_res['access_token']}"}

        code_sample = "console.log('raw code test');"
        create_res = self.client.post("/api/snippets", json={
            "title": "Raw Code Test",
            "code_content": code_sample,
            "language": "javascript",
            "is_private": False
        }, headers=headers)
        snippet_id = create_res.json()["snippet_id"]

        raw_res = self.client.get(f"/api/snippets/{snippet_id}/raw", headers=headers)
        self.assertEqual(raw_res.status_code, 200)
        self.assertEqual(raw_res.text, code_sample)

    def test_11_update_and_delete_snippet(self):
        dev_res = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "password123"
        }).json()
        dev_headers = {"Authorization": f"Bearer {dev_res['access_token']}"}

        member_res = self.client.post("/api/auth/login", json={
            "email": "member@devhub.com",
            "password": "password123"
        }).json()
        member_headers = {"Authorization": f"Bearer {member_res['access_token']}"}

        # Dev creates snippet
        snippet_id = self.client.post("/api/snippets", json={
            "title": "Initial Title",
            "code_content": "code_v1",
            "language": "python"
        }, headers=dev_headers).json()["snippet_id"]

        # Member tries to edit -> 403
        edit_forbidden = self.client.put(f"/api/snippets/{snippet_id}", json={
            "title": "Hacked Title"
        }, headers=member_headers)
        self.assertEqual(edit_forbidden.status_code, 403)

        # Dev edits successfully
        edit_ok = self.client.put(f"/api/snippets/{snippet_id}", json={
            "title": "Updated Title",
            "code_content": "code_v2"
        }, headers=dev_headers)
        self.assertEqual(edit_ok.status_code, 200)

        # Dev deletes snippet
        del_res = self.client.delete(f"/api/snippets/{snippet_id}", headers=dev_headers)
        self.assertEqual(del_res.status_code, 200)

        # Snippet now 404
        get_deleted = self.client.get(f"/api/snippets/{snippet_id}", headers=dev_headers)
        self.assertEqual(get_deleted.status_code, 404)

    def test_12_toggle_bookmark_and_list(self):
        login_res = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "password123"
        }).json()
        headers = {"Authorization": f"Bearer {login_res['access_token']}"}

        snippets = self.client.get("/api/snippets", headers=headers).json()
        target_id = snippets[0]["id"]

        # Toggle ON
        toggle1 = self.client.post(f"/api/bookmarks/{target_id}/toggle", headers=headers).json()
        # Toggle OFF
        toggle2 = self.client.post(f"/api/bookmarks/{target_id}/toggle", headers=headers).json()
        self.assertNotEqual(toggle1["is_bookmarked"], toggle2["is_bookmarked"])

        # Fetch bookmarks
        bookmarks = self.client.get("/api/bookmarks", headers=headers)
        self.assertEqual(bookmarks.status_code, 200)
        self.assertIsInstance(bookmarks.json(), list)

    def test_13_search_and_filter(self):
        login_res = self.client.post("/api/auth/login", json={
            "email": "dev@devhub.com",
            "password": "password123"
        }).json()
        headers = {"Authorization": f"Bearer {login_res['access_token']}"}

        # Search by query
        search_res = self.client.get("/api/snippets?query=FastAPI", headers=headers)
        self.assertEqual(search_res.status_code, 200)

        # Filter by language
        lang_res = self.client.get("/api/snippets?language=python", headers=headers)
        self.assertEqual(lang_res.status_code, 200)
        for s in lang_res.json():
            self.assertEqual(s["language"].lower(), "python")

    def test_14_dashboard_stats(self):
        login_res = self.client.post("/api/auth/login", json={
            "email": "admin@devhub.com",
            "password": "password123"
        }).json()
        headers = {"Authorization": f"Bearer {login_res['access_token']}"}

        stats_res = self.client.get("/api/dashboard/stats", headers=headers)
        self.assertEqual(stats_res.status_code, 200)
        data = stats_res.json()
        self.assertIn("total_accessible_snippets", data)
        self.assertIn("my_snippets_count", data)
        self.assertIn("my_bookmarks_count", data)
        self.assertIn("total_snippet_views", data)
        self.assertIn("language_breakdown", data)

if __name__ == "__main__":
    unittest.main()
