import unittest
import requests

BASE_URL = "http://localhost:8000"

class TestUserFollowing(unittest.TestCase):

    def setUp(self):
        """Register users before running tests."""
        self.users = [
            {"id": "1", "username": "jilly", "password": "123", "first_name": "jilly", "last_name": "song"},
            {"id": "2", "username": "brian", "password": "123", "first_name": "brian", "last_name": "qiu"},
            {"id": "3","username": "tk", "password": "123", "first_name": "tk", "last_name": "tk"},
        ]
        requests.delete(f"{BASE_URL}/reset")
        for user in self.users:
            response = requests.post(f"{BASE_URL}/register", json=user)
            self.assertIn(response.status_code, [200, 400])  # 400 if user already exists

    def test_register_login_follow(self):
        """Ensure users can log in successfully."""
        for user in self.users:
            login_data = {"username": user["username"], "password": user["password"]}
            response = requests.post(f"{BASE_URL}/login", json=login_data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json().get("success"))

        """Ensure users can follow each other."""
        follow_pairs = [
            ("1", "2"),
            ("3", "1"),
            ("3", "2"),
        ]
        
        for follower, following in follow_pairs:
            response = requests.post(f"{BASE_URL}/follow", json={"follower_id": follower, "following_id": following})
            self.assertEqual(response.status_code, 200)

        """Ensure followings are correctly recorded."""
        expected_followings = {
            "1": [2],
            "2": [],
            "3": [1, 2],
        }
        
        for user_id, expected in expected_followings.items():
            response = requests.get(f"{BASE_URL}/followings/{user_id}")

            self.assertEqual(response.status_code, 200)
            self.assertCountEqual(response.json().get("following", []), expected)

    @classmethod
    def tearDownClass(cls):
        """Clean up test data by clearing the tables."""
        requests.delete(f"{BASE_URL}/reset")

if __name__ == "__main__":
    unittest.main()